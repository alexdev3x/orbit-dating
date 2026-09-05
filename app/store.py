from collections import defaultdict
from datetime import datetime, timezone

messages: dict[str, list[dict]] = defaultdict(list)
blocked: set[str] = set()
reports: list[dict] = []

agent = {
    "name": "Orbit Agent",
    "instructions": (
        "You are Orbit support and in-app assistant for an 18+ dating app. "
        "Be direct, short, and practical. Never help with minors, scams, "
        "or non-consensual behavior. If unsure, escalate to human support."
    ),
    "auto_reply_support": True,
}

tickets: list[dict] = []


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
