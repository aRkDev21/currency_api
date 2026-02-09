import pytest

async def get_auth_headers(client, username="test", password="test"):
    await client.post("/auth/register/", json={"username": username, "password": password})

    response = await client.post("/auth/login/", data={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "username,password",
    [
        ("user1", "pass1"),
        ("user2", "pass2"),
    ],
)
async def test_register(client, username, password):
    response = await client.post("/auth/register/", json={"username": username, "password": password})
    assert response.status_code == 201


@pytest.mark.anyio
async def test_register_existing_user(client):
    await client.post("/auth/register/", json={"username": "exists", "password": "111"})
    response = await client.post("/auth/register/", json={"username": "exists", "password": "111"})
    assert response.status_code == 409


@pytest.mark.anyio
async def test_login_user(client):
    await client.post("/auth/register/", json={"username": "login", "password": "test"})
    response = await client.post("/auth/login/", data={"username": "login", "password": "test"})
    assert response.status_code == 200
    assert "access_token" in response.json()