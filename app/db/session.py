
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from models import user, shop, product, order, order_item

load_dotenv()

DATABASE_URL = os.getenv("Db_url")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)  # factory, not a session itself

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()