from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.endpoints.users import router as users_router
from app.db.dao import dao


@asynccontextmanager
async def lifespan(app_: FastAPI):
    yield
    dao.save()


app = FastAPI(lifespan=lifespan)

app.include_router(
    users_router
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
