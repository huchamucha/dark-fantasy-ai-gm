from fastapi import APIRouter, HTTPException

from app.schemas.campaign import CampaignCreate
from app.schemas.character import CharacterCreate
from app.services.game_service import GameService

router = APIRouter()
service = GameService()


@router.post("/campaigns")
async def create_campaign(payload: CampaignCreate):
    try:
        return service.create_campaign(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/campaigns/{campaign_id}/characters")
async def create_character(campaign_id: str, payload: CharacterCreate):
    try:
        return service.create_character(campaign_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/campaigns/{campaign_id}/world")
async def get_world(campaign_id: str):
    try:
        return service.get_world(campaign_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
