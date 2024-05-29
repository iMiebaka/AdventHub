import pytest, httpx
from settings import Engine
from core.models.user import User
from httpx import AsyncClient
from core.app import app
import logging, asyncio, base64
from fastapi.testclient import TestClient
from .payload import test_data


client = TestClient(app)
engine = Engine
LOGGER = logging.getLogger(__name__)

def get_basic_auth_header(username: str, password: str) -> str:
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_app_client():
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client

@pytest.mark.asyncio
async def test_1_create_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list[0],
    )
    assert response.status_code == 200, response.text
    user_exist = await engine.find_one(User, User.email == test_data.user_list[0]["email"])
    assert user_exist.email == test_data.user_list[0]["email"]


@pytest.mark.asyncio
async def test_2_create_existing_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list[0],
    )
    assert response.json() == {"detail":"Email already exist"}


@pytest.mark.asyncio
async def test_4_login_user(async_app_client):
    user = test_data.user_list[0]
    user["password"] = "12346"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400
    
    user = test_data.user_list[0]
    user["email"] = "wrongemail@adventhub.com"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400

    user = test_data.user_list[0]
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_5_user_profile(async_app_client):
    user = test_data.user_list[0]
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