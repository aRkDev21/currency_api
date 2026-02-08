from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import User
from app.core.security import (
    decode_jwt_token, create_token, hash_password, verify_password,
)
from app.core.config import settings
from app.db.repo.user_repo import UserRepository
from app.db.database import get_db

router = APIRouter()
refresh_tokens = {}


@router.post("/register")
async def register(user: User, db: AsyncSession = Depends(get_db)) -> dict:
    repo = UserRepository(db)

    existing_user = await repo.get_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = hash_password(user.password)
    await repo.create(user.username, hashed)

    return {"message": "User registered successfully"}


@router.post("/login")
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)

    usr = await repo.get_by_username(form_data.username)
    if not usr or not verify_password(form_data.password, str(usr.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_token({"sub": usr.username})
    refresh_token = create_token({"sub": usr.username}, token_type="refresh")
    refresh_tokens[usr.username] = refresh_token
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True,
                        samesite="strict", max_age=60*settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token}


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    payload = decode_jwt_token(request.cookies.get("refresh_token"))
    username = payload.get("sub")
    if username in refresh_tokens:
        new_access = create_token({"sub": username})
        new_refresh = create_token({"sub": username}, token_type="refresh")
        refresh_tokens[username] = new_refresh
        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, secure=True,
                            samesite="strict", max_age=60 * settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        return {"access_token": new_access}

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token not in database")
