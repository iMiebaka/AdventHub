from fastapi import APIRouter, Depends
from odmantic import ObjectId
from settings import Engine
import logging
from src.models.user import User
from src.utils.security import get_current_user_instance
from src.core.reaction import exhortation_reaction, comment_reaction


LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/reaction",
    tags=["reaction"],
    responses={404: {"details": "Not found"}},
)


@router.get("/exhortation")
async def get(
    id: ObjectId,
    current_user: User = Depends(get_current_user_instance)

):  
    return await exhortation_reaction(id=id, user=current_user)


@router.get("/comment")
async def get(
    id: ObjectId,
    current_user: User = Depends(get_current_user_instance)

):  
    return await comment_reaction(id=id, user=current_user)
