from typing import Optional

import aiohttp
from fastapi import HTTPException

from app.api.schemas.currency import Exchange
from app.core.config import settings


class CurrencyAPI:
    def __init__(self, api_key: str):
        self._base_url = "https://api.apilayer.com/currency_data"
        self._headers = {"apikey": api_key}
        self.session: Optional[aiohttp.ClientSession] = None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _fetch(self, endpoint: str, **kwargs) -> dict:
        try:
            async with self.session.get(f"{self._base_url}/{endpoint}", **kwargs) as response:
                if response.status != 200:
                    raise HTTPException(response.status, detail="external api error")
                return await response.json()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=503, detail=str(e))

    async def fetch_exchange(self, exchange: Exchange):
        params = exchange.model_dump(by_alias=True, exclude_none=True)
        return await self._fetch("convert", params=params)


    async def fetch_currencies(self):
        return await self._fetch("currencies")


currency_api = CurrencyAPI(api_key=settings.API_KEY.get_secret_value())