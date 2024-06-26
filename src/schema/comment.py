from .base import Base
from typing_extensions import List
from .user import UserDisplayProfileSchema
from datetime import datetime
from odmantic import ObjectId
from typing import Optional

class CommentSchemaLogic(Base):
    id: ObjectId
    body: str
    edited: bool
    liked: Optional[bool] = False
    author: UserDisplayProfileSchema
    reaction: Optional[int] = 0
    edited_at: datetime
    created_at: datetime

class UpdateCommentSchemaLogic(Base):
    body: str

class CreateCommentSchema(Base):
    body: str
    slug: str

class CommentListSchema(Base):
    totalPage: int
    page: int
    count: int
    data: List[CommentSchemaLogic]