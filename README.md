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
- `.gitignore` — local env and cache exclusions

## Local development

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Optional environment variables:

```bash
export LLM_URL="http://localhost:11434/v1/chat/completions"
export LLM_MODEL="gpt-4o-mini"
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open:
- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/api/health

## MVP concept

- AI GM runs the campaign in dark fantasy tone
- world state is stored as structured JSON
- NPCs, quests, inventory, and locations are tracked
- player actions are sent to the AI service and resolved into world updates

## Current status

This repo is an MVP skeleton. The next stages are:
1. add real DB persistence
2. add campaign creation flow
3. add full quest/NPC state
4. add combat and inventory rules
5. add richer world-generation prompts

## Recommended next milestone

Focus on a single playable loop:
- create a character
- enter the city
- get the first quest
- follow the quest through the monastery and catacombs
- resolve the first major decision with AI GM narration
