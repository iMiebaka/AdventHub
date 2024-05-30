import pytest
from settings import Engine
from core.models.user import User
from httpx import AsyncClient, ASGITransport
from core.app import app
import logging, asyncio, base64
from fastapi.testclient import TestClient
from .payload import test_data
from .suite import exhortation, comment, account

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
    await account.test_1_create_user(async_app_client)

@pytest.mark.asyncio
async def test_1_create_users_others(async_app_client):
    await account.test_1_create_users_others(async_app_client)

@pytest.mark.asyncio
async def test_2_create_existing_user(async_app_client):
    await account.test_2_create_existing_user(async_app_client)

@pytest.mark.asyncio
async def test_4_login_user(async_app_client):
    await account.test_4_login_user(async_app_client)

@pytest.mark.asyncio
async def test_5_user_profile(async_app_client):
    await account.test_5_user_profile(async_app_client)



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
