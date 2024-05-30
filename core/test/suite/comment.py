import logging
from ..payload import test_data
from httpx import AsyncClient


LOGGER = logging.getLogger(__name__)

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
    LOGGER.info(comment)
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
            headers={
            "Authorization": f"Bearer {access_token}"
        }
        )
    LOGGER.info(response.json())
    assert response.status_code == 201