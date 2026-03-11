from sqlalchemy import Column, Float, Integer, String
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    mrp = Column(Float)
