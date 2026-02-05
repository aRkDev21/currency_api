from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.currency import Exchange
from app.utils.external_api import currency_api


router = APIRouter()

@router.get("/exchange")
async def exchange(exc: Annotated[Exchange, Depends()]):
    response = await currency_api.fetch_exchange(exc)
    if response["success"]:
        return {"result": response["result"]}
    return {"error": response["error"]}


@router.get("/list")
async def list_currencies():
    response = await currency_api.fetch_currencies()
    if response["success"]:
        return {"currencies": response["currencies"]}
    return {"error": response["error"]}