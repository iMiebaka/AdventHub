from datetime import datetime, timedelta
from typing import Optional, cast

from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
import jwt
from odmantic import AIOEngine
from .exceptions import NotAuthenticatedException, CredentialsException
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from passlib.context import CryptContext

from core.models.user import User
from core.schema.user import UserSchema
from settings import SETTINGS, Engine


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenContent(BaseModel):
    username: str


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth2PasswordToken(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=False)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "token":
            return None
        return cast(str, param)


OAUTH2_SCHEME = OAuth2PasswordToken(tokenUrl="/users")


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


async def get_user_instance(
    engine: AIOEngine, username: Optional[str] = None, email: Optional[str] = None
) -> Optional[User]:
    """Get a user instance from its username"""
    if username is not None:
        query = User.username == username
    elif email is not None:
        query = User.email == email
    else:
        return None
    user = await engine.find_one(User, query)
    return user


async def authenticate_user(
    engine: AIOEngine, email: str, password: str
) -> Optional[User]:
    """Verify the User/Password pair against the DB content"""
    user = await get_user_instance(engine, email=email)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User) -> str:
    token_content = TokenContent(username=user.username)
    expire = datetime.utcnow() + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": token_content.json()}
    encoded_jwt = jwt.encode(
        to_encode, SETTINGS.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.ALGORITHM
    )
    return str(encoded_jwt)


async def get_current_user_instance(
    token: Optional[str] = Depends(OAUTH2_SCHEME),
) -> User:
    """Decode the JWT and return the associated User"""
    if token is None:
        raise NotAuthenticatedException()
    try:
        payload = jwt.decode(
            token,
            SETTINGS.SECRET_KEY.get_secret_value(),
            algorithms=[SETTINGS.ALGORITHM],
        )
        
    except Exception:
        raise CredentialsException()

    try:
        token_content = TokenContent.parse_raw(payload.get("sub"))
    except ValidationError:
        raise CredentialsException()

    user = await get_user_instance(Engine, username=token_content.username)
    if user is None:
        raise CredentialsException()
    return user


async def get_current_user_optional_instance(
    token: str = Depends(OAUTH2_SCHEME),
) -> Optional[User]:
    try:
        user = await get_current_user_instance(token)
        return user
    except HTTPException:
        return None


async def get_current_user(
    user_instance: User = Depends(get_current_user_instance),
    token: str = Depends(OAUTH2_SCHEME),
) -> UserSchema:
    return UserSchema(token=token, **user_instance.dict())
