from .base import Base
from typing_extensions import List
from .user import UserDisplayProfileSchema
from datetime import datetime

class CommentSchema(Base):
    body: str
    reaction: List[str] = []
    edited: bool = False


class CommentSchemaLogic(Base):
    body: str
    edited: bool
    author: UserDisplayProfileSchema
    reaction: List[str]
    edited_at: datetime
    created_at: datetime

class CreateCommentSchema(Base):
    body: str
    slug: str

class CommentListSchema(Base):
    total_page: int
    page: int
    count: int
    data: List[CommentSchemaLogic]