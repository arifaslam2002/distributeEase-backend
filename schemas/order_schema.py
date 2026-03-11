from typing import List, Optional

from pydantic import BaseModel


class Item(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[Item]


class OrderUpdate(BaseModel):
    items: Optional[List[Item]] = None
