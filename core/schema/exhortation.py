from .base import Base
from odmantic import ObjectId
from pydantic import model_validator
import random, random, string
from typing_extensions import Self, Optional, List
from .user import UserDisplayProfileSchema
from datetime import datetime


def generate_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))



class CreateExhortationSchema(Base):
    media: str
    media_type: str
    slug: Optional[str] = None

    @model_validator(mode="after")
    def generate_slug(self) -> Self:
        self.slug = generate_alphanumeric(10)
        return self


class ExhortationSchema(Base):
    slug: str
    media: str
    media_type: str
    author: UserDisplayProfileSchema
    edited_at: datetime 
    created_at: datetime 

class ExhortationListSchema(Base):
    total_page: int
    page: int
    data: List[ExhortationSchema]


class UpdateExhortationSchema(Base):
    media: str = None
