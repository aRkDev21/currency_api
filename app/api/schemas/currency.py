from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Exchange(BaseModel):
    from_: str = Field(alias="from", pattern=r"^[A-Z]{3}$")
    amount: float = Field(..., gt=0)
    to: str = Field(pattern=r"^[A-Z]{3}$")
    date: Optional[datetime] = None # change format

    model_config = ConfigDict(populate_by_name=True)
