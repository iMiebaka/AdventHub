from .base import Base
from typing_extensions import List
from .user import UserDisplayProfileSchema
from datetime import datetime
from odmantic import ObjectId


class CommentSchemaLogic(Base):
    id: ObjectId
    body: str
    edited: bool
    author: UserDisplayProfileSchema
    reaction: List[str]
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