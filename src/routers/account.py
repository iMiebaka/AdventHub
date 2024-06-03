from fastapi import APIRouter, Depends, Request
from settings import Engine, ENV
from src.models.user import User
from src.models.profile import Profile
from src.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema, UserProfileSchema, PrivateUserProfileSchema, UpdateUserProfileSchema, SearchUserProfileSchema
from src.utils.security import  get_current_user_instance
from src.utils.exceptions import *
from src.core import account
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"details": "Not found"}},
)


@router.get("", response_model=SearchUserProfileSchema)
async def get_profile(
    username: str
):
    return await account.get_profile(username=username)



@router.get("/profile", response_model=PrivateUserProfileSchema)
async def profile(
    current_user: User = Depends(get_current_user_instance)
):
    return await account.profile(user=current_user)


@router.put("/profile", response_model=PrivateUserProfileSchema)
async def update_profile(
    payload: UpdateUserProfileSchema,
    current_user: User = Depends(get_current_user_instance)
):
    return await account.update_profile(payload=payload, user=current_user)


@router.post("/sign-up", response_model=UserProfileSchema)
async def sign_up(user: UserSchema):
    return await account.sign_up(user=user)


@router.post("/login", response_model=UserAuthResponeSchema)
async def login_user(
    user_input: UserLoginSchema,
):
    return await account.login_user(user_input)


@router.post("/oauth", response_model=UserAuthResponeSchema)
async def login_user_oauth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return await account.login_user_oauth(form_data=form_data)
