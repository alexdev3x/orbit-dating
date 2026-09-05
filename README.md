# Orbit

Location-grid dating MVP plus an in-app **AI agent** (custom instructions) and a **support ticket chat**.

**18+ only.**

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

- App: http://127.0.0.1:8090
- Support: http://127.0.0.1:8090/support
- Agent instructions: http://127.0.0.1:8090/agent

## Agent

Default engine is local (rule + instructions prefix). Optional OpenAI-compatible backend:

```bash
export ORBIT_LLM_URL=https://api.openai.com
export ORBIT_LLM_KEY=sk-...
export ORBIT_LLM_MODEL=gpt-4o-mini
```

`PUT /api/agent` saves name, custom instructions, and whether support tickets auto-reply.

## Support

`POST /api/support/tickets` opens a ticket. If auto-reply is on, the agent answers first. Replies can be marked `as_support: true` for a human agent.
