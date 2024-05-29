from fastapi import APIRouter, Depends, Request
from settings import Engine, ENV
from core.models.user import User
from core.models.profile import Profile
from core.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema, UserProfileSchema
from core.utils.security import  authenticate_user, create_access_token, get_current_user
from core.utils.exceptions import *
import logging
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"details": "Not found"}},
)


@router.get("/profile", response_model=UserProfileSchema)
async def profile(
    current_user: User = Depends(get_current_user)
):
    user = await engine.find_one(User, User.email == current_user.email)
    if user is None:
        raise HTTPException(404)
    return user

@router.post("/sign-up", response_model=UserProfileSchema)
async def sign_up(user: UserSchema):
    user_exist = await engine.find_one(User, User.email == user.email)
    if user_exist:
        raise HTTPException(400, detail="Email already exist")
    profile= Profile(profile_picture = f"https://ui-avatars.com/api/?name={user.first_name[0]+user.last_name}")
    user = User(**user.model_dump(), profile=profile)
    await engine.save(user)
    return user


@router.post("/login", response_model=UserAuthResponeSchema)
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

@router.post("/oauth", response_model=UserAuthResponeSchema)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(
        Engine, form_data.username, form_data.password
    )
    if user is None:
        raise InvalidCredentialsException()

    token = create_access_token(user)
    return UserAuthResponeSchema(access_token=token, token_type="bearer")
