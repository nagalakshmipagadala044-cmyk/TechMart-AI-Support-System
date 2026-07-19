import os
import sys
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(__file__))
from agents.router import AgentRouter

app = FastAPI(title="TechMart Customer Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = AgentRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    agents_used: list[str]
    reasoning: str
    predicted_category: str
    responses: dict


@app.get("/")
def health_check():
    return {"status": "TechMart Support API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    result = router.handle_message(session_id, request.message)

    return ChatResponse(
        session_id=session_id,
        agents_used=result["agents_used"],
        reasoning=result["reasoning"],
        predicted_category=result["predicted_category"],
        responses=result["responses"]
    )


@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {"history": router.memory.get_full_log(session_id)}

@app.get("/admin/all-messages")
def get_all_messages():
    """View all stored conversations - useful for demos and debugging"""
    import sqlite3
    conn = sqlite3.connect("database/conversations.db")
    cursor = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()

    return {
        "total_shown": len(rows),
        "messages": [
            {
                "id": r[0],
                "session_id": r[1],
                "role": r[2],
                "content": r[3],
                "agent": r[4],
                "timestamp": r[5]
            }
            for r in rows
        ]
    }