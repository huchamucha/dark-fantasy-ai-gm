
from fastapi import APIRouter, HTTPException

from pydantic import ValidationError

from app.actions.interpreter import interpret_action
from app.schemas.action import ActionInterpretationRequest


router = APIRouter()


@router.post("/actions/interpret")
async def interpret_player_action(
    request: ActionInterpretationRequest,
):
    try:
        result = await interpret_action(
            player_action=request.player_action,
            world_context=request.world_context,
        )

        return result.model_dump(mode="json")

    except (ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка интерпретации AI: {exc}",
        )
