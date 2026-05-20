from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status
from Database.model import UserDATABASE, OrderDATABASE, OrderItemDATABASE, ProductDATABASE
from uuid import UUID
from datetime import datetime
from typing import Optional
from schemas import AdminOrder

def get_all_user( db: Session, search: Optional[UUID] = None):
    user = db.query(UserDATABASE)
    if search:
        user = user.filter(UserDATABASE.id_db == search)
    users = user.all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบผู้ใช้")
    return {"total":len(users), "users": users}

def delete_user(user_id:UUID, db:Session):
    user = db.query(UserDATABASE).filter(UserDATABASE.id_db == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบผู้ใช้นี้")
    if user.role_db == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ไม่สามารถลบแอดมินได้นะจ๊ะ")
    username = user.username_db
    db.delete(user)
    db.commit()
    return {"message":f"ลบผู้ใช้ {username} ออกจากระบบแล้ว"}

def search_orders(db: Session, page: int = 1, limit: int = 20):
    leng = db.query(OrderDATABASE)
    total = leng.count()
    skip = (page - 1)*limit
    orders = leng.order_by(OrderDATABASE.create_at.desc()).offset(skip).limit(limit).all() #desc คือมากไปน้อยหรือก็คือเรียงเวลาล่าสุดนั่นแหละ(create_at) order_by คือจัดเรียงข้อมูล
    if not orders:
        return {"orders": [], "message": "ไม่พบบิลที่ตรงกับเงื่อนไข"}
    result = []
    for o in orders:
        items = db.query(OrderItemDATABASE).filter(OrderItemDATABASE.order_id_db == o.id_db).all()
        items_detail = []
        for item in items:
            product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == item.product_id_db).first()
            items_detail.append({
                "product_name"   : product.name_db if product else "ถูกลบออกจากระบบแล้ว",
                "quantity"       : item.quantity_db,
                "price_per_piece": item.price_per_piece_db,
            })
        result.append({
            "order_id"   : o.id_db,
            "created_at" : o.create_at,
            "total_price": o.total_price,
            "items"      : items_detail
        })
 
    return {"total":total ,"page":page,"limit":limit,"total_pages": -(-total//limit),
            "orders": result}

def get_sale_static(db:Session):
    total_priceeeeee = db.query(func.sum(OrderDATABASE.total_price)).scalar()# ได้ค่าเดียวโดดๆ มักใช้คู่กับพวกคิดเลขของ database 
    if total_priceeeeee is None:
        total_priceeeeee = 0.0
    total_orderrrrrr = db.query(func.count(OrderDATABASE.id_db)).scalar()
    if total_orderrrrrr is None:
        total_orderrrrrr = 0
    best_product = (db.query(ProductDATABASE.name_db, func.sum(OrderItemDATABASE.quantity_db).label("total_sold")) #หาชื่อสินค้าและผลรวมของที่ขายได้
                    .join(OrderItemDATABASE, ProductDATABASE.id_db == OrderItemDATABASE.product_id_db) #คือการนำมาจับคู่กันระหว่าง product และ orderitem โดยเช็คว่ารหัสสินค้าทั้ง 2 ต้องตรงกัน จะได้เห็นทั้งชื่อและจำนวนที่ขายคู่กัน
                    .group_by(ProductDATABASE.id_db) #AIบอกว่า ลองนึกภาพบิล 1,000 ใบที่มีแอปเปิล ส้ม กล้วย ปนกันมั่วไปหมด... ถ้าเราไม่ใช้บรรทัดนี้ func.sum ในสเต็ป 1 จะเอาจำนวนผลไม้ทุกชนิดบวกกันเป็นก้อนเดียวเลย!
                    .order_by(desc("total_sold")) #เรียงยอดขายจากม้ากไปน้อย
                    .limit(5) #โชว์แค่ 5 อัน
                    .all()) 
    top_product =[]
    for name_fruitttt, total_sold in best_product:
        top_product.append({"product_name": name_fruitttt,
                            "total_sold": total_sold})
    return {"total_price": total_priceeeeee,
            "total_order": total_orderrrrrr,
            "top5": top_product}