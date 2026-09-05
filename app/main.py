from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import store
from app.agent import generate
from app.data import ME, PROFILES

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Orbit", version="0.2.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class MessageIn(BaseModel):
    to: str
    text: str = Field(min_length=1, max_length=1000)


class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=200)


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    instructions: str | None = Field(default=None, min_length=10, max_length=4000)
    auto_reply_support: bool | None = None


class AgentChatIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list)


class TicketIn(BaseModel):
    subject: str = Field(min_length=3, max_length=80)
    text: str = Field(min_length=1, max_length=2000)


class TicketMessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    as_support: bool = False


def _public(p: dict) -> dict:
    return {k: v for k, v in p.items()}


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/support")
def support_page():
    return FileResponse(ROOT / "static" / "support.html")


@app.get("/agent")
def agent_page():
    return FileResponse(ROOT / "static" / "agent.html")


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
    store.reports.append({"id": pid, "reason": body.reason, "at": store.now()})
    store.blocked.add(pid)
    return {"ok": True}


@app.get("/api/agent")
def agent_get():
    return store.agent


@app.put("/api/agent")
def agent_put(body: AgentUpdate):
    if body.name:
        store.agent["name"] = body.name.strip()
    if body.instructions:
        store.agent["instructions"] = body.instructions.strip()
    if body.auto_reply_support is not None:
        store.agent["auto_reply_support"] = body.auto_reply_support
    return store.agent


@app.post("/api/agent/chat")
async def agent_chat(body: AgentChatIn):
    result = await generate(body.text, body.history)
    return {
        "agent": store.agent["name"],
        "provider": result["provider"],
        "text": result["text"],
    }


@app.get("/api/support/tickets")
def list_tickets():
    return {"tickets": store.tickets}


@app.post("/api/support/tickets")
async def create_ticket(body: TicketIn):
    ticket = {
        "id": f"t{len(store.tickets) + 1:03d}",
        "subject": body.subject.strip(),
        "status": "open",
        "created_at": store.now(),
        "messages": [
            {"role": "user", "text": body.text.strip(), "at": store.now()},
        ],
    }
    if store.agent["auto_reply_support"]:
        reply = await generate(body.text, ticket["messages"])
        ticket["messages"].append(
            {
                "role": "agent",
                "name": store.agent["name"],
                "text": reply["text"],
                "at": store.now(),
            }
        )
    store.tickets.insert(0, ticket)
    return ticket


@app.post("/api/support/tickets/{tid}/messages")
async def ticket_message(tid: str, body: TicketMessageIn):
    ticket = next((t for t in store.tickets if t["id"] == tid), None)
    if not ticket:
        raise HTTPException(404, "Unknown ticket")
    role = "support" if body.as_support else "user"
    ticket["messages"].append({"role": role, "text": body.text.strip(), "at": store.now()})
    if (not body.as_support) and store.agent["auto_reply_support"]:
        reply = await generate(body.text, ticket["messages"])
        ticket["messages"].append(
            {
                "role": "agent",
                "name": store.agent["name"],
                "text": reply["text"],
                "at": store.now(),
            }
        )
    return ticket
