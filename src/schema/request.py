from odmantic import ObjectId
from typing_extensions import List
from datetime import datetime
from .base import Base
from .user import UserDisplayProfileSchema


class FollowerFollowingSchema(Base):
    id: ObjectId
    user: UserDisplayProfileSchema
    friend: UserDisplayProfileSchema
    created_at: datetime 


class FollowUserSchema(Base):
    username: str


class FollowerFollowingListSchema(Base):
    total_page: int
    page: int
    count: int
    data: List[FollowerFollowingSchema]

