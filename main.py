from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI, Depends

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.currency import router as currency_router
from app.core.security import decode_jwt_token
from app.db.database import engine, Base
from app.utils.external_api import currency_api


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    currency_api.session = aiohttp.ClientSession(headers=currency_api._headers)
    yield
    await currency_api.close()


app = FastAPI(lifespan=lifespan)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    currency_router,
    prefix="/currency",
    tags=["currency"],
    dependencies=[Depends(decode_jwt_token)],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/me")
async def me(payload: dict = Depends(decode_jwt_token)):
    return payload