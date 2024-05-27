from fastapi import APIRouter, Body
from settings import Engine, ENV
from core.models.user import User
from core.models.profile import Profile
from core.schema.user import UserSchema, UserAuthResponeSchema, UserLoginSchema, UserProfileSchema
from core.utils.security import get_password_hash, authenticate_user, create_access_token
from core.utils.exceptions import *
from core.test.payload import Payload
import logging



LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def read_item():
    payload = Payload()
    user = payload.user_list[0]
    user_exist = await engine.find_one(User, User.email == user["email"])
    if user_exist is None:
        raise HTTPException(404)
    # user_exist = await engine.find_one(User, User.email == user["email"])
    LOGGER.info(user_exist)
    return {}

@router.post("/sign-up", response_model=UserProfileSchema)
async def sign_up(user: UserSchema):
    user_exist = await engine.find_one(User, User.email == user.email)
    if user_exist:
        raise HTTPException(400, detail="Email already exist")
    profile= Profile(profile_picture = f"https://ui-avatars.com/api/?name={user.first_name[0]+user.last_name}")
    user = User(**user.model_dump(), profile=profile)
    user.password = get_password_hash(user.password)
    await engine.save(user)
    return await engine.find_one(User, User.email == user.email)

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
    LOGGER.info(user.model_dump())
    return UserAuthResponeSchema(user=User(token=token))
