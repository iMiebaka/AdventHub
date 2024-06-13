from fastapi import APIRouter, Depends
from src.models.user import User
from src.utils.security import  get_current_user_instance
from src.schema.request import FollowUserSchema
from src.utils.exceptions import *
from src.core import request
from typing import Optional

router = APIRouter(
    prefix="/request",
    tags=["request"],
    responses={404: {"details": "Not found"}},
)


@router.post("/followers")
async def followers(
    payload: FollowUserSchema,
    current_user: User = Depends(get_current_user_instance)

):

    return await request.follow_user(payload=payload, current_user=current_user)


@router.get("/followers")
async def get_followers(
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_user_instance)

):
    return await request.followers(limit=limit, page=page, current_user=current_user)


@router.get("/following")
async def following(
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_user_instance)

):
    return await request.following(limit=limit, page=page, current_user=current_user)
