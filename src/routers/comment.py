from fastapi import APIRouter, Depends
from settings import Engine
from odmantic import ObjectId
from src.models.user import User
from src.schema.comment import CreateCommentSchema, UpdateCommentSchemaLogic, CommentSchemaLogic
from src.utils.security import get_current_user_instance, get_current_user_optional_instance
from src.core import comment
from typing import Optional

engine = Engine
router = APIRouter(
    prefix="/comment",
    tags=["Comment"],
    responses={404: {"details": "Not found"}},
)


@router.post("/exhortation", status_code=201, response_model=CommentSchemaLogic)
async def create_exhortation_comment(
    body: CreateCommentSchema,
    reply: Optional[ObjectId] = None,
    current_user: User = Depends(get_current_user_instance)
):  
    return await comment.create_exhortation_comment(body=body, reply=reply, user=current_user)


@router.get("/exhortation")
async def get(
    exhortationId: ObjectId,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    user: User = Depends(get_current_user_optional_instance)
):  
    return await comment.get(exhortationId=exhortationId, page=page, limit=limit, user=user)


@router.put("/exhortation", response_model=CommentSchemaLogic)
async def update(
    id: ObjectId,
    patch: UpdateCommentSchemaLogic,
    current_user: User = Depends(get_current_user_instance)
):
    return await comment.update(id=id, patch=patch, user=current_user)


@router.delete("/exhortation", status_code=204)
async def delete(
    id: ObjectId,
    current_user: User = Depends(get_current_user_instance)
):
    return await comment.delete(id=id, user=current_user)
