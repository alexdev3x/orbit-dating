from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.data import ME, PROFILES
from app import store

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Orbit", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class MessageIn(BaseModel):
    to: str
    text: str = Field(min_length=1, max_length=1000)


class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=200)


def _public(p: dict) -> dict:
    return {k: v for k, v in p.items()}


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/me")
def me():
    return ME


@app.get("/api/nearby")
def nearby():
    rows = [p for p in PROFILES if p["id"] not in store.blocked]
    rows = sorted(rows, key=lambda p: p["distance_km"])
    return {"results": [_public(p) for p in rows]}


@app.get("/api/profiles/{pid}")
def profile(pid: str):
    if pid in store.blocked:
        raise HTTPException(404, "Not found")
    for p in PROFILES:
        if p["id"] == pid:
            return _public(p)
    raise HTTPException(404, "Not found")


@app.get("/api/messages/{pid}")
def thread(pid: str):
    return {"messages": store.messages[pid]}


@app.post("/api/messages")
def send(msg: MessageIn):
    if msg.to in store.blocked:
        raise HTTPException(403, "Blocked")
    if not any(p["id"] == msg.to for p in PROFILES):
        raise HTTPException(404, "Unknown user")
    row = {"from": "me", "to": msg.to, "text": msg.text}
    store.messages[msg.to].append(row)
    return {"ok": True, "message": row}


@app.post("/api/block/{pid}")
def block(pid: str):
    store.blocked.add(pid)
    return {"ok": True, "blocked": sorted(store.blocked)}


@app.post("/api/report/{pid}")
def report(pid: str, body: ReportIn):
    store.reports.append({"id": pid, "reason": body.reason})
    store.blocked.add(pid)
    return {"ok": True}
