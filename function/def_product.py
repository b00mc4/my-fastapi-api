import os
from sqlalchemy.orm import Session
import shutil
from Database.model import CatagoryDATABASE, ProductDATABASE
from schemas import  ProductCreate, ProductUpdate, StockAdjust
from fastapi import HTTPException, status, UploadFile
from uuid import UUID
from typing import Optional
from fastapi import Request

UPLOAD_DIR = "static/image"
os.makedirs(UPLOAD_DIR, exist_ok=True) #เป็นการสร้าง folder ถ้า True หมายถึงว่าถ้ามีโฟลเดออยู่แล้ว

def _delete_product_file(image_url: str):
    """รับ URL ที่เก็บใน DB แล้วแปลงเป็น path จริงบน disk แล้วลบ"""
    filename = image_url.removeprefix("/images/products/")
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

#====================================================================================================

def create_product(data: ProductCreate, db:Session):
    oldproduct = db.query(ProductDATABASE).filter(ProductDATABASE.name_db == data.name_sm, ProductDATABASE.price_db == data.price_per_packorkilogram).first()
    if oldproduct:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีรายการนี้แล้ว")
    uuidCT = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == data.uuid_catagory).first()
    if not uuidCT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่มีหมวดหมู่นี้")
    newproduct = ProductDATABASE(catagory_id_db=data.uuid_catagory,name_db=data.name_sm,price_db=data.price_per_packorkilogram,stock_db = data.stock)
    db.add(newproduct)
    db.commit()
    return {"message":"สร้างProductเรียบร้อย"}

def all_product(request: Request,db:Session, search: Optional[str] = None):
    name = db.query(ProductDATABASE)
    if search:
        name = name.filter(ProductDATABASE.name_db.ilike(f"%{search}%"))
    products = name.all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้านี้")
    image = str(request.base_url).rstrip("/")
    result = []
    for p in products:
        if p.image_db:
            image_url = f"{image}{p.image_db}"
        else:
            image_url = None
        result.append({
            "uuid_product": p.id_db,
            "uuid_catagory": p.catagory_id_db,
            "name_Product": p.name_db,
            "price": p.price_db,
            "stock": p.stock_db,
            "image_url": image_url,
        })
    
    return result

def search_product(data: UUID,request: Request, db: Session):
    products = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == data).first()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้าหมู่นี้")
    image = str(request.base_url).rstrip("/")
    if products.image_db:
        image_url = f"{image}{products.image_db}"
    else:
        image_url = None 
    return {
            "uuid_product": products.id_db,             
            "uuid_catagory": products.catagory_id_db,
            "name_catagory": products.catagorys.name_db,
            "name_Product": products.name_db,
            "price": products.price_db,
            "stock"  : products.stock_db,
            "image_url": image_url
        }

def add_stock(uuid_product: UUID, data: StockAdjust, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้านี้")
    product.stock_db = data.amount
    db.commit()
    return {
        "message" : f"แก้ไข stock เป็น {data.amount} สำเร็จ",
        "product" : product.name_db,
        "stock"   : product.stock_db,
    }

def update_product(uuid_product:UUID,data: ProductUpdate, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้านี้")
    if data.name_sm is not None:
        product.name_db = data.name_sm
    if data.uuid_catagory is not None:
        product.catagory_id_db = data.uuid_catagory
    if data.price_per_packorkilogram is not None:
        product.price_db = data.price_per_packorkilogram
    db.commit()
    return {"message":"อัปเดตสินค้าสำเร็จ"}

def delete_product(uuid_product: UUID, db:Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสิ้นค้านี้")
    if product.image_db:
        _delete_product_file(product.image_db)
    db.delete(product)
    db.commit()
    return {"message":f"ลบสินค้า {product.name_db} สำเร็จแล้ว"}

#===============================================================================================================

def upload_product_image(uuid_product: UUID, request: Request, file:UploadFile, db: Session):
    product =db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้า")
    if product.image_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="สินค้านี้มีรูปภาพอยู่แล้ว กรุณาใช้ PUT /image เพื่ออัปเดตรูปภาพ")
    allowed_types = ["image/jpeg","image/png","image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่รองรับไฟล์นี้")
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid_product}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="เกิดข้อผิดพลาด")
    product.image_db = f"/images/products/{new_filename}"
    db.commit()
    full_url = f"{request.base_url}images/products/{new_filename}"
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": full_url}

def update_product_image(uuid_product: UUID, request: Request, file: UploadFile, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="ไม่รองรับไฟล์นี้")
    if product.image_db:
        _delete_product_file(product.image_db)
    file_extension = file.filename.split(".")[-1].lower()
    new_filename = f"{uuid_product}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="เกิดข้อผิดพลาดในการอัปโหลด")
    product.image_db = f"/images/products/{new_filename}"
    db.commit()
    full_url = f"{str(request.base_url)}images/products/{new_filename}"
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": full_url}

def delete_product_image(uuid_product: UUID, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    if not product.image_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="สินค้านี้ยังไม่มีรูปภาพ")
    _delete_product_file(product.image_db)
    product.image_db = None
    db.commit()
    return {"message": "ลบรูปภาพสำเร็จ"}

#===================================================================================================================