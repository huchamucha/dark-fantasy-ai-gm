from fastapi import APIRouter

from app.story_packs.registry import list_story_packs

router = APIRouter()


@router.get("/story-packs")
async def get_story_packs():
    return list_story_packs()
