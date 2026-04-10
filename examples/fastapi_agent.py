"""
Example: FastAPI Agent Endpoint

Usage:
    pip install fastapi uvicorn
    ANTHROPIC_API_KEY=sk-xxx uvicorn examples.fastapi_agent:app
"""

import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from claude_runner import Runner

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    model: str = "sonnet"


@app.post("/chat")
async def chat(req: ChatRequest):
    runner = Runner(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model=req.model,
        max_turns=5,
    )

    result = await runner.run(req.message)
    return {
        "reply": result.text,
        "cost": result.cost,
        "turns": result.turns,
    }


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    runner = Runner(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model=req.model,
        max_turns=5,
    )

    async def generate():
        async for event in runner.stream(req.message):
            if event.type == "text":
                yield event.text

    return StreamingResponse(generate(), media_type="text/plain")
