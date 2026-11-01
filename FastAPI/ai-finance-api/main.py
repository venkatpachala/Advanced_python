# # Our application will:
# - Validate the incoming question.
# - Run document retrieval and customer lookup concurrently.
# - Build a grounded prompt.
# - Call an LLM.
# - Enforce request deadlines and concurrency limits.
# - Return an answer, source citations, and a request ID.
# - Report expected failures without exposing sensitive internals.


import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance_api")


# ---------- Request and response schemas ----------

class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class Citation(BaseModel):
    document_id: str
    title: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    request_id: str


# ---------- Simulated external clients ----------

class RetrievalService:
    async def search(self, query: str) -> list[dict]:
        await asyncio.sleep(0.2)

        return [
            {
                "document_id": "policy-1",
                "title": "Refund Policy",
                "content": "Eligible refunds are processed within 7 days."
            }
        ]


class CustomerService:
    async def get_customer(self, user_id: str) -> dict:
        await asyncio.sleep(0.15)

        return {
            "user_id": user_id,
            "account_status": "active"
        }


class LLMService:
    async def generate(self, query: str, context: str) -> str:
        await asyncio.sleep(0.5)

        # Demo only. A real implementation would use a model.
        return f"Based on the policy: {context}"


# ---------- Application lifecycle ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retrieval = RetrievalService()
    app.state.customers = CustomerService()
    app.state.llm = LLMService()

    # One semaphore shared by requests in this process.
    app.state.llm_limit = asyncio.Semaphore(5)

    yield

    # Close real client connections here during shutdown.


app = FastAPI(
    title="AI Finance Assistant",
    lifespan=lifespan
)


# ---------- Dependencies ----------

def get_services(request: Request):
    return request.app.state


# ---------- Request timing middleware ----------

@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid4())
    request.state.request_id = request_id

    try:
        response = await call_next(request)
    finally:
        duration = time.perf_counter() - start
        logger.info(
            "path=%s duration_ms=%.2f",
            request.url.path,
            duration * 1000
        )

    response.headers["X-Request-ID"] = request_id
    return response


# ---------- Health endpoint ----------

@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------- AI endpoint ----------

@app.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    request: Request,
    services: Annotated[object, Depends(get_services)]
):
    request_id = request.state.request_id

    try:
        # Overall request execution deadline.
        async with asyncio.timeout(8.0):

            # Both operations are independent.
            documents, customer = await asyncio.gather(
                services.retrieval.search(payload.query),
                services.customers.get_customer(payload.user_id)
            )

            if customer["account_status"] != "active":
                raise HTTPException(
                    status_code=403,
                    detail="Account not permitted"
                )

            if not documents:
                return AskResponse(
                    answer="I couldn't find relevant information.",
                    citations=[],
                    request_id=request_id
                )

            context = "\n".join(
                f"[{doc['document_id']}] {doc['content']}"
                for doc in documents
            )

            # Limit simultaneous model calls.
            async with services.llm_limit:
                answer = await services.llm.generate(
                    payload.query,
                    context
                )

            return AskResponse(
                answer=answer,
                citations=[
                    Citation(
                        document_id=doc["document_id"],
                        title=doc["title"]
                    )
                    for doc in documents
                ],
                request_id=request_id
            )

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI request timed out"
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "AI request failed request_id=%s",
            request_id
        )
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable"
        )
