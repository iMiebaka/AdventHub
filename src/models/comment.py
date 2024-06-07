from odmantic import Model, Field, Reference, ObjectId
from datetime import datetime
from .exhortation import Exhortation
from .user import User
from typing import List


class Comment(Model):
    body: str
    edited: bool = False
    exhortation: Exhortation = Reference()
    author: User = Reference()
    # reaction: int = 0 #DEPRECATE
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommentReaction(Model):
    comment: ObjectId
    user: ObjectId
