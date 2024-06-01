import logging, pytest
from .payload import test_data as TEST_DATA
from httpx import AsyncClient, ASGITransport
from src.app import app
from src.models.comment import Comment
from settings import Engine


engine = Engine
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest.mark.asyncio(scope="session")
async def test_1_reaction_exhortation(async_app_client: AsyncClient):
# Get post to exhortation ✅
    response = await async_app_client.get(
        "/exhortation",
    )

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]
    res_datas = response.json()["data"]
    res_data = res_datas[0]
    exhortationId = res_data["id"]

# like post ❌
    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
    )
    assert response.status_code == 401

    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}

    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 0, 'reacted': False}

    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}

    access_token = access_tokens[1]
    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    _res_data = response.json()
    assert _res_data == {'count': 2, 'reacted': True}
    total_length = _res_data["count"]

    response = await async_app_client.get(
        "/exhortation",
    )
    assert len(response.json()["data"][0]["reaction"]) == total_length

    res_data = res_datas[1]
    exhortationId = res_data["id"]
    response = await async_app_client.get(
        "/reaction/exhortation?id=" + exhortationId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}


@pytest.mark.asyncio(scope="session")
async def test_2_reaction_comment(async_app_client: AsyncClient):
# Get post to exhortation ✅
    comments = await engine.find(Comment)
    commentId = str(comments[0].id)

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]

# like comment ❌
    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
    )
    assert response.status_code == 401

# like comment ✅
    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}

    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 0, 'reacted': False}

    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}

    access_token = access_tokens[1]
    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    _res_data = response.json()
    assert _res_data == {'count': 2, 'reacted': True}
    total_length = _res_data["count"]

    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={comments[0].exhortation.id}",
    )
    assert len(response.json()["data"][0]["reaction"]) == total_length

    commentId = str(comments[1].id)
    response = await async_app_client.get(
        "/reaction/comment?id=" + commentId,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.json() == {'count': 1, 'reacted': True}