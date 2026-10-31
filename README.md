# Dark Fantasy AI GM

A local dark-fantasy game master powered by LM Studio and Qwen.

This project is a lightweight starter for a text-first GM loop:
- create a session
- advance story with player input or choice
- ask the model for narration, options and world state
- keep the session state in memory for the next step

It is meant to be the foundation for a future RPG loop with:
- richer world state
- inventory and quests
- scene selection
- image generation layer
- interactive game UI

## Tech stack

- Python 3.11+
- Flask
- LM Studio OpenAI-compatible API
- Qwen2.5-7B-Instruct-GGUF (recommended)

## Local setup

1. Install LM Studio.
2. Download a model such as `Qwen2.5-7B-Instruct-GGUF`.
3. Enable Local Server in LM Studio.
4. Create a `.env` file from `.env.example` and adjust the model name if necessary.

```bash
cp .env.example .env
```

5. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

6. Start the API:

```bash
python app.py
```

7. Check health:

```bash
curl http://localhost:5000/api/health
```

8. Create a session:

```bash
curl -X POST http://localhost:5000/api/session/new \
  -H "Content-Type: application/json" \
  -d '{"player_name":"Ash","title":"The Ashen Dominion","location":"Blackglass Keep","trait":"merciless curiosity"}'
```

9. Advance the story:

```bash
curl -X POST http://localhost:5000/api/story/next \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"<session_id>",
    "player_input":"I step toward the chapel door and listen for the whispers beneath the stone.",
    "choice":"Open the cracked iron door"
  }'
```

## Notes

- The project is intentionally text-first.
- The current flow is a GM loop that uses an LM Studio-hosted local model.
- The next expansion path is: richer state, quests, asset references, optional image generation, and browser UI.

## Recommended next step

After the base GM loop is stable, the next iteration should add:
- narrative memory across sessions
- inventory/quest tracking
- scene templates and named NPCs
- image generator for key scenes
- optional web frontend for the game table
