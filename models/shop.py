from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.db.base import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    shop_name = Column(String)
    phone = Column(String)
    address = Column(String)
    salesman_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
