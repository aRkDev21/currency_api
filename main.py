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

if __name__ == "__main__":
    import os

    TARGET_DIRS = {"app", "tests"}
    EXCLUDE_DIRS = {".venv", "venv", "__pycache__"}


    def print_project_code(root="."):
        for dirpath, dirnames, filenames in os.walk(root):
            # исключаем ненужные директории
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            # проверяем, что мы внутри app или tests
            parts = set(dirpath.split(os.sep))
            if not parts & TARGET_DIRS:
                continue

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue  # бинарные файлы / ошибки чтения

                print("\n" + "=" * 80)
                print(f"FILE: {file_path}")
                print("=" * 80)
                print(content)


    if __name__ == "__main__":
        print_project_code()
