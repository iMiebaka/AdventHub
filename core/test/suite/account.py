import pytest
from settings import Engine
from core.models.user import User
import logging
from ..payload import test_data

engine = Engine
LOGGER = logging.getLogger(__name__)



""" Accounting testing """
async def test_1_create_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list(0),
    )
    assert response.status_code == 200, response.text
    user_exist = await engine.find_one(User, User.email == test_data.user_list(0)["email"])
    assert user_exist.email == test_data.user_list(0)["email"]


async def test_1_create_users_others(async_app_client):
    users: list = test_data.user_list("")
    users.pop(0)
    for user in users:
        response = await async_app_client.post(
            "/account/sign-up",
            json=user,
        )
        assert response.status_code == 200, response.text
        user_exist = await engine.find_one(User, User.email == test_data.user_list(0)["email"])
        assert user_exist.email == test_data.user_list(0)["email"]


async def test_2_create_existing_user(async_app_client):
    response = await async_app_client.post(
        "/account/sign-up",
        json=test_data.user_list(0),
    )
    assert response.json() == {"detail":"Email already exist"}


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
