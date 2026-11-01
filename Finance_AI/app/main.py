from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Finance AI")


class AgentRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/agent")
async def run_agent(payload: AgentRequest):
    return {
        "answer": f"Processed: {payload.question}"
    }