from fastapi import APIRouter, Depends, UploadFile, File
from src.models.user import User
from src.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema,\
     UserProfileSchema, PrivateUserProfileSchema, UpdateUserProfileSchema,\
          SearchUserProfileSchema
from src.models.exhortation import Exhortation
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


@router.get("")
async def get_profile(
    username: str
):
    res = await account.get_profile(username=username)
    return SearchUserProfileSchema(**res)



@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
    _: User = Depends(get_current_user_instance)
):
    return await account.upload(files=files)



@router.get("/profile")
async def profile(
    current_user: User = Depends(get_current_user_instance)
):
    res = await account.profile(user=current_user)
    return PrivateUserProfileSchema(**res)


@router.put("/profile")
async def update_profile(
    payload: UpdateUserProfileSchema,
    current_user: User = Depends(get_current_user_instance)
):
    res = await account.update_profile(payload=payload, user=current_user)
    return PrivateUserProfileSchema(**res) 


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
