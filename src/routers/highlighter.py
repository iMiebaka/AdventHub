from fastapi import APIRouter, Depends
from settings import Engine
from src.models.user import User
from src.schema.highlighter import HighlightSchema
from src.utils.security import get_current_user_instance
from src.core import highlighter
from src.utils.exceptions import *
import logging
from typing import Optional
from odmantic import ObjectId

LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/highlights",
    tags=["highlighter", "highlights"],
    responses={404: {"details": "Not found"}},
)



@router.post("")
async def create(
    highlight:HighlightSchema,
    current_user: User = Depends(get_current_user_instance)
):
    return await highlighter.create_destory_highlight(highlighter=highlight, user=current_user)


@router.get("")
async def get(
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_user_instance)

):  
    return await highlighter.get(page=page, limit=limit, user=current_user)
