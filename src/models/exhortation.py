from odmantic import Model, Field, Index, Reference, ObjectId
from datetime import datetime
from .user import User
from typing import List

class Exhortation(Model):
    slug: str
    media: str = Field(unique=True)
    media_type: str
    edited: bool = False
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: User = Reference()
    comments: List[ObjectId] = []
    reaction: List[ObjectId] = []

    model_config = {
        "indexes": lambda: [
            Index(Exhortation.author, Exhortation.slug, name="post_index"),
        ]
    }
