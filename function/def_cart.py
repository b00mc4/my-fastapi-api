from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from Database.model import ProductDATABASE, CartUserDATABASE, CartItemDATABASE, UserDATABASE
from schemas import SaiCart
from uuid import UUID
from typing import Optional

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
    
def add_product(data: SaiCart, db: Session, product: ProductDATABASE, cart: CartUserDATABASE):
    cart_item = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db, CartItemDATABASE.product_id_db == data.uuid_product).first()
    if cart_item:
        new_quantity = cart_item.quantity_db + data.quantity_sm
        cart_item.quantity_db = new_quantity
    else:
        new_cart_item = CartItemDATABASE(cart_id_db=cart.id_db, product_id_db=data.uuid_product, quantity_db=data.quantity_sm)
        db.add(new_cart_item)
    db.commit()
    return {"message": f"หยิบ {product.name_db} จำนวน {data.quantity_sm} ชิ้น ลงตะกร้าเรียบร้อยแล้ว"}

def add_to_cart_main(data: SaiCart, db: Session, current_user: UserDATABASE):
    product = get_product(data, db)
    cart = get_cart(db, current_user)
    return add_product(data, db, product, cart)

def edit_quantity(data: SaiCart, db:Session, user:UserDATABASE ):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == user.id_db).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="คุณยังไม่มีตะกร้าสินค้า")
    cart_item = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db==cart.id_db, CartItemDATABASE.product_id_db == data.uuid_product).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้านี้ในตะกร้าของคุณ")
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == data.uuid_product).first()
    cart_item.quantity_db = data.quantity_sm
    db.commit()
    return {"message": f"อัปเดตจำนวนสินค้าเป็น {data.quantity_sm} ชิ้น เรียบร้อยแล้ว"}

def view_cart(db: Session, current_user: UserDATABASE):
    cart = db.query(CartUserDATABASE).filter(CartUserDATABASE.user_id_db == current_user.id_db).first()
    if not cart:
        return {"items": [], "grand_total": 0.0, "message": "คุณไม่มีตะกร้า"}
    cart_items = db.query(CartItemDATABASE).filter(CartItemDATABASE.cart_id_db == cart.id_db).all()
    if not cart_items:
         return {"items": [], "grand_total": 0.0, "message": "ตะกร้าสินค้าของคุณว่างเปล่า"}
    items_detail = []
    grand_total = 0.0
    for item in cart_items:
        product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
        if product:
            item_total_price = item.quantity_db * product.price_db
            grand_total += item_total_price
            vat = round(grand_total*0.07,2)
            vat_total = round(grand_total+vat,2)
            items_detail.append({
                "product_id": product.id_db,
                "product_name": product.name_db,
                "price_per_piece": product.price_db,
                "quantity": item.quantity_db,
                "item_total_price": item_total_price
            })
    return {
        "cart_id": cart.id_db,
        "items": items_detail,
        "grand_total": grand_total,
        "final_total": vat_total,
        "message": "ดึงข้อมูลตะกร้าสินค้าเรียบร้อยแล้ว"
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