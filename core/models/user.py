from odmantic import Model, Field, Index, Reference, ObjectId
from uuid import uuid4
from datetime import datetime
from .profile import Profile
from typing import List


class User(Model):
    first_name: str
    last_name: str
    email: str = Field(unique=True)
    password: str
    public_id: str = uuid4().hex
    created_at: datetime = Field(default_factory=datetime.utcnow)
    profile: Profile = Reference()
    messages: List[ObjectId] = []

    model_config = {
        "indexes": lambda: [
            Index(User.first_name, User.last_name, name="name_index"),
        ]
    }
    
