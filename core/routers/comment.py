from fastapi import APIRouter, Depends, Body
from settings import Engine
from odmantic import ObjectId
from core.models.user import User
from core.models.exhortation import Exhortation
from core.models.comment import Comment
from core.schema.comment import CreateCommentSchema, CommentSchema, CommentListSchema, CommentSchemaLogic
from core.utils.security import get_current_user_instance
from core.utils.exceptions import *
import logging, math
from typing import Optional
from datetime import datetime

LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/comment",
    tags=["Comment"],
    responses={404: {"details": "Not found"}},
)


@router.post("/exhortation", status_code=201)
async def create_exhortation_comment(
    body: CreateCommentSchema,
    reply: Optional[ObjectId] = None,
    current_user: User = Depends(get_current_user_instance)
):  
    try:
        exhortation = await engine.find_one(Exhortation, Exhortation.slug == body.slug)
        if exhortation is None:
            raise HTTPException(404, detail="We could not find this Exhortation")
        if reply:
            pass

        else:
            comment = Comment(**body.model_dump(), author=current_user, exhortation=exhortation)
            exhortation.comments.append(comment.id)
            await engine.save_all([comment, current_user])
            return CommentSchema(body=comment.body, author=current_user.model_dump())
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


@router.get("/exhortation")
async def get(
    exhortationId: ObjectId,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
):  
    skip = (page - 1) * limit
    query=Comment.exhortation == exhortationId
    exhortation = await engine.find(Comment, query, skip=skip, limit=limit*1)
    count = await engine.count(model=Comment)
    total_page = math.ceil(count/limit) if count >= limit else 1
    data = [CommentSchemaLogic(**e.model_dump()) for e in exhortation]
    return CommentListSchema(page=page, data=data, total_page=total_page, count=count)
    