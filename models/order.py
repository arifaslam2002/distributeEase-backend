from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer,Float
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    salesman_id = Column(Integer, ForeignKey("users.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    Grand_total = Column(Float)