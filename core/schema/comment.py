from .base import Base
from typing_extensions import List
from .user import UserDisplayProfileSchema


class CommentSchema(Base):
    profile: UserDisplayProfileSchema
    body: str
    reaction: List[str]


class CreateCommentSchema(Base):
    body: str
    slug: str
