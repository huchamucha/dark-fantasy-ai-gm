from fastapi import FastAPI

from app.routes.campaigns import router as campaigns_router
from app.routes.turns import router as turns_router
from app.routes.story_packs import router as story_packs_router
from app.routes.game_rules import router as game_rules_router

app = FastAPI(title="Universal AI RPG")


app.include_router(campaigns_router, prefix="/api")
app.include_router(turns_router, prefix="/api")
app.include_router(story_packs_router, prefix="/api")
app.include_router(game_rules_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "game": "Universal AI RPG",
    }
