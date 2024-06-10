import logging, pytest
from .payload import test_data as TEST_DATA
from httpx import AsyncClient, ASGITransport
from src.app import app
from settings import Engine


engine = Engine
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def async_app_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest.mark.asyncio(scope="session")
async def test_1_create_hightlight(async_app_client: AsyncClient):
# Get exhortation ✅
    response = await async_app_client.get(
        "/exhortation",
    )

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]
    res_datas = response.json()["data"]
    exhortationId = res_datas[0]["id"]

# lighlight post ❌
    response = await async_app_client.post(
        "/highlights",
        json={"exhortationId": exhortationId},
    )
    assert response.status_code == 401

    for exhortation in [res_datas[0], res_datas[1]]:
        response = await async_app_client.post(
            "/highlights",
            json={"exhortationId": exhortation["id"]},
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        assert response.status_code == 200



@pytest.mark.asyncio(scope="session")
async def test_2_read_hightlight(async_app_client: AsyncClient):
    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[0]

    response = await async_app_client.get(
        "/highlights",
    )
    assert response.status_code == 401

    response = await async_app_client.get(
        "/highlights",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    res_data["count"] == 2

    access_token = access_tokens[1]
    response = await async_app_client.get(
        "/highlights",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    res_data["count"] == 1
    
    access_token = access_tokens[2]
    response = await async_app_client.get(
        "/highlights",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    res_data["count"] == 1

    access_token = access_tokens[0]
    response = await async_app_client.get(
        "/highlights",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    res_data = response.json()
    res_data["count"] == 1


@pytest.mark.asyncio(scope="session")
async def test_3_de_hightlight(async_app_client: AsyncClient):
# Get exhortation ✅
    response = await async_app_client.get(
        "/exhortation",
    )

    access_tokens = TEST_DATA.read_token("")
    access_token = access_tokens[1]
    res_datas = response.json()["data"]

    post = TEST_DATA.exhortation_list["textBase"][3]
    post["body"] = "This must be highlighted at all times"
    response = await async_app_client.post(
        "/exhortation",
        data=post,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert response.status_code == 201
    exhortationId = response.json()["id"]

    access_token = access_tokens[0]
    response = await async_app_client.post(
            "/highlights",
            json={"exhortationId": exhortationId},
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
    assert response.status_code == 200

    exhortationId = res_datas[1]["id"]
    for access_token in [access_tokens[0], access_tokens[1]]:
        response = await async_app_client.post(
            "/highlights",
            json={"exhortationId": exhortationId},
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        assert response.status_code == 200
