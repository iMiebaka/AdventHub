from .base import Base
from pydantic import EmailStr, SecretStr
from odmantic import ObjectId
from typing import Optional

class ProfileSchema(Base):
    postion: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    cover_picture: Optional[str] = None
    about_me: Optional[str] = None
    
class UserProfileSchema(Base):
    id: ObjectId
    first_name: str
    last_name: str
    email: str
    profile: ProfileSchema


class UserSchema(Base):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserAuthResponeSchema(Base):
    token: str

class UserLoginSchema(Base):
    email: str
    password: SecretStr
