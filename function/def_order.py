from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from Database.model import CartUserDATABASE, CartItemDATABASE, ProductDATABASE, OrderDATABASE, OrderItemDATABASE, UserDATABASE
from schemas import OrderSearch
from uuid import UUID
from datetime import datetime

def checkout_cart(db: Session, user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบตะกร้าสินค้า")
    cart_items = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ตะกร้าว่างเปล่า ไม่สามารถชำระเงินได้")
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="พบสินค้าบางรายการในตะกร้าที่ถูกลบออกจากระบบแล้ว")
        if product.stock_db < item.quantity_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"สินค้า '{product.name_db}' มี stock เหลือแค่ {product.stock_db} ชิ้น แต่สั่ง {item.quantity_db} ชิ้น")
    price_total = 0.0
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        price_total += product.price_db * item.quantity_db
    vat       = round(price_total * 0.07, 2)
    total_vat = round(price_total + vat, 2)
    neworder = OrderDATABASE(user_id_db=user.id_db, total_price=total_vat)
    db.add(neworder)
    db.flush()# ได้ id ก่อน commit
    purchased_items = []
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        neworder_item = OrderItemDATABASE(
            order_id_db        = neworder.id_db,
            product_id_db      = item.product_id_db,
            quantity_db        = item.quantity_db,
            price_per_piece_db = product.price_db,
        )
        db.add(neworder_item)
        product.stock_db -= item.quantity_db  # ✅ ตัด stock
        purchased_items.append({
            "product_name"    : product.name_db,
            "quantity"        : item.quantity_db,
            "price_per_piece" : product.price_db,
            "subtotal"        : round(product.price_db * item.quantity_db, 2),
        })
    db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).delete(synchronize_session=False)
    db.commit()
    return {
        "message"     : "ชำระแล้วจ้า",
        "order_id"    : neworder.id_db,
        "items"       : purchased_items,  
        "price_total" : price_total,
        "vat"         : vat,
        "final_price" : total_vat,
    }

def all_orders(db: Session, user: UserDATABASE):
    orders = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db).all()
    if not orders:
        return {"order": [], "message": "ยังไม่มีบิล"}
    result = []
    for order in orders:
        items      = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        item_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            item_detail.append({
                "product"  : product.name_db if product else "ถูกลบออกจากระบบแล้ว",
                "quantity" : item.quantity_db,
                "price"    : item.price_per_piece_db,
            })
        result.append({
            "order_id"    : order.id_db,
            "created_at"  : order.create_at,
            "total_price" : order.total_price,
            "items"       : item_detail,
        })
    return {"Orders": result}

def search_order_uuid(uuid_orders :UUID, db:Session, user: UserDATABASE):
    orders = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db, OrderDATABASE.id_db == uuid_orders).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบบิล")
    resault = []
    for order in orders:
        items = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        item_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            item_detail.append({"product": product.name_db if product else "ถูกลบออกจากระบบแล้ว",
                                "quantity": item.quantity_db,
                               "price": item.price_per_piece_db})
        resault.append({"order_id"   : order.id_db,
                        "created_at" : order.create_at,
                        "total_price": order.total_price,
                        "items"      : item_detail,})
    return {"Orders": resault}

def search_my_orders(data: OrderSearch, db: Session, user: UserDATABASE):
    query = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db)
    if data.start_date:
        query = query.filter(OrderDATABASE.create_at >= datetime.combine(data.start_date, datetime.min.time()))#combine มีหน้าที่จับ date กับ time เข้าด้วยกัน
    if data.end_date:
        query = query.filter(OrderDATABASE.create_at <= datetime.combine(data.end_date, datetime.max.time().replace(microsecond=0)))
    orders = query.order_by(OrderDATABASE.create_at.desc()).all()
    if not orders:
        return {"orders": [], "message": "ไม่พบบิลที่ตรงกับเงื่อนไข"}
    result = []
    for order in orders:
        items = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        items_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            items_detail.append({
                "product_name" : product.name_db if product else "ถูกลบออกจากระบบแล้ว",
                "quantity"       : item.quantity_db,
                "price_per_piece": item.price_per_piece_db,
            })
        result.append({
            "order_id"   : order.id_db,
            "created_at" : order.create_at,
            "total_price": order.total_price,
            "items"      : items_detail
        })
    return {"orders": result}