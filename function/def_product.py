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

def _price_label(price: float, price_type: str):
    unit = "แพ็ค" if price_type == "pack" else "กิโล"
    return f"฿{price:,.2f} / {unit}"
#====================================================================================================

def create_product(data: ProductCreate, db:Session):
    oldproduct = db.query(ProductDATABASE).filter(ProductDATABASE.name_db == data.name_sm, ProductDATABASE.catagory_id_db == data.uuid_catagory).first()
    if oldproduct:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีรายการนี้แล้ว")
    uuidCT = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == data.uuid_catagory).first()
    if not uuidCT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่มีหมวดหมู่นี้")
    newproduct = ProductDATABASE(
        catagory_id_db = data.uuid_catagory,
        name_db        = data.name_sm,
        price_db       = data.price,
        price_type_db  = data.price_type,
        pack_size_db   = data.pack_size,
        stock_db       = data.stock,
    )
    db.add(newproduct)
    db.commit()
    db.refresh(newproduct)
    return {
        "message"    : "สร้างสินค้าสำเร็จ",
        "uuid_product": newproduct.id_db,
        "name"       : newproduct.name_db,
        "price"      : newproduct.price_db,
        "price_type" : newproduct.price_type_db,
        "price_label": _price_label(newproduct.price_db, newproduct.price_type_db),
        "pack_size"  : newproduct.pack_size_db,
        "stock"      : newproduct.stock_db,
    }

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
            "name_catagory" : p.catagorys.name_db,
            "name_product": p.name_db,  
            "price": p.price_db,
            "price_type"   : p.price_type_db,
            "price_label"  : _price_label(p.price_db, p.price_type_db),
            "pack_size"    : p.pack_size_db,
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
            "name_product": products.name_db,
            "price": products.price_db,
            "price_type"   : products.price_type_db,
            "price_label"  : _price_label(products.price_db, products.price_type_db),
            "pack_size"    : products.pack_size_db,
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
        "uuid_product" : product.id_db,
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
    if data.price is not None:
        product.price_db = data.price
    if data.price_type is not None:
        product.price_type_db = data.price_type
    if data.pack_size is not None:
        product.pack_size_db = data.pack_size
    db.commit()
    return {"message":"อัปเดตสินค้าสำเร็จ", "uuid_product":product.id_db}

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ไฟล์ '{file.content_type}' ไม่รองรับ กรุณาใช้ {', '.join(allowed_types)} เท่านั้น")
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
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": full_url,"uuid_product":product.id_db}

def update_product_image(uuid_product: UUID, request: Request, file: UploadFile, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"ไฟล์ '{file.content_type}' ไม่รองรับ กรุณาใช้ {', '.join(allowed_types)} เท่านั้น")
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
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": full_url,"uuid_product":product.id_db}

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