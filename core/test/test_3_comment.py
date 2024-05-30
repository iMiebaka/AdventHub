import logging, pytest
from .payload import test_data as TEST_DATA
from httpx import AsyncClient, ASGITransport
from core.app import app
from uuid import uuid4 
from bson import ObjectId
from settings import Engine
from core.models.comment import User
from core.models.comment import Comment


engine = Engine
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest.mark.asyncio(scope="session")
async def test_1A_make_comment(async_app_client: AsyncClient):
# Get post to comment ✅
    response = await async_app_client.get(
        "/exhortation",
    )

    access_token = TEST_DATA.read_token(0)
    comment = TEST_DATA.comment_list(0)
    res_data = response.json()["data"][0]
    slug = res_data["slug"]
    exhortationId = res_data["id"]

# Post a comment ❌
    response = await async_app_client.post(
            "/comment/exhortation",
            json=comment,
        )
    assert response.status_code == 401

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

    # Check comment updated ✅ 
    response = await async_app_client.get(
        f"/comment/exhortation?exhortationId={exhortationId}",
    )
    res_data = response.json()
    assert res_data["count"] == 1
    assert res_data["totalPage"] == 1


@pytest.mark.asyncio(scope="session")
async def test_1B_make_multi_comment(async_app_client: AsyncClient):
    # Get post to comment ✅
    
    access_tokens = TEST_DATA.read_token("")
    response = await async_app_client.get(
        "/exhortation",
    )
    slug = response.json()["data"][0]["slug"]
    slugTwo = response.json()["data"][1]["slug"]
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
            "slug": slugTwo,
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
    
    # Check comment pagination
    pages = res_data["totalPage"]
    count = res_data["count"]
    countChecker = 0
    
    for page in range(pages):
        response = await async_app_client.get(
            f"/comment/exhortation?exhortationId={exhortationId}&page={page+1}",
        )
        res_data = response.json()
        countChecker = countChecker + len(res_data["data"])

    assert count == countChecker


@pytest.mark.asyncio(scope="session")
async def test_3_update_comment(async_app_client: AsyncClient):
    comment = await engine.find_one(Comment)
    id = comment.id
    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]
    new_comment = {"body": "lorem has changed"}
    
    # Update post ✅
    response = await async_app_client.put(
        f"/comment/exhortation?id={id}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()  
    assert response.status_code == 200
    assert res_data["body"] == new_comment["body"]
    new_comment["body"] = "I want to force my way in"

    access_token = access_tokens[1]
    response = await async_app_client.put(
        f"/comment/exhortation?id={id}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json() 
    assert response.status_code == 401

    access_token = access_tokens[2]
    response = await async_app_client.put(
        f"/comment/exhortation?id={id}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json() 
    assert response.status_code == 401
    
    access_token = access_tokens[3]
    response = await async_app_client.put(
        f"/comment/exhortation?id={id}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json() 
    assert response.status_code == 401

    new_comment["body"] = "No one can take the place"
    access_token = access_tokens[0]
    response = await async_app_client.put(
        f"/comment/exhortation?id={id}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json() 
    assert response.status_code == 200

    response = await async_app_client.put(
        f"/comment/exhortation?id={ObjectId()}",
        json=new_comment,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 404