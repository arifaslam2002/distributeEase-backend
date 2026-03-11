from typing import Optional

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    mrp:float

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    mrp:Optional[float] = None