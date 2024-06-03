from .base import Base
from pydantic import EmailStr, SecretStr
from odmantic import ObjectId
from typing import Optional
from pydantic import model_validator
from src.utils.security import get_password_hash
from typing_extensions import Self, List

class ProfileSchema(Base):
    postion: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    cover_picture: Optional[str] = None
    about_me: Optional[str] = None
    
class PrivateUserProfileSchema(Base):
    id: ObjectId
    first_name: str
    last_name: str
    email: str
    exhortation: List[ObjectId] # Done to control circular import
    profile: ProfileSchema
    username: str

class UpdateUserProfileSchema(Base):
    first_name: str
    last_name: str
    email: str
    profile: ProfileSchema
    username: str


class UserProfileSchema(Base):
    id: ObjectId
    first_name: str
    last_name: str
    email: str
    username: str
    profile: ProfileSchema


class SearchUserProfileSchema(Base):
    first_name: str
    last_name: str
    username: str
    profile: ProfileSchema
    exhortation: List[ObjectId]

class ProfileDisplaySchema(Base):
    postion: Optional[str] = None
    profile_picture: Optional[str] = None


class UserDisplayProfileSchema(Base):
    id: ObjectId
    first_name: str
    last_name: str
    profile: ProfileDisplaySchema


class UserSchema(Base):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @model_validator(mode="after")
    def hash_password(self) -> Self:
        self.password = get_password_hash(self.password)
        return self


class UserAuthResponeSchema(Base):
    access_token: str
    token_type: str


class UserLoginSchema(Base):
    email: str
    password: SecretStr
