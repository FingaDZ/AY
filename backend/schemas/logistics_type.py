from pydantic import BaseModel
from typing import Optional

class LogisticsTypeBase(BaseModel):
    name: str
    is_active: bool = True

class LogisticsTypeCreate(LogisticsTypeBase):
    pass

class LogisticsTypeUpdate(LogisticsTypeBase):
    pass

class LogisticsTypeResponse(LogisticsTypeBase):
    id: int

    class Config:
        from_attributes = True
