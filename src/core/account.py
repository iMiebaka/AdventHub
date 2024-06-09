from fastapi import Depends, UploadFile
from settings import Engine, ENV
from src.models.user import User
from src.models.profile import Profile
from src.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema, UpdateUserProfileSchema
from src.utils.security import  authenticate_user, create_access_token, get_current_user_instance, init_passkey_history
from src.utils.exceptions import *
import logging, random
from uuid import uuid4
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from src.models.exhortation import Exhortation

LOGGER = logging.getLogger(__name__)
engine = Engine


async def get_profile(
    username: str
):
    user = await engine.find_one(User, User.username == username)
    if user is None:
        raise HTTPException(404)
    payload =  user.model_dump()
    payload["exhortations"] = await engine.count(Exhortation, Exhortation.author == user.id)
    return payload


async def profile(
    user: User = Depends(get_current_user_instance)
):
    payload = user.model_dump()
    payload["exhortations"] = await engine.count(Exhortation, Exhortation.author == user.id)
    return payload


async def upload(
    files: list[UploadFile],
) -> list[str]:
    links = []
    for file in files:

        PATH = f"/media/{str(uuid4())}.png" if ENV != "testing" else f"/media/{str(uuid4())}-test.png"
        with open(f".{PATH}", "wb") as f:
            f.write(file.file.read())
            links.append(f"http://localhost:8000/account{PATH}")
    return links


async def update_profile(
    payload: UpdateUserProfileSchema,
    user: User = Depends(get_current_user_instance)
):
    user.model_update(payload)
    await engine.save(user)
    payload = user.model_dump()
    payload["exhortations"] = await engine.count(Exhortation, Exhortation.author == user.id)
    return payload


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
        pass_history=init_passkey_history(user.password)
    )
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
