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
    last_ping: datetime.datetime | None = None  # NEW: when was last health check
    status: str | None = None  # NEW: "healthy"/"error"/"unknown"
    quality: str | None = None      # "pass" / "fail"

def init_db():
    """Initialize database with updated schema"""
    db = sqlite_utils.Database(DB_PATH)
    if "agents" not in db.table_names():
        db["agents"].create({
            "name": str,
            "image": str,
            "registered_at": str,
            "last_ping": str,  # NEW
            "status": str,     # NEW
            "quality": str,    # NEW: pass/fail
        }, pk="name")
    else:
        # Add new columns if they don't exist (for existing databases)
        try:
            db["agents"].add_column("last_ping", str)
        except Exception:
            pass  # Column already exists
        try:
            db["agents"].add_column("status", str)
        except Exception:
            pass  # Column already exists
        try:
            db["agents"].add_column("quality", str)
        except Exception:
            pass  # Column already exists

@app.post("/agents", status_code=201)
def add_agent(agent: Agent):
    init_db()
    db = sqlite_utils.Database(DB_PATH)
    
    agent.registered_at = datetime.datetime.utcnow()
    agent.status = "unknown"  # NEW: default status for new agents
    
    record = agent.model_dump()
    record["registered_at"] = record["registered_at"].isoformat()
    if record["last_ping"]:
        record["last_ping"] = record["last_ping"].isoformat()
    
    db["agents"].insert(record, pk="name", replace=True)
    return {"ok": True}

@app.get("/agents")
def list_agents():
    init_db()
    db = sqlite_utils.Database(DB_PATH)
    return list(db["agents"].rows)

@app.patch("/agents/{name}")  # NEW: endpoint for health updates
def update_agent(name: str, patch: dict):
    """Update agent status and last_ping"""
    init_db()
    db = sqlite_utils.Database(DB_PATH)
    
    # Convert datetime string to proper format if needed
    if "last_ping" in patch and isinstance(patch["last_ping"], str):
        # patch["last_ping"] is already in ISO format from the pinger
        pass
    
    try:
        db["agents"].update(name, patch)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/")
def root():
    init_db()
    db = sqlite_utils.Database(DB_PATH)
    agent_count = db["agents"].count if "agents" in db.table_names() else 0
    return {"message": "Emergence Directory API", "agents": agent_count}