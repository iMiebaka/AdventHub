from settings import Engine
from odmantic import ObjectId
from src.models.exhortation import Exhortation
from src.models.comment import Comment
from src.models.user import User
from src.utils.exceptions import *

engine = Engine

async def exhortation_reaction(id: ObjectId, user:User):
    exhortation = await engine.find_one(Exhortation, Exhortation.id == id)
    if exhortation is None:
        raise ExhortationNotFoundException()
    if user.id in  exhortation.reaction:
        exhortation.reaction.remove(user.id)
        await engine.save(exhortation)
        return {"count": len(exhortation.reaction), "reacted": False}
    else:
        exhortation.reaction.append(user.id)
        await engine.save(exhortation)
        return {"count": len(exhortation.reaction), "reacted": True}


async def comment_reaction(id: ObjectId, user:User):
    comment = await engine.find_one(Comment, Comment.id == id)
    if comment is None:
        raise CommentNotFoundException()
    if user.id in  comment.reaction:
        comment.reaction.remove(user.id)
        await engine.save(comment)
        return {"count": len(comment.reaction), "reacted": False}
    else:
        comment.reaction.append(user.id)
        await engine.save(comment)
        return {"count": len(comment.reaction), "reacted": True}