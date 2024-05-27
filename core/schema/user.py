from .base import Base
from pydantic import EmailStr, SecretStr

class UserProfileSchema(Base):
    first_name: str
    last_name: str
    email: str
    
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
