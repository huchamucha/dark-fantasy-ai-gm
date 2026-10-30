from fastapi import FastAPI
from app.routes.campaigns import router as campaigns_router
from app.routes.turns import router as turns_router

app = FastAPI(title="Dark Fantasy AI GM")

app.include_router(campaigns_router, prefix="/api")
app.include_router(turns_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "game": "Пепельная Корона"}
