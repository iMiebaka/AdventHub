import logging, pytest
from .payload import test_data
from httpx import AsyncClient, ASGITransport
from core.app import app


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest.mark.asyncio(scope="session")
async def test_1_make_comment(async_app_client: AsyncClient):
# Get post to comment ✅
    response = await async_app_client.get(
        "/exhortation",
    )
    slug = response.json()["data"][0]["slug"]
    comment = test_data.comment_list(0)

# Post a comment ❌
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
        )
    assert response.status_code == 401

    user = test_data.user_list(0)
    response = await async_app_client.post(
            "/account/login",
            json=user,
        )
    assert response.status_code == 200
    access_token = response.json()["access_token"]

# Post a comment without slug ❌
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
            headers={
            "Authorization": f"Bearer {access_token}"
        }
        )
    assert response.status_code == 422

# Post a comment ✅
    comment["slug"] = slug
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
            headers={
            "Authorization": f"Bearer {access_token}"
        }
        )
    assert response.status_code == 201

@pytest.mark.asyncio(scope="session")
async def test_2_read_comment(async_app_client: AsyncClient):
    response = await async_app_client.get(
        "/exhortation",
    )
    res_data = response.json()
    assert res_data["count"] == 2

    exhortationId = response.json()["data"][0]["id"]
    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={exhortationId}",
    )
    assert response.status_code == 200
    res_data = response.json()