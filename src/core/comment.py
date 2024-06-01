from fastapi import Depends
from settings import Engine
from odmantic import ObjectId
from src.models.user import User
from src.models.exhortation import Exhortation
from src.models.comment import Comment
from src.schema.comment import CreateCommentSchema, UpdateCommentSchemaLogic, CommentListSchema, CommentSchemaLogic
from src.utils.security import get_current_user_instance
from src.utils.exceptions import *
import logging, math
from typing import Optional
from datetime import datetime

LOGGER = logging.getLogger(__name__)
engine = Engine


async def create_exhortation_comment(
    body: CreateCommentSchema,
    reply: Optional[ObjectId],
    user: User
):  
    try:
        exhortation = await engine.find_one(Exhortation, Exhortation.slug == body.slug)
        if exhortation is None:
            raise ExhortationNotFoundException()
        if reply:
            pass

        else:
            comment = Comment(**body.model_dump(), author=user, exhortation=exhortation)
            exhortation.comments.append(comment.id)
            await engine.save_all([comment, user])
            return comment
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


async def get(
    exhortationId: ObjectId,
    page: Optional[int],
    limit: Optional[int],
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


async def update(
    id: ObjectId,
    patch: UpdateCommentSchemaLogic,
    user: User = Depends(get_current_user_instance)
):
    result = await engine.find_one(Comment, Comment.id == id)
    if result is None:
            raise CommentNotFoundException()
    if result.author.id != user.id:
        raise CommentAuthorNotFoundException() 
    try:
        result.model_update(patch)
        result.edited = True
        result.edited_at = datetime.utcnow()
        await engine.save(result)
        return result
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


async def delete(
    id: ObjectId,
    user: User
):
    result = await engine.find_one(Comment, Comment.id == id)
    if result is None:
        raise CommentNotFoundException()
    if result.author.id != user.id:
        raise CommentAuthorNotFoundException() 
    try:
        exhortation:Exhortation = result.exhortation
        exhortation.comments.remove(result.id)
        await engine.delete(result)
        await engine.save(exhortation)
        return {"message": "Comment deleted"}
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))
