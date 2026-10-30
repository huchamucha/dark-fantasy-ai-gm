from app.services.game_service import GameService
from fastapi import APIRouter, HTTPException
from app.schemas.turn import TurnRequest

router = APIRouter()
service = GameService()


@router.post("/campaigns/{campaign_id}/turns")
async def process_turn(campaign_id: str, turn: TurnRequest):
    try:
        return await service.process_turn(campaign_id, turn)
    except Exception as exc:  # pragma: no cover - simple demo path
        raise HTTPException(status_code=500, detail=str(exc))
