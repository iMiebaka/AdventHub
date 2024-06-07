from odmantic import Model, Field, Index, Reference, ObjectId
from datetime import datetime
from .user import User
from typing import List, Optional

class Exhortation(Model):
    slug: str
    media: str = Field(unique=True)
    media_type: str
    edited: bool = False
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: User = Reference()
    # DEPRECATE ⬇️
    # comments: int = 0
    # reaction: int = 0

    model_config = {
        "indexes": lambda: [
            Index(Exhortation.author, Exhortation.slug, name="post_index"),
        ]
    }



class ExhortationReaction(Model):
    exhortation: ObjectId
    user: ObjectId

    model_config = {
        "indexes": lambda: [
            Index(ExhortationReaction.exhortation, ExhortationReaction.user, name="exhortation_reaction_index"),
        ]
    }