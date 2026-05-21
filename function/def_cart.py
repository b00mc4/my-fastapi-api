from pydantic import Field
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from Database.model import ProductDATABASE, CartUserDATABASE, CartItemDATABASE, UserDATABASE
from schemas import SaiCart,Quantity
from uuid import UUID

def _price_label(price: float, price_type: str) -> str:
    unit = "แพ็ค" if price_type == "pack" else "กิโล"
    return f"฿{price:,.2f} / {unit}"

def get_product(data: SaiCart, db: Session) :
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == data.uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    return product
    
def get_cart(db:Session, user:UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == user.id_db).first()
    if not cart:
        cart = CartUserDATABASE(user_id_db=user.id_db)
        db.add(cart)
        db.commit()
        db.refresh(cart) 
    return cart
    
def add_to_cart_main(data: SaiCart, db: Session, current_user: UserDATABASE):
    product = get_product(data, db)
    cart = get_cart(db, current_user)
    cart_item = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db, CartItemDATABASE.product_id_db == data.uuid_product).first()
    current_in_cart = cart_item.quantity_db if cart_item else 0
    total_quantity  = current_in_cart + data.quantity
    if product.stock_db == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"สินค้า '{product.name_db}' หมดแล้ว")
    if total_quantity > product.stock_db:
        available = product.stock_db - current_in_cart
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"สินค้า '{product.name_db}' มี stock เหลือ {product.stock_db} ชิ้น "f"(ในตะกร้ามีอยู่แล้ว {current_in_cart} ชิ้น เพิ่มได้อีกแค่ {available} ชิ้น)")
    if cart_item:
        cart_item.quantity_db = total_quantity
    else:
        new_cart_item = CartItemDATABASE(cart_id_db  = cart.id_db,product_id_db = data.uuid_product,quantity_db  = data.quantity)
        db.add(new_cart_item)
    db.commit()
    return {
        "message"        : f"หยิบ '{product.name_db}' จำนวน {data.quantity} ชิ้น ลงตะกร้าเรียบร้อยแล้ว",
        "product_id"     : product.id_db,
        "product_name"   : product.name_db,
        "quantity_added" : data.quantity,
        "quantity_in_cart": total_quantity,
        "price" : product.price_db,
        "total_price" : round(product.price_db * total_quantity,2),
        "price_label"    : _price_label(product.price_db, product.price_type_db),
    }

def edit_quantity(uuid_product:UUID ,data:Quantity, db:Session, user:UserDATABASE ):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="คุณยังไม่มีตะกร้าสินค้า")
    cart_item = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db==cart.id_db, CartItemDATABASE.product_id_db == uuid_product).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้านี้ในตะกร้าของคุณ")
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if data.quantity_sm > product.stock_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"สินค้า '{product.name_db}' มี stock เหลือแค่ {product.stock_db} ชิ้น")
    cart_item.quantity_db = data.quantity_sm
    db.commit()
    return {
        "message"         : f"อัปเดตจำนวน '{product.name_db}' เป็น {data.quantity_sm} ชิ้น เรียบร้อยแล้ว",
        "product_id"      : product.id_db,
        "product_name"    : product.name_db,
        "new_quantity"    : data.quantity_sm,
        "price_per_piece" : product.price_db,
        "item_total_price": round(product.price_db * data.quantity_sm, 2),
    }

def view_cart(request :Request,db: Session, current_user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == current_user.id_db).first()
    if not cart:
        return {"items": [], "item_count": 0, "grand_total": 0.0, "vat": 0.0, "final_total": 0.0, "message": "ตะกร้าสินค้าของคุณว่างเปล่า"}
    cart_items = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).all()
    if not cart_items:
        return {"cart_id": cart.id_db, "items": [], "item_count": 0, "grand_total": 0.0, "vat": 0.0, "final_total": 0.0, "message": "ตะกร้าสินค้าของคุณว่างเปล่า"}
    items_detail = []
    grand_total = 0.0
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        base_url  = str(request.base_url).rstrip("/")
        image_url = f"{base_url}{product.image_db}" if product.image_db else None
        if product:
            item_total    = round(item.quantity_db * product.price_db, 2)
            grand_total  += item_total
            items_detail.append({
                "product_id"      : product.id_db,
                "product_name"    : product.name_db,
                "image_url" : image_url,
                "price" : product.price_db,
                "price_label"     : _price_label(product.price_db, product.price_type_db),            
                "quantity"        : item.quantity_db,
                "item_total_price": item_total,
        })
    vat = round(grand_total*0.07,2)
    final_total = round(grand_total+vat,2)
    return {
        "cart_id"    : cart.id_db,
        "items"      : items_detail,
        "item_count" : len(items_detail),
        "grand_total": round(grand_total, 2),
        "vat"        : vat,
        "final_total": final_total,
        "message"    : "ดึงข้อมูลตะกร้าสินค้าเรียบร้อยแล้ว",
    }

def delete_cart_item(uuid_product: UUID, db: Session, current_user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == current_user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบตะกร้าสินค้า")
    cart_item = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db, CartItemDATABASE.product_id_db == uuid_product).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้านี้ในตะกร้าของคุณ")
    db.delete(cart_item)
    db.commit()
    return {"message": "ลบสินค้าออกจากตะกร้าเรียบร้อยแล้ว"}

def clear_cart(db: Session, current_user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == current_user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบตะกร้าสินค้า")
    deleted_count = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).delete(synchronize_session=False)#ลบออกจากdatabaseเลย
    db.commit()
    return {"message":"ล้างตะกร้าสินค้าเรียบร้อยแล้ว"}