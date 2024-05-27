from odmantic import Model, Field, ObjectId, Reference
from datetime import datetime

class Messages(Model):
    # id: ObjectId = Field(default_factory=ObjectId)
    slug: str
    media: str
    media_type: str
    edited_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: ObjectId

