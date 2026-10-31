from fastapi import APIRouter, HTTPException

from app.engine.attribute_catalog import get_attribute_catalog
from app.story_packs.registry import get_story_pack

router = APIRouter()


@router.get("/rules/attributes")
async def get_attributes(story_pack_id: str = "dark_fantasy"):
    try:
        pack = get_story_pack(story_pack_id)

        overrides = pack["presentation"].get(
            "attribute_overrides",
            {},
        )

        return get_attribute_catalog(overrides)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
