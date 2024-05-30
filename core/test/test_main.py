import pytest
from settings import Engine
from core.models.user import User
from httpx import AsyncClient, ASGITransport
from core.app import app
import logging, asyncio, base64
from fastapi.testclient import TestClient
from .payload import test_data
from .suite import exhortation, comment 

client = TestClient(app)
engine = Engine
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



""" Accounting testing """
@pytest.mark.asyncio
async def test_1_create_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list(0),
    )
    assert response.status_code == 200, response.text
    user_exist = await engine.find_one(User, User.email == test_data.user_list(0)["email"])
    assert user_exist.email == test_data.user_list(0)["email"]


@pytest.mark.asyncio
async def test_2_create_existing_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list(0),
    )
    assert response.json() == {"detail":"Email already exist"}


@pytest.mark.asyncio
async def test_4_login_user(async_app_client):
    user = test_data.user_list(0)
    user["password"] = "12346"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400
    
    user = test_data.user_list(0)
    user["email"] = "wrongemail@adventhub.com"
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 400

    user = test_data.user_list(0)
    response = await async_app_client.post(
        "/account/login",
        json=user,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_5_user_profile(async_app_client):
    user = test_data.user_list(0)
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





""" Exhortation """

@pytest.mark.asyncio
async def test_1_create_exhortation(async_app_client):
    await exhortation.test_1_create_exhortation(async_app_client)

@pytest.mark.asyncio
async def test_2_read_exhortation(async_app_client):
    await exhortation.test_2_read_exhortation(async_app_client)

@pytest.mark.asyncio
async def test_3_update_exhortation(async_app_client):
    await exhortation.test_3_update_exhortation(async_app_client)

@pytest.mark.asyncio
async def test_4_delete_exhortation(async_app_client):
    await exhortation.test_1_create_exhortation(async_app_client)
    await exhortation.test_1_create_exhortation(async_app_client)
    await exhortation.test_4_delete_exhortation(async_app_client)



""" Exhortation comment """
@pytest.mark.asyncio
async def test_1_make_comment(async_app_client):
    await comment.test_1_make_comment(async_app_client)
