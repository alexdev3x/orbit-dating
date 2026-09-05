# Orbit

Location-grid dating MVP. Inspired by the *shape* of apps like Grindr or DBNA — not a clone of their brand, data, or servers.

**18+ only.** No minors in seed data, no age fields under 18, no underage imagery.

## What this is

- Nearby grid (distance mocked from a home point)
- Profile view (bio, tags, photo placeholder)
- 1:1 chat stub (in-memory)
- Block / report stubs
- Age gate on first visit

## What this is not

- Not production dating infrastructure
- No real GPS tracking, no push, no payments, no photo pipeline
- No copying of Grindr/DBNA assets, layouts-as-trademark, or user data

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

Open http://127.0.0.1:8090

Or: `docker compose up --build`

## API

```
GET  /api/me
GET  /api/nearby
GET  /api/profiles/{id}
POST /api/messages
GET  /api/messages/{user_id}
POST /api/block/{id}
POST /api/report/{id}
```

## Next

1. Real auth (session / magic link)
2. Postgres + PostGIS or coarse geohash (not raw lat/lng in logs)
3. Photo upload with moderation queue
4. WebSocket chat
5. Native shell later — product first, store listing last
