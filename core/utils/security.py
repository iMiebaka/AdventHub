from datetime import datetime, timedelta
from typing import Optional, cast

from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
import jwt, hashlib
from odmantic import AIOEngine
from .exceptions import NotAuthenticatedException, CredentialsException
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from passlib.context import CryptContext

from core.models.user import User
from settings import SETTINGS, Engine


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenContent(BaseModel):
    public_id: str


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
        if not authorization or scheme.lower() != "bearer":
            return None
        return cast(str, param)


OAUTH2_SCHEME = OAuth2PasswordToken(tokenUrl="/account/oauth")


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


async def get_user_instance(
    engine: AIOEngine, username: Optional[str] = None, email: Optional[str] = None, public_id: Optional[str] = None
) -> Optional[User]:
    """Get a user instance from its username"""
    if username is not None:
        query = User.username == username
    elif email is not None:
        query = User.email == email
    elif public_id is not None:
        query = User.public_id == public_id
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
    token_content = TokenContent(public_id=user.public_id)
    expire = datetime.utcnow() + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": token_content.model_dump()}
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
        public_id = payload.get("sub")["public_id"]
        # token_content = TokenContent.model_dump_json(payload.get("sub"))
    except ValidationError:
        raise CredentialsException()
    
    user = await get_user_instance(Engine, public_id=public_id)
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
):
    from core.schema.user import UserSchema
    return UserSchema(token=token, **user_instance.model_dump())

# from Crypto.Cipher import AES
# import base64
# from settings import SETTINGS

# def mutulate_pass_key(pass_key: str) -> str:
#     cipher = AES.new(SETTINGS.SECRET_PASS_KEY.get_secret_value(), AES.MODE_CBC, "advent-hub")
#     return base64.b64encode(cipher.encrypt(pass_key))

# def init_passkey_history(pass_key:str) -> str:
#     return [mutulate_pass_key(pass_key=pass_key)]

# def update_passkey_history(pass_key:str, existing_keys: list[str]) -> list[str]:
#     new_key = mutulate_pass_key(pass_key=pass_key)
#     if new_key in existing_keys:
#         raise AssertionError("This password has been used before")
#     return existing_keys.pop(new_key)

def init_passkey_history(pass_key:str) -> str:
    return [hashlib.sha256(pass_key.encode()).hexdigest()]

def update_passkey_history(pass_key:str, existing_keys: list[str]) -> list[str]:
    new_key = hashlib.sha256(pass_key.encode()).hexdigest()
    if new_key in existing_keys:
        raise AssertionError("This password has been used before")
    return existing_keys.pop(new_key)