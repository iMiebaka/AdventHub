from fastapi import APIRouter, Depends, Request
from settings import Engine, ENV
from src.models.user import User
from src.models.profile import Profile
from src.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema, UserProfileSchema, PrivateUserProfileSchema
from src.utils.security import  authenticate_user, create_access_token, get_current_user_instance, init_passkey_history
from src.utils.exceptions import *
import logging, random
from uuid import uuid4
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

LOGGER = logging.getLogger(__name__)
engine = Engine


async def profile(
    user: User = Depends(get_current_user_instance)
):
    user = await engine.find_one(User, User.email == user.email)
    if user is None:
        raise HTTPException(404)
    return user


async def generate_username(first_name: str, last_name: str) -> str:
    user_name = ""
    user_name = f"{first_name.lower()}.{last_name.lower()}"
    username_exist = await engine.find_one(User, User.username == user_name)
    if username_exist:
        return f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"
    return user_name


async def sign_up(user: UserSchema):
    user_exist = await engine.find_one(User, User.email == user.email)
    if user_exist:
        raise HTTPException(400, detail="Email already exist")
    profile= Profile(
        profile_picture = f"https://ui-avatars.com/api/?name={user.first_name[0]+user.last_name}",
        pass_history=init_passkey_history(user.password))
    username = await generate_username(first_name=user.first_name, last_name=user.last_name)
    user = User(**user.model_dump(), profile=profile, public_id=uuid4().hex, username=username)
    await engine.save(user)
    return user


async def login_user(
    user_input: UserLoginSchema,
):
    user = await authenticate_user(
        Engine, user_input.email, user_input.password.get_secret_value()
    )
    if user is None:
        raise InvalidCredentialsException()

    token = create_access_token(user)
    return UserAuthResponeSchema(access_token=token, token_type="bearer")


async def login_user_oauth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(
        Engine, form_data.username, form_data.password
    )
    if user is None:
        raise InvalidCredentialsException()

    token = create_access_token(user)
    return UserAuthResponeSchema(access_token=token, token_type="bearer")
