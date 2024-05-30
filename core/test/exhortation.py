import logging
from .payload import test_data
from httpx import AsyncClient


LOGGER = logging.getLogger(__name__)


async def test_1_create_exhortation(async_app_client: AsyncClient):
    user = test_data.user_list(0)
    response = await async_app_client.post(
            "/account/login",
            json=user,
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json()["access_token"]


    post = test_data.exhortation_list["textBase"][0]
    response = await async_app_client.post(
        "/exhortation",
        json=post,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 200
    res_data = response.json()    

    assert res_data["media"] == post["media"]
    assert res_data["media_type"] == post["media_type"]
    assert res_data["author"]["first_name"] == user["first_name"]
    assert res_data["author"]["last_name"] == user["last_name"]


async def test_2_read_exhortation(async_app_client: AsyncClient):
# Getting all post ✅
    response = await async_app_client.get(
        "/exhortation",
    )
    slug = response.json()["data"][0]["slug"]

# Getting single post ✅
    response = await async_app_client.get(
        f"/exhortation?slug={slug}",
    )
    assert response.json()["slug"] == slug

# Getting single post ❌
    response = await async_app_client.get(
        f"/exhortation?slug={slug}849",
    )
    assert response.status_code == 404


async def test_3_update_exhortation(async_app_client: AsyncClient):
    user = test_data.user_list(0)
    response = await async_app_client.post(
            "/account/login",
            json=user,
        )
    access_token = response.json()["access_token"]

    response = await async_app_client.get(
        "/exhortation",
    )
    post = response.json()["data"][0]

    slug = post["slug"]
    new_title = "lorem updated"
    post["media"] = new_title
    
    # Update post ✅
    response = await async_app_client.put(
        f"/exhortation?slug={slug}",
        json=post,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 200
    res_data = response.json()  
    assert res_data["media"] == new_title
    
    # Update post with attempt to change slug and media type ❌
    new_title = "lorem updated 2"
    post["media"] = new_title
    post["slug"] = "changeSlug"
    post["media_type"] = "VIDEO"
    response = await async_app_client.put(
        f"/exhortation?slug={slug}",
        json=post,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 200
    res_data = response.json() 
    assert res_data["media"] == new_title
    assert res_data["slug"] != post["slug"]
    assert res_data["media_type"] != post["media_type"]
    assert res_data["slug"] == slug
    assert res_data["media_type"] == "TEXT"
    


async def test_4_delete_exhortation(async_app_client: AsyncClient):
    user = test_data.user_list(0)
    response = await async_app_client.post(
            "/account/login",
            json=user,
        )
    access_token = response.json()["access_token"]

    response = await async_app_client.get(
        "/exhortation",
    )
    post = response.json()["data"]
    assert len(post) == 3
    slug= post[2]["slug"]

    # Attempting unauthorized access ❌
    response = await async_app_client.delete(
        f"/exhortation?slug={slug}",
    )
    assert response.status_code == 401

    # Attempting with wrong slug ❌
    response = await async_app_client.delete(
        f"/exhortation?slug={slug}+sdjg",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 404
    
    # Attempt with correct data ✅
    response = await async_app_client.delete(
        f"/exhortation?slug={slug}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 204