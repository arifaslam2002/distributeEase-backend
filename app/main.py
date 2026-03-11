from app.db.session import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_router import router as auth_router
from routers.order_router import router as order_router
from routers.product_router import router as product_router
from routers.shop_router import router as shop_router

app = FastAPI(title="distributeEase")
create_tables()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(shop_router, prefix="/shops", tags=["Shops"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
