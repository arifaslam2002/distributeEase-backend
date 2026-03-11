from typing import Optional

from pydantic import BaseModel


class ShopCreate(BaseModel):
    shop_name: str
    phone: str
    address: str


class ShopUpdate(BaseModel):
    shop_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
