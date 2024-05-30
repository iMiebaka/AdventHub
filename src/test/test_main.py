# import pytest
# from . import test_2_exhortation, test_3_comment
# from settings import Engine
# from core.models.user import User
# from httpx import AsyncClient, ASGITransport
# from core.app import app
# import logging, asyncio, base64
# from fastapi.testclient import TestClient
# from .payload import test_data
# from . import test_1_account

# client = TestClient(app)
# engine = Engine
# LOGGER = logging.getLogger(__name__)



# @pytest.fixture(scope="session")
# async def async_app_client():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url='http://test') as client:
#         yield client



# """ Accounting testing """
# @pytest.mark.asyncio(scope="session")
# async def test_1_create_user(async_app_client):
#     await test_1_account.test_1_create_user(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_1_create_users_others(async_app_client):
#     await test_1_account.test_1_create_users_others(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_2_create_existing_user(async_app_client):
#     await test_1_account.test_2_create_existing_user(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_4_login_user(async_app_client):
#     await test_1_account.test_4_login_user(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_5_user_profile(async_app_client):
#     await test_1_account.test_5_user_profile(async_app_client)



# """ Exhortation """
# @pytest.mark.asyncio(scope="session")
# async def test_1_create_exhortation(async_app_client):
#     await test_2_exhortation.test_1_create_exhortation(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_2_read_exhortation(async_app_client):
#     await test_2_exhortation.test_2_read_exhortation(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_3_update_exhortation(async_app_client):
#     await test_2_exhortation.test_3_update_exhortation(async_app_client)

# @pytest.mark.asyncio(scope="session")
# async def test_4_delete_exhortation(async_app_client):
#     await test_2_exhortation.test_1_create_exhortation(async_app_client)
#     await test_2_exhortation.test_1_create_exhortation(async_app_client)
#     await test_2_exhortation.test_4_delete_exhortation(async_app_client)


# """ Exhortation comment """
# @pytest.mark.asyncio(scope="session")
# async def test_1_make_comment(async_app_client):
#     await test_3_comment.test_1_make_comment(async_app_client)
