from pydantic import BaseModel, Field, field_validator, SecretStr


class User(BaseModel):
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=256)
