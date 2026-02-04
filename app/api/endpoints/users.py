from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.user import User, UserDB
from app.db.dao import dao
from app.core.security import (
    decode_jwt_token, create_token, hash_password, verify_password,
    get_current_refresh_token, get_current_access_token, REFRESH_TOKEN_EXPIRE_MINUTES
)


router = APIRouter()
refresh_tokens = {}


@router.post("/auth/register")
async def register(user: User) -> dict:
    user_db = UserDB(username=user.username, hashed_password=hash_password(user.password))
    if dao.add_user(user_db):
        return {"message": "User registered successfully"}

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already exists",
    )


@router.post("/auth/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    usr = dao.get_user(form_data.username)
    if not usr or not verify_password(form_data.password, usr.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_token({"sub": usr.username})
    refresh_token = create_token({"sub": usr.username}, token_type="refresh")
    refresh_tokens[usr.username] = refresh_token
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True,
                        max_age=60*REFRESH_TOKEN_EXPIRE_MINUTES)

    return {"access_token": access_token}


@router.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    payload = decode_jwt_token(request.cookies.get("refresh_token"))
    username = payload.get("sub")
    if username in refresh_tokens:
        new_access = create_token({"sub": username})
        new_refresh = create_token({"sub": username}, token_type="refresh")
        refresh_tokens[username] = new_refresh
        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, secure=True,
                            samesite="strict", max_age=60 * REFRESH_TOKEN_EXPIRE_MINUTES)
        return {"access_token": new_access}

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token not in database")


@router.get("/me")
async def get_me(payload: dict = Depends(get_current_access_token)) -> str:
    return f"Hello {payload['sub']}"