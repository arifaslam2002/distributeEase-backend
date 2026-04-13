from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from core.dependecies import require_roles
from models.shop import Shop
from schemas.shop_schema import ShopCreate ,ShopUpdate
from sqlalchemy.orm import Session
router = APIRouter()
@router.post("/shop")
def add_shop(data:ShopCreate,db:Session = Depends(get_db),current_user = Depends(require_roles(["admin","salesman"]))):
        existing = db.query(Shop).filter(
        Shop.shop_name == data.shop_name,
        Shop.address   == data.address
    ).first()
        if existing :
          raise HTTPException(status_code=400,detail="This shop is already registered")
        new_shop = Shop(
        shop_name=data.shop_name,
        phone=data.phone,
        address=data.address,
        salesman_id = int(current_user["id"])

    )
        db.add(new_shop)
        db.commit()
        db.refresh(new_shop)
        return new_shop
@router.get("/shops")
def get_shops(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    # ✅ all roles see all shops
    shops = db.query(Shop).all()

    return [
        {
            "id":        s.id,
            "shop_name": s.shop_name,
            "phone":     s.phone,
            "address":   s.address,
            "is_active": s.is_active,
            "salesman_id": s.salesman_id,
        }
        for s in shops
    ]
@router.patch("/shops/{shop_id}")
def update_shop(
     shop_id:int,
     data:ShopUpdate,
     db:Session = Depends(get_db),
     current_user = Depends(require_roles(["admin","salesman"]))):
     shop = db.query(Shop).filter(Shop.id == shop_id).first()
     if not shop:
        raise HTTPException(status_code=404,detail="No shop is registered")
     if data.shop_name is not None:
      shop.shop_name = data.shop_name
     if data.phone is not None:
      shop.phone=data.phone
     if data.address is not None:
      shop.address=data.address
     db.commit()
     db.refresh(shop)
     return shop

@router.delete("/shop/{shop_id}")
def delete_shop(
     shop_id:int,
     db:Session = Depends(get_db),
     current_user = Depends(require_roles(["admin","salesman"]))):
     shop = db.query(Shop).filter(Shop.id == shop_id).first()
     if not shop:
        raise HTTPException(status_code=404,detail="No shop is registered") 
     shop.is_active = False
     db.commit() 
     return {"message": f"{shop.shop_name} deactivated successfully"}
