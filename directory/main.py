from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite_utils, datetime, os

DB_PATH = os.getenv("EMERGENCE_DB", "directory.db")

app = FastAPI(title="Emergence Directory")

# ✅ Add CORS middleware for frontend access (Dev only — lock down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev; tighten for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

class Agent(BaseModel):
    name: str
    image: str
    registered_at: datetime.datetime | None = None

@app.post("/agents", status_code=201)
def add_agent(agent: Agent):
    db = sqlite_utils.Database(DB_PATH)
    if "agents" not in db.table_names():
        db["agents"].create({
            "name": str,
            "image": str,
            "registered_at": str,
        }, pk="name")

    agent.registered_at = datetime.datetime.utcnow()
    record = agent.model_dump()
    record["registered_at"] = record["registered_at"].isoformat()
    db["agents"].insert(record, pk="name", replace=True)
    return {"ok": True}

@app.get("/agents")
def list_agents():
    db = sqlite_utils.Database(DB_PATH)
    return list(db["agents"].rows)
