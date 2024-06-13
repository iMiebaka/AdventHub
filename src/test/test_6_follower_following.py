import logging, pytest
from httpx import AsyncClient, ASGITransport
from .payload import test_data as TEST_DATA
from src.models.user import FollowerFollowing, User
from src.core.request import followers
from src.app import app
from settings import Engine


engine = Engine
LOGGER = logging.getLogger(__name__)

def debug(value: str):
    LOGGER.info(value)


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest.mark.asyncio(scope="session")
async def test_1_follow_user(async_app_client: AsyncClient):
# Get followers ✅
    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]

    response = await async_app_client.get(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_datas = response.json()
    assert len(res_datas["data"]) == 0

    users = await engine.find(User)
    user = users[1]
    username = user.username
    access_token = access_tokens[1]
    

    # try following yourself ❌
    response = await async_app_client.post(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={"username": username}

    )
    res_datas = response.json()
    assert res_datas == {'message': 'User already following'}
    _followers = await engine.find(FollowerFollowing, FollowerFollowing.user == user.id)
    assert _followers == []
    
    user = users[0]
    username = user.username
    # try following another user ✅
    response = await async_app_client.post(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={"username": username}

    )
    res_datas = response.json()
    assert res_datas == {'message': 'User Followed'}
    user = users[1]
    _followers = await engine.find(FollowerFollowing, FollowerFollowing.user == user.id)
    assert len(_followers) == 1

    user = users[0]
    response = await async_app_client.get(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_datas = response.json()
    assert len(res_datas["data"]) == 1

# Hit again to unfollowed ✅
    response = await async_app_client.post(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={"username": username}

    )
    res_datas = response.json()
    assert res_datas == {'message': 'User Unfollowed'}

    _followers = await engine.find(FollowerFollowing, FollowerFollowing.friend  == user.id)
    assert len(_followers) == 0
    

@pytest.mark.asyncio(scope="session")
async def test_2_multifollow_user(async_app_client: AsyncClient):
    users = await engine.find(User)
    user = users[-1]
    username = user.username

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[-1]

# Check if list is updated ["Empty"]
    response = await async_app_client.get(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_datas = response.json()
    assert len(res_datas["data"]) == 0
    
# last user should follow everyone else ✅
    for user in users:
        response = await async_app_client.post(
            "/request/followers",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            json={"username": user.username}

        )
        res_datas = response.json()
        if user.username != username:
            assert res_datas == {'message': 'User Followed'}
        else:
            assert res_datas == {'message': 'User already following'}

# Check if list is updated
    response = await async_app_client.get(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_datas = response.json()
    assert len(res_datas["data"]) == len(users) - 1


@pytest.mark.asyncio(scope="session")
async def test_3_unfollow_last_follower_user(async_app_client: AsyncClient):
    users = await engine.find(User)
    user = users[-2]
    username = user.username

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[-1]

    # last user should follow everyone else ✅
    response = await async_app_client.post(
            "/request/followers",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            json={"username": username}

        )
    res_datas = response.json()
    if user.username != username:
        assert res_datas == {'message': 'User Unfollowed'}

# Check if list is updated
    response = await async_app_client.get(
        "/request/followers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_datas = response.json()
    assert len(res_datas["data"]) == len(users) - 2


@pytest.mark.asyncio(scope="session")
async def test_4_follow_following_via_profile(async_app_client: AsyncClient):
    users = await engine.find(User)
    user = users[-1]
    username = user.username

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[-1]

    response = await async_app_client.get(
        "/account/profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    followers = await engine.count(FollowerFollowing, FollowerFollowing.user == user.id)
    following = await engine.count(FollowerFollowing, FollowerFollowing.friend == user.id)
    assert res_data["profile"]["following"] == following
    assert res_data["profile"]["followers"] == followers

    response = await async_app_client.get(
        f"/account?username={username}",
    )
    res_data = response.json()
    
    assert res_data["profile"].get("following") == None
    assert res_data["profile"].get("followers") == None