from odmantic import Model, Field, Index, Reference
from datetime import datetime
from .user import User

class Exhortation(Model):
    slug: str
    media: str = Field(unique=True)
    media_type: str
    edited: bool = False
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: User = Reference()

    model_config = {
        "indexes": lambda: [
            Index(Exhortation.author, Exhortation.slug, name="post_index"),
        ]
    }
