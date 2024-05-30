import logging, pytest
from .payload import test_data as TEST_DATA
from httpx import AsyncClient, ASGITransport
from core.app import app


LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.mark.asyncio(scope="session")
async def test_1_create_exhortation(async_app_client: AsyncClient):
    user = TEST_DATA.user_list(0)
    access_token = TEST_DATA.read_token(0)


    post = TEST_DATA.exhortation_list["textBase"][0]
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


@pytest.mark.asyncio(scope="session")
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


@pytest.mark.asyncio(scope="session")
async def test_3_update_exhortation(async_app_client: AsyncClient):

    access_tokens:list = TEST_DATA.read_token("")
    access_token = access_tokens[0] 
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
    
    access_tokens.pop(0)
    for iter, access_token in enumerate(access_tokens):
        if iter == 4:
            break
        response = await async_app_client.put(
            f"/exhortation?slug={slug}",
            json=post,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        assert response.status_code == 401

    response = await async_app_client.put(
        f"/exhortation?slug=jsdSJDSSDh",
        json=post,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio(scope="session")
async def test_4_delete_exhortation(async_app_client: AsyncClient):
    access_token = TEST_DATA.read_token(0)

    # Create post
    for index in range(2):
        post  = TEST_DATA.exhortation_list["textBase"][index + 1]
        response = await async_app_client.post(
            "/exhortation",
            json=post,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        assert response.status_code == 200
    
    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    exhortation_length = len(res_data["exhortation"])
    response = await async_app_client.get(
        "/exhortation",
    )
    post = response.json()["data"]
    assert len(post) == exhortation_length
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

    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    assert len(res_data["exhortation"]) == exhortation_length -1