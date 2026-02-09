from pydantic import BaseModel, Field, field_validator, SecretStr


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=256)


class User(UserBase):
    password: str = Field(min_length=1, max_length=40)