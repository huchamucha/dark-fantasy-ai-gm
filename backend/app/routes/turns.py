from __future__ import annotations

from app.schemas.turn import TurnRequest, TurnResponse
from app.services.game_service import GameService
from fastapi import APIRouter, HTTPException

router = APIRouter()
service = GameService()


@router.post("/campaigns/{campaign_id}/turns")
async def process_turn(campaign_id: str, turn: TurnRequest):
    try:
        return await service.process_turn(campaign_id, turn)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
