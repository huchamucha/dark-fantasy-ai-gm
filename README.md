# Dark Fantasy AI GM

Dark fantasy AI GM prototype with a backend and frontend skeleton.

## Stack
- Backend: FastAPI + Python
- Frontend: React + TypeScript + Vite
- AI: OpenAI-compatible API
- Storage: PostgreSQL-ready models, with JSON state structure for MVP

## Project structure
- `backend/` — game API and AI service
- `frontend/` — browser UI
- `README.md` — project overview

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set environment variables:

```bash
export LLM_URL="http://localhost:11434/v1/chat/completions"
export LLM_MODEL="gpt-4o-mini"
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## MVP concept

- AI GM runs the campaign in dark fantasy tone
- world state is stored as structured JSON
- NPCs, quests, inventory, and locations are tracked
- player actions are sent to the AI service and resolved into world updates

## Current status

This repo is an MVP skeleton. The next steps are:
1. add real DB persistence
2. add campaign creation flow
3. add full quest/NPC state
4. add combat and inventory rules
5. add richer world-generation prompts
