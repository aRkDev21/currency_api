import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.database import Base, get_db
from main import app
from app.utils.external_api import currency_api


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine):
    async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def override_get_db(async_session):
    async def _override():
        async with async_session as session:
            yield session
    app.dependency_overrides[get_db] = _override
    return _override



@pytest.fixture(autouse=True)
def mock_currency_api(monkeypatch):
    VALID_CURRENCIES = {"USD", "EUR"}

    async def mock_fetch_exchange(exc):
        if exc.from_ not in VALID_CURRENCIES or exc.to not in VALID_CURRENCIES:
            return {"success": False, "error": "Invalid currency code"}
        return {"success": True, "result": 25.5}

    async def mock_fetch_currencies():
        return {"success": True, "currencies": {"USD": "Dollar", "EUR": "Euro"}}

    monkeypatch.setattr(currency_api, "fetch_exchange", mock_fetch_exchange)
    monkeypatch.setattr(currency_api, "fetch_currencies", mock_fetch_currencies)


@pytest.fixture(scope="function")
async def client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac
