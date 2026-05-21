from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from Database.model import CartUserDATABASE, CartItemDATABASE, ProductDATABASE, OrderDATABASE, OrderItemDATABASE, UserDATABASE
from schemas import OrderSearch,SelectiveCheckout
from uuid import UUID
from datetime import datetime

from Database.model import CartUserDATABASE, CartItemDATABASE, ProductDATABASE, OrderDATABASE, OrderItemDATABASE, UserDATABASE
from uuid import UUID

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="พบสินค้าบางรายการถูกลบออกจากระบบแล้ว")
        if product.stock_db < item.quantity_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"สินค้า '{product.name_db}' มีสต็อกไม่พอ (เหลือ {product.stock_db} ชิ้น)")
    price_total       = 0.0
    order_items_ready = []
    purchased_items   = []

    for item in cart_items:
        product           = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        price_total      += product.price_db * item.quantity_db
        product.stock_db -= item.quantity_db
        order_items_ready.append(OrderItemDATABASE(
            product_id_db      = item.product_id_db,
            quantity_db        = item.quantity_db,
            price_per_piece_db = product.price_db,
        ))
        purchased_items.append({
            "product_name"   : product.name_db,
            "quantity"       : item.quantity_db,
            "price_per_piece": product.price_db,
            "subtotal"       : round(product.price_db * item.quantity_db, 2),
        })

    vat = round(price_total * 0.07, 2)
    total_vat = round(price_total + vat, 2)

    new_order = OrderDATABASE(user_id_db=user.id_db, total_price=total_vat)
    db.add(new_order)
    db.flush() 

    for order_item in order_items_ready:
        order_item.order_id_db = new_order.id_db
        db.add(order_item)

    db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).delete(synchronize_session=False)
    db.commit()
    return {
        "message"                : "ชำระเงินสำเร็จแล้วจ้า",
        "order_id"               : new_order.id_db,
        "items_purchased"        : len(purchased_items),       
        "items"                  : purchased_items,
        "price_before_vat"       : round(price_total, 2),       
        "vat_7_percent"          : vat,                         
        "final_price"            : total_vat,
        "items_remaining_in_cart": 0,                           
    }

def checkout_selective(data: SelectiveCheckout, db: Session, user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบตะกร้าสินค้า")
    cart_items = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db, CartItemDATABASE.product_id_db.in_(data.product_ids),).all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้าที่เลือกในตะกร้า กรุณาตรวจสอบ product_ids อีกครั้ง")
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="พบสินค้าบางรายการถูกลบออกจากระบบแล้ว")
        if product.stock_db < item.quantity_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"สินค้า '{product.name_db}' มีสต็อกไม่พอ (เหลือ {product.stock_db} ชิ้น)")
    price_total       = 0.0
    order_items_ready = []
    purchased_items   = []
    for item in cart_items:
        product           = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        price_total      += product.price_db * item.quantity_db
        product.stock_db -= item.quantity_db
        order_items_ready.append(OrderItemDATABASE(
            product_id_db      = item.product_id_db,
            quantity_db        = item.quantity_db,
            price_per_piece_db = product.price_db,
        ))
        purchased_items.append({
            "product_name"   : product.name_db,
            "quantity"       : item.quantity_db,
            "price_per_piece": product.price_db,
            "subtotal"       : round(product.price_db * item.quantity_db, 2),
        })
    vat       = round(price_total * 0.07, 2)
    total_vat = round(price_total + vat, 2)

    new_order = OrderDATABASE(user_id_db=user.id_db, total_price=total_vat)
    db.add(new_order)
    db.flush()
    for order_item in order_items_ready:
        order_item.order_id_db = new_order.id_db
        db.add(order_item)
    paid_ids = [item.product_id_db for item in cart_items]
    db.query(CartItemDATABASE).filter( CartItemDATABASE.cart_id_db == cart.id_db,CartItemDATABASE.product_id_db.in_(paid_ids),).delete(synchronize_session=False)
    db.commit()
    remaining = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).count()
    return {
        "message"                : "ชำระเงินสำเร็จแล้วจ้า",
        "order_id"               : new_order.id_db,
        "items_purchased"        : len(purchased_items),       
        "items"                  : purchased_items,
        "price_before_vat"       : round(price_total, 2),      
        "vat_7_percent"          : vat,                       
        "final_price"            : total_vat,
        "items_remaining_in_cart": remaining,
    }
    
def all_orders(request:Request ,db: Session, user: UserDATABASE):
    orders = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db).all()
    if not orders:
        return {"total": 0, "orders": []}  
    result = []
    for order in orders:
        items      = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        item_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            image = str(request.base_url).rstrip("/")
            if product:
                image_url    = f"{image}{product.image_db}" if product.image_db else None
                product_name = product.name_db
            else:
                image_url    = None
                product_name = "ถูกลบออกจากระบบแล้ว"
            item_detail.append({
                "product_name"  : product_name,
                "image_url" : image_url,
                "quantity" : item.quantity_db,
                "price_per_piece"    : item.price_per_piece_db,
                "subtotal": round((item.price_per_piece_db or 0) * item.quantity_db, 2),
            })
        result.append({
            "order_id"    : order.id_db,
            "created_at" : order.create_at.isoformat(), 
            "total_price" : order.total_price,
            "items"       : item_detail,
        })
    return {"total": len(result), "orders": result}  

def search_order_uuid(uuid_orders :UUID,request:Request ,db:Session, user: UserDATABASE):
    orders = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db, OrderDATABASE.id_db == uuid_orders).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบบิล")
    resault = []
    for order in orders:
        items = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        item_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            image = str(request.base_url).rstrip("/")
            image_url = f"{image}{product.image_db}" if product.image_db else None
            item_detail.append({"product_name": product.name_db if product else "ถูกลบออกจากระบบแล้ว",
                                "uuid_product": product.id_db,
                                "image_url" : image_url,
                                "quantity": item.quantity_db,
                               "price_per_piece": item.price_per_piece_db,
                               "subtotal": round((item.price_per_piece_db or 0) * item.quantity_db, 2),})
        resault.append({"order_id"   : order.id_db,
                        "created_at" : order.create_at.isoformat(),
                        "total_price": order.total_price,
                        "items"      : item_detail,})
    return {"total": len(resault), "orders": resault}

def search_my_orders(request:Request,data: OrderSearch, db: Session, user: UserDATABASE):
    query = db.query(OrderDATABASE).filter(OrderDATABASE.user_id_db == user.id_db)
    if data.start_date:
        query = query.filter(OrderDATABASE.create_at >= datetime.combine(data.start_date, datetime.min.time()))#combine มีหน้าที่จับ date กับ time เข้าด้วยกัน
    if data.end_date:
        query = query.filter(OrderDATABASE.create_at <= datetime.combine(data.end_date, datetime.max.time().replace(microsecond=0)))
    orders = query.order_by(OrderDATABASE.create_at.desc()).all()
    if not orders:
        return {"total": 0, "orders": []} 
    result = []
    for order in orders:
        items = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == order.id_db).all()
        items_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            image = str(request.base_url).rstrip("/")
            if product:
                image_url    = f"{image}{product.image_db}" if product.image_db else None
                product_name = product.name_db
            else:
                image_url    = None
                product_name = "ถูกลบออกจากระบบแล้ว"
            items_detail.append({
                "product_name" : product_name,
                "image_url" : image_url,
                "quantity"       : item.quantity_db,
                "price_per_piece": item.price_per_piece_db,
                "subtotal": round((item.price_per_piece_db or 0) * item.quantity_db, 2),
            })
        result.append({
            "order_id"   : order.id_db,
            "created_at" : order.create_at.isoformat(),
            "total_price": order.total_price,
            "items"      : items_detail
        })
    return  {"total": len(result), "orders": result}