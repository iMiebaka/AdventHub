from .base import Base
from odmantic import ObjectId
from datetime import datetime
from typing import List
from src.schema.exhortation import ExhortationSchema



class HighlightSchema(Base):
    exhortationId: ObjectId


class HighlighterSchema(Base):
    id: ObjectId
    exhortation: ExhortationSchema
    created_at: datetime 


class HighlighterListSchema(Base):
    totalPage: int
    page: int
    count: int
    data: List[HighlighterSchema]