from __future__ import annotations

import os
import re
from typing import Any

import httpx

from app import store

LLM_URL = os.getenv("ORBIT_LLM_URL", "").rstrip("/")
LLM_KEY = os.getenv("ORBIT_LLM_KEY", "")
LLM_MODEL = os.getenv("ORBIT_LLM_MODEL", "gpt-4o-mini")

HARD_RULES = (
    "Hard rules: users must be 18+. Refuse anything involving minors, "
    "extortion, stalking, or non-consent. Do not ask for payment details. "
    "Support answers: account, block/report, distance grid, messages."
)


def _local_reply(user_text: str, instructions: str) -> str:
    t = user_text.lower()
    if re.search(r"\b(underage|minor|kid|teen)\b", t):
        return "Orbit is 18+ only. That request is blocked. If you saw a underage profile, use Report."
    if "block" in t:
        return "Open a profile → Block. Blocked people disappear from Nearby and cannot message you."
    if "report" in t:
        return "Open a profile → Report and write why. We also auto-block on report in this MVP."
    if any(k in t for k in ("distance", "nearby", "grid", "location")):
        return "Nearby is a coarse distance grid from your city, not live GPS. Production should store geohash, not raw coordinates."
    if any(k in t for k in ("delete", "account", "dsgvo", "gdpr")):
        return "Account deletion is not wired yet. In production this must be a real DSGVO path (export + erase)."
    if "photo" in t or "bild" in t:
        return "Photos are placeholders in the MVP. Real uploads need moderation before they go public."
    prefix = instructions.strip().split(".")[0]
    return f"{prefix}. I can help with Nearby, profiles, messages, block/report. What exactly broke?"


async def generate(user_text: str, history: list[dict] | None = None) -> dict[str, Any]:
    instructions = store.agent["instructions"]
    if not LLM_URL:
        return {
            "provider": "local",
            "text": _local_reply(user_text, instructions),
        }

    messages = [
        {"role": "system", "content": f"{instructions}\n\n{HARD_RULES}"},
    ]
    for item in (history or [])[-8:]:
        messages.append({"role": item.get("role", "user"), "content": item.get("text", "")})
    messages.append({"role": "user", "content": user_text})

    headers = {"Content-Type": "application/json"}
    if LLM_KEY:
        headers["Authorization"] = f"Bearer {LLM_KEY}"
    payload = {"model": LLM_MODEL, "messages": messages, "temperature": 0.3}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(f"{LLM_URL}/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
        text = data["choices"][0]["message"]["content"]
        return {"provider": "llm", "text": text.strip()}
    except Exception:
        return {
            "provider": "local-fallback",
            "text": _local_reply(user_text, instructions),
        }
