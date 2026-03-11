from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from core.dependecies import require_roles
from models.order_item import OrderItem
from models.product import Product
from schemas.product_schema import ProductCreate,ProductUpdate

router = APIRouter()


@router.post("/product")
def add_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    product = db.query(Product).filter(Product.name == data.name).first()
    if product:
        raise HTTPException(status_code=400, detail="This Product is already Listed")
    new_product = Product(name=data.name, price=data.price, mrp=data.mrp)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/product/{product_id}")
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="This Product is Not in the list")
    return product
@router.patch("/product/{product_id}")
def update_product_by_id(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ each field independent — not nested inside each other
    if data.name  is not None: 
        product.name  = data.name
    if data.price is not None:
        product.price = data.price
    if data.mrp   is not None: 
        product.mrp   = data.mrp

    db.commit()
    db.refresh(product)
    return product
@router.get("/products")
def get_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    products = db.query(Product).all()
    return products


@router.delete("/product/{product_id}")
def delete_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):   
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="This Product is Not in the list")
    used = db.query(OrderItem).filter(OrderItem.product_id == product_id).first()
    if used:
        # Option A — block deletion
        raise HTTPException(status_code=400, detail="Cannot delete product — it is part of existing orders")
    db.delete(product)
    db.commit()
    return {"message": f"{product.name} deleted successfully"}
