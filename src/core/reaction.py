from settings import Engine
from odmantic import ObjectId
from src.models.comment import CommentReaction
from src.models.exhortation import ExhortationReaction
from src.models.user import User
from src.utils.exceptions import *
import logging

engine = Engine
LOGGER = logging.getLogger(__name__)


async def comment_reaction(id: ObjectId, user:User):
    query = (CommentReaction.comment == id) & (CommentReaction.user == user.id)
    reaction = await engine.find_one(CommentReaction, query)
    total_comment = await engine.count(CommentReaction, CommentReaction.comment == id)
    if reaction is None:
        reaction = CommentReaction(comment=id, user=user.id)
        await engine.save(reaction)
        return {"count": total_comment + 1, "reacted": True}
    else:
        await engine.delete(reaction)
        return {"count": total_comment - 1, "reacted": False}


async def exhortation_reaction(id: ObjectId, user:User):
    query = (ExhortationReaction.exhortation == id) & (ExhortationReaction.user == user.id)
    reaction = await engine.find_one(ExhortationReaction, query)
    total_comment = await engine.count(ExhortationReaction, ExhortationReaction.exhortation == id)
    if reaction is None:
        reaction = ExhortationReaction(exhortation=id, user=user.id)
        await engine.save(reaction)
        return {"count": total_comment + 1, "reacted": True}
    else:
        await engine.delete(reaction)
        return {"count": total_comment - 1, "reacted": False}