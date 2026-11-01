
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import (
    FastAPI,
    HTTPException,
    Path,
    Request,
)
from pydantic import BaseModel, Field


# Limit concurrent invoice workflow executions
workflow_semaphore = asyncio.Semaphore(5)


class InvoiceRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000
    )


class InvoiceResponse(BaseModel):
    invoice_id: int
    question: str
    context: dict
    answer: str
    elapsed_seconds: float


async def fetch_vendor(invoice_id: int):
    await asyncio.sleep(2)

    return {
        "vendor_id": 22,
        "name": "Aira AI"
    }


async def fetch_payment_history(invoice_id: int):
    await asyncio.sleep(3)

    return {
        "invoice_id": invoice_id,
        "past_due_count": 2
    }


async def fetch_payment_policy(invoice_id: int):
    await asyncio.sleep(1)

    return {
        "payment_terms": "Net 30",
        "approval_required": True
    }


async def generate_answer(question: str, context: dict):
    # Mock LLM call
    await asyncio.sleep(1)

    return (
        f"Question: {question}. "
        f"Vendor: {context['vendor']['name']}. "
        f"Payment terms: "
        f"{context['policy']['payment_terms']}."
    )


app = FastAPI(
    title="Finance AI Async API"
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post(
    "/invoices/{invoice_id}/analyze",
    response_model=InvoiceResponse
)
async def analyze_invoice(
    invoice_id: Annotated[int, Path(gt=0)],
    payload: InvoiceRequest
):
    start = time.perf_counter()

    try:
        async with asyncio.timeout(8):
            async with workflow_semaphore:

                # Independent upstream calls
                vendor, history, policy = await asyncio.gather(
                    fetch_vendor(invoice_id),
                    fetch_payment_history(invoice_id),
                    fetch_payment_policy(invoice_id)
                )

                context = {
                    "vendor": vendor,
                    "history": history,
                    "policy": policy
                }

                # Depends on retrieved context
                answer = await generate_answer(
                    payload.question,
                    context
                )

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Invoice analysis timed out"
        )

    elapsed = time.perf_counter() - start

    return InvoiceResponse(
        invoice_id=invoice_id,
        question=payload.question,
        context=context,
        answer=answer,
        elapsed_seconds=round(elapsed, 3)
    )
