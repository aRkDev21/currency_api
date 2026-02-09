from fastapi import APIRouter, Query, HTTPException
from app.api.schemas.currency import Exchange
from app.utils.external_api import currency_api

router = APIRouter()

@router.get("/exchange")
async def exchange(
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: float = Query(...)
):
    exc = Exchange(from_=from_, to=to, amount=amount)
    response = await currency_api.fetch_exchange(exc)
    if not response["success"]:
        raise HTTPException(status_code=400, detail=response.get("error"))
    return {
        "from": exc.from_,
        "to": exc.to,
        "amount": exc.amount,
        "result": response["result"]
    }

@router.get("/list")
async def list_currencies():
    response = await currency_api.fetch_currencies()
    if not response["success"]:
        raise HTTPException(status_code=400, detail=response.get("error"))
    return {"currencies": response["currencies"]}
