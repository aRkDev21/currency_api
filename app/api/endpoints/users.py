from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.user import User
from app.db.dao import dao
from app.core.security import get_user_from_token, create_access_token

router = APIRouter()

@router.post("/auth/register")
async def register(user: User) -> dict:
    if dao.add_user(user):
        return {"message": "User registered successfully"}

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already exists",
    )


@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usr = dao.get_user(form_data.username)
    if not usr or not usr.password == form_data.password: # !!! verify by hash
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": usr.username})

    return {"access_token": token}


@router.get("/me")
async def get_me(user: str = Depends(get_user_from_token)) -> User:
    return dao.get_user(user)