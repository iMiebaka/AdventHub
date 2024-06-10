from odmantic import ObjectId
from typing_extensions import  Optional, List
from datetime import datetime
from .base import Base
from .user import UserDisplayProfileSchema



class ExhortationMedia(Base):
    media: str
    media_type: str


# class CreateExhortationSchema(Base):
#     body: str


class ExhortationSchema(Base):
    id: ObjectId
    body: str
    slug: str
    media: List[ExhortationMedia] = []
    liked: Optional[bool] = False
    author: UserDisplayProfileSchema
    edited_at: datetime 
    created_at: datetime 
    comments: Optional[int] = 0
    reaction: Optional[int] = 0

class ExhortationListSchema(Base):
    total_page: int
    page: int
    count: int
    data: List[ExhortationSchema]


class UpdateExhortationSchema(Base):
    body: str = None
    # media: str = None
