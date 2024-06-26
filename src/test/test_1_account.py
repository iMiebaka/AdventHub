import pytest
from settings import Engine
from src.models.user import User
import logging
from .payload import test_data as TEST_DATA
from src.app import app
from httpx import AsyncClient, ASGITransport
from src.utils.security import create_access_token, get_current_user_instance
from src.models.user import User
from settings import Engine
from odmantic import query
from src.core.account import sign_up
from src.schema.user import UserSchema


engine = Engine
LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


""" Accounting testing """
@pytest.mark.asyncio(scope="session")
async def test_1A_create_user(async_app_client: AsyncClient):
    response = await async_app_client.post(
        "/account/sign-up",
        json=TEST_DATA.user_list(0),
    )
    assert response.status_code == 200, response.text
    user_exist = await engine.find_one(User, User.email == TEST_DATA.user_list(0)["email"])
    assert user_exist.email == TEST_DATA.user_list(0)["email"]


@pytest.mark.asyncio(scope="session")
async def test_1B_create_users_others():
    users: list = TEST_DATA.user_list("")
    users.pop(0)
    for iter, user in enumerate(users):
        await sign_up(user=UserSchema(**user))
        user_exist = await engine.find_one(User, User.email == TEST_DATA.user_list(iter)["email"])
        assert user_exist.email == TEST_DATA.user_list(iter)["email"]


@pytest.mark.asyncio(scope="session")
async def test_2_create_existing_user(async_app_client: AsyncClient):
    response = await async_app_client.post(
        "/account/sign-up",
        json=TEST_DATA.user_list(0),
    )
    assert response.json() == {"detail":"Email already exist"}



@pytest.mark.asyncio(scope="session")
async def test_3A_create_token():
    # Generate tokens ✅
    access_tokens = []
    users = await engine.find(User)
    for user in users:
        token = create_access_token(user=user)
        access_tokens.append(token)
    TEST_DATA.write_token(token=access_tokens)

    assert type(TEST_DATA.read_token(0)) == str
    assert type(TEST_DATA.read_token("")) == list


@pytest.mark.asyncio(scope="session")
async def test_3B_test_token():
    # Run checks for generated tokens 🔑
    access_tokens = TEST_DATA.read_token("")
    users = await engine.find(User)
    assert len(users) == len(access_tokens)

    for iter, user in enumerate(users):
        access_token = access_tokens[iter]
        user_init = await get_current_user_instance(access_token)
        assert user.id == user_init.id
        

@pytest.mark.asyncio(scope="session")
async def test_4_login_user(async_app_client: AsyncClient):
    user = TEST_DATA.user_list(0)
    user["password"] = "12346"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400
    
    user = TEST_DATA.user_list(0)
    user["email"] = "wrongemail@adventhub.com"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400

    user = TEST_DATA.user_list(0)
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio(scope="session")
async def test_5_user_profile(async_app_client: AsyncClient):
    user = TEST_DATA.user_list(0)
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    assert res_data["email"] == user["email"]
    assert res_data["first_name"] == user["first_name"]
    assert res_data["last_name"] == user["last_name"]

    user = await engine.find_one(User)
    username = user.username
    response = await async_app_client.get(
        f"/account?username={username}",
    )
    res_data = response.json()
    assert res_data["first_name"] == user.first_name
    assert res_data["last_name"] == user.last_name
    assert res_data["username"] == user.username

    response = await async_app_client.get(
        f"/account?username={username}321",
    )
    assert response.status_code == 404

    user = await engine.find_one(User, sort=query.desc(User.created_at))
    response = await async_app_client.get(
        f"/account?username={username}",
    )
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_6_update_profile(async_app_client: AsyncClient):
    access_token:str = TEST_DATA.read_token(0)

    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    res_data["profile"]["cover_picture"] = "https://www.thespruce.com/thmb/zXQvC3RGBgZOFmnfsjlnSVl81eo=/5616x3744/filters:no_upscale():max_bytes(150000):strip_icc()/old-white-church-157610088-6f1735caa5054ff79fa44217005706fb.jpg"
    assert response.status_code == 200
   
    response = await async_app_client.put(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json=res_data
    )
    res_data = response.json()
    assert res_data["profile"]["cover_picture"] != None

    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    assert res_data["profile"]["cover_picture"] != None