from fastapi import APIRouter, Depends, Body
from settings import Engine
from odmantic import ObjectId
from core.models.user import User
from core.models.exhortation import Exhortation
from core.models.comment import Comment
from core.schema.comment import CreateCommentSchema, UpdateCommentSchemaLogic, CommentListSchema, CommentSchemaLogic
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


@router.post("/exhortation", status_code=201, response_model=CommentSchemaLogic)
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
            return comment
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
    comments = await engine.find(Comment, query, skip=skip, limit=limit)
    count = await engine.count(Comment, query)
    total_page = math.ceil(count/limit) if count >= limit else 1
    data = [CommentSchemaLogic(**e.model_dump()) for e in comments]
    if len(data) == 0:
        return CommentListSchema(page=1, data=data, totalPage=0, count=0)

    return CommentListSchema(page=page, data=data, totalPage=total_page, count=count)


@router.put("/exhortation", response_model=CommentSchemaLogic)
async def update(
    id: ObjectId,
    patch: UpdateCommentSchemaLogic,
    current_user: User = Depends(get_current_user_instance)
):
    result = await engine.find_one(Comment, Comment.id == id)
    if result is None:
            raise HTTPException(404, detail="We could not find this comment")
    if result.author.id != current_user.id:
        raise HTTPException(401, detail="We could not find this comment")
    try:
        result.model_update(patch)
        result.edited = True
        result.edited_at = datetime.utcnow()
        await engine.save(result)
        return result
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))

