from settings import Engine
from src.models.user import User
from src.models.exhortation import Highlighter, Exhortation
from src.schema.highlighter import HighlighterSchema, HighlighterListSchema, HighlightSchema
from src.utils.exceptions import *
import logging, math
from typing import Optional, List


LOGGER = logging.getLogger(__name__)
engine = Engine


async def create_destory_highlight(highlighter: HighlightSchema, user:User) -> bool:
    id = highlighter.exhortationId
    query = (Highlighter.exhortation == id) & (Highlighter.user == user.id)
    highlight = await engine.find_one(Highlighter, query)
    if highlight is None:

        exhortation = await engine.find_one(Exhortation, Exhortation.id == id)
        highlight = Highlighter(exhortation=exhortation, user=user.id)
        await engine.save(highlight)
        return True
    else:
        await engine.delete(highlight)
        return False


async def get(
    page: Optional[int],
    limit: Optional[int],
    user: User
):  

    query = Highlighter.user == user.id
    count = await engine.count(Highlighter, query)
    skip = (page - 1) * limit
    payload = await engine.find(Highlighter, query, skip=skip, limit=limit)
    data = [HighlighterSchema(**p.model_dump()) for p in payload]
    total_page = math.ceil(count/limit) if count >= limit else 1
    if len(data) == 0:
        return HighlighterListSchema(page=1, data=data, totalPage=0, count=0)

    return HighlighterListSchema(page=page, data=data, totalPage=total_page, count=count)