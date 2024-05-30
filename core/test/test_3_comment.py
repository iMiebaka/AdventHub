import logging, pytest
from .payload import test_data as TEST_DATA
from httpx import AsyncClient, ASGITransport
from core.app import app
from uuid import uuid4 
from bson import ObjectId




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
    comment = TEST_DATA.comment_list(0)

# Post a comment ❌
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
        )
    assert response.status_code == 401

    user = TEST_DATA.user_list(0)
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
async def test_1_make_multi_comment(async_app_client: AsyncClient):
    users = TEST_DATA.user_list("")
    # Get post to comment ✅
    response = await async_app_client.get(
        "/exhortation",
    )
    slug = response.json()["data"][0]["slug"]
    

    return
    for iter, c in enumerate(range(10)):
        c = {
            "slug": slug,
            "body": f"lorem comment {iter + 1} from == test_1_make_comment"
        }
        response = await async_app_client.post(
                "/comment/exhortation",
                json=c,
                headers={
                "Authorization": f"Bearer {access_tokens[0]}"
            }
            )
        assert response.status_code == 201

    for iter, c in enumerate(range(10, 20)):
        c = {
            "slug": slug,
            "body": f"lorem comment {iter + 1} from == test_1_make_comment"
        }
        response = await async_app_client.post(
                "/comment/exhortation",
                json=c,
                headers={
                "Authorization": f"Bearer {access_tokens[1]}"
            }
            )
        assert response.status_code == 201

    for iter, c in enumerate(range(20,30)):
        c = {
            "slug": slug,
            "body": f"lorem comment {iter + 1} from == test_1_make_comment"
        }
        response = await async_app_client.post(
                "/comment/exhortation",
                json=c,
                headers={
                "Authorization": f"Bearer {access_tokens[iter]}"
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
        f"/comment/exhortation?exhortationId={exhortationId}544",
    )
    assert response.status_code == 422

    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={uuid4().hex}",
    )
    assert response.status_code == 422

    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={ObjectId()}",
    )
    res_data = response.json()
    assert res_data["data"] == []

    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={exhortationId}",
    )
    assert response.status_code == 200
    res_data = response.json()
    LOGGER.info(res_data)