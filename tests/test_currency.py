import pytest

from tests.test_auth import get_auth_headers

@pytest.mark.anyio
async def test_requires_auth_exchange(client):
    response = await client.get("/currency/exchange", params={"from": "USD", "to": "EUR", "amount": 100})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_requires_auth_list(client):
    response = await client.get("/currency/list")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_currency_list_with_token(client):
    headers = await get_auth_headers(client)
    response = await client.get("/currency/list", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@pytest.mark.anyio
async def test_currency_exchange_valid(client):
    headers = await get_auth_headers(client)
    response = await client.get(
        "/currency/exchange",
        headers=headers,
        params={"from": "USD", "to": "EUR", "amount": 100}
    )
    assert response.status_code == 200
    data = response.json()
    assert "from" in data and "to" in data and "amount" in data


@pytest.mark.anyio
@pytest.mark.parametrize(
    "bad_from,bad_to",
    [
        ("XXX", "USD"),
        ("USD", "YYY"),
        ("AAA", "BBB"),
    ],
)
async def test_currency_exchange_invalid_codes(client, bad_from, bad_to):
    headers = await get_auth_headers(client)
    response = await client.get(
        "/currency/exchange",
        headers=headers,
        params={"from": bad_from, "to": bad_to, "amount": 100}
    )
    assert response.status_code == 400