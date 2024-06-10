from odmantic import Model, Field, Index, Reference, ObjectId, EmbeddedModel
from datetime import datetime
from .user import User
from typing import List




class ExhortationMedia(EmbeddedModel):
    media: str
    media_type: str


class Exhortation(Model):
    slug: str
    body: str
    edited: bool = False
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: User = Reference()
    media: List[ExhortationMedia] = []

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


class Highlighter(Model):
    user: ObjectId
    exhortation: Exhortation = Reference()
    created_at: datetime = Field(default_factory=datetime.utcnow)
