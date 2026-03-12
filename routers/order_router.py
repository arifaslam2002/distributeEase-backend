from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from core.dependecies import require_roles
from core.telegram import send_telegram
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.shop import Shop
from schemas.order_schema import OrderCreate, OrderUpdate

router = APIRouter()


@router.post("/{shop_id}/order")
def add_order(
    shop_id: int,
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="No shop is registered")

    grand_total = 0
    order_items = []

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        amount = product.price * item.quantity
        grand_total += amount

        order_items.append({
            "product_id"  : item.product_id,
            "product_name": product.name,
            "quantity"    : item.quantity,
            "Amount"      : amount
        })

    new_order = Order(
        shop_id=shop_id,
        salesman_id=int(current_user["id"]),
        Grand_total=grand_total
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_items:
        new_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            Amount=item["Amount"],
        )
        db.add(new_item)

    db.commit()

    product_lines = "\n".join([
        f"  - {i['product_name']} x{i['quantity']}"
        for i in order_items
    ])

    message = f"""
🛒 *New Order Placed!*
🏪 Shop     : {shop.shop_name}
👤 Salesman : {current_user['name']}
📦 Products :
{product_lines}
💰 Total    : ₹{grand_total}
🕐 Order ID : {new_order.id}
    """

    try:
        send_telegram(message)
    except Exception:
        pass

    return {
        "message"    : "Order placed successfully",
        "order_id"   : new_order.id,
        "grand_total": grand_total
    }


@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman", "packing"])),
):
    if current_user["role"] in ["admin", "packing"]:
        orders = db.query(Order).all()
    else:
        orders = db.query(Order).filter(Order.salesman_id == int(current_user["id"])).all()

    result = []
    for order in orders:
        shop = db.query(Shop).filter(Shop.id == order.shop_id).first()
        result.append({
            "id"         : order.id,
            "shop_id"    : order.shop_id,
            "shop_name"  : shop.shop_name if shop else None,
            "salesman_id": order.salesman_id,
            "Grand_total": order.Grand_total,
            "order_date" : order.order_date,
        })

    return result


@router.get("/order/{order_id}")
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman", "packing"])),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    shop = db.query(Shop).filter(Shop.id == order.shop_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    products = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        products.append({
            "product_id"  : item.product_id,       # ✅ REQUIRED for edit modal
            "product_name": product.name if product else "Unknown",
            "quantity"    : item.quantity,
            "amount"      : item.Amount,
        })

    return {
        "order_id"   : order.id,
        "shop_id"    : order.shop_id,
        "shop_name"  : shop.shop_name if shop else None,
        "order_date" : order.order_date,
        "Grand_total": order.Grand_total,
        "products"   : products,
    }


@router.get("/{shop_id}/order")
def get_order_by_shop_id(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    orders = db.query(Order).filter(Order.shop_id == shop_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this shop")

    result = []

    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        products = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            products.append({
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "amount": item.Amount,
            })

        result.append({
            "order_id": order.id,
            "order_date": order.order_date,
            "grand_total": order.Grand_total,
            "products": products,
        })

    return {
        "shop_name": shop.shop_name,
        "orders": result
    }
@router.get("/date/{order_date}")
def get_orders_by_date(
    order_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "packing", "salesman"])),
):
    start = datetime(order_date.year, order_date.month, order_date.day, 0, 0, 0)
    end   = datetime(order_date.year, order_date.month, order_date.day, 23, 59, 59)

    orders = db.query(Order).filter(
        Order.order_date >= start,
        Order.order_date <= end
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for {order_date}")

    result = []
    for order in orders:
        shop = db.query(Shop).filter(Shop.id == order.shop_id).first()
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        products = []
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            products.append({
                "product_name": product.name if product else "Unknown",
                "quantity"    : item.quantity,
            })

        result.append({
            "order_id" : order.id,
            "shop_name": shop.shop_name if shop else None,
            "products" : products
        })

    return {"order_date": str(order_date), "orders": result}


@router.patch("/order/{order_id}")
def update_order_by_id(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if data.items is not None:
        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            existing_item = (
                db.query(OrderItem)
                .filter(
                    OrderItem.order_id == order_id,
                    OrderItem.product_id == item.product_id,
                )
                .first()
            )

            if item.quantity == 0:
                if existing_item:
                    all_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
                    if len(all_items) == 1:
                        raise HTTPException(status_code=400, detail="Order must have at least one product")
                    db.delete(existing_item)
                    db.flush()
                else:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not in this order")

            elif existing_item:
                existing_item.quantity = item.quantity
                existing_item.Amount   = product.price * item.quantity

            else:
                new_item = OrderItem(
                    order_id  =order_id,
                    product_id=item.product_id,
                    quantity  =item.quantity,
                    Amount    =product.price * item.quantity,
                )
                db.add(new_item)

        # Recalculate grand total
        db.flush()
        all_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        order.Grand_total = sum(i.Amount for i in all_items)
        db.add(order)

    db.commit()
    db.refresh(order)

    all_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    products = []
    for i in all_items:
        product = db.query(Product).filter(Product.id == i.product_id).first()
        products.append({
            "product_id"  : i.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity"    : i.quantity,
            "amount"      : i.Amount,
        })

        return {
                  "id"       : order.id,   # ← add this
                  "order_id"  : order.id,
                  "order_date": order.order_date,
                  "Grand_total": order.Grand_total,
                  "products"  : products,
                 }


@router.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return {"message": f"Order {order_id} deleted successfully"}


@router.get("/summary/{order_date}")
def get_summary_by_date(
    order_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "packing","salesman"])),
):
    start = datetime(order_date.year, order_date.month, order_date.day, 0, 0, 0)
    end   = datetime(order_date.year, order_date.month, order_date.day, 23, 59, 59)

    orders = db.query(Order).filter(
        Order.order_date >= start,
        Order.order_date <= end
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for {order_date}")

    product_summary = {}
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            if item.product_id in product_summary:
                product_summary[item.product_id] += item.quantity
            else:
                product_summary[item.product_id] = item.quantity

    result = []
    for product_id, total_qty in product_summary.items():
        product = db.query(Product).filter(Product.id == product_id).first()
        result.append({
            "product_name"  : product.name if product else "Unknown",
            "total_quantity": total_qty
        })

    product_lines = "\n".join([
        f"  - {i['product_name']} → {i['total_quantity']} units"
        for i in result
    ])

    message = f"""
📊 *Daily Packing Summary*
📅 Date         : {order_date}
📦 Total Orders : {len(orders)}
👤 Fetched by   : {current_user['name']}

🛒 *Products to Pack:*
{product_lines}

✅ Please start packing!
    """

    try:
        send_telegram(message)
    except Exception:
        pass

    return {
        "date"   : str(order_date),
        "summary": result
    }


@router.get("/orders/{order_id}/items")
def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "salesman"])),
):
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    result = []
    for i in items:
        product = db.query(Product).filter(Product.id == i.product_id).first()
        result.append({
            "product_id"  : i.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity"    : i.quantity,
            "amount"      : i.Amount,
        })
    return result