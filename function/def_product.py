import os
from sqlalchemy.orm import Session
import shutil
from Database.model import CatagoryDATABASE, ProductDATABASE
from schemas import CatagoryCreate, ProductCreate, CatagoryUpdate, ProductUpdate, ProductSearch
from fastapi import HTTPException, status, UploadFile
from uuid import UUID
from typing import Optional

UPLOAD_DIR = "static/image"
os.makedirs(UPLOAD_DIR, exist_ok=True) #เป็นการสร้าง folder ถ้า True หมายถึงว่าถ้ามีโฟลเดออยู่แล้ว

#====================================================================================================
def create_catagory(data: CatagoryCreate, db: Session):
    oldcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.name_db == data.name_sm).first()
    if oldcatagory:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีหมวดหมู่นี้แล้ว")
    newcatagory = CatagoryDATABASE(name_db = data.name_sm)
    db.add(newcatagory)
    db.commit()
    return {"message":"สร้างหมวดหมู่สำเร็จ", "catagory_name":newcatagory.name_db}

def all_catagory(db:Session, search: Optional[str]=None):
    name = db.query(CatagoryDATABASE)
    if search:
        name = name.filter(CatagoryDATABASE.name_db.ilike(f"%{search}%"))
    catagories = name.all()
    if not catagories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    return catagories

def search_catagory_uuid(search: UUID, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == search).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบหมวดหมู่นี้")
    return {
        "catagory_name": catagory.name_db,
        "products": [{
                "name": p.name_db,
                "price": p.price_db}
            for p in catagory.products]
            }

def update_catagory(data:CatagoryUpdate, db: Session):
    upcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == data.uuid_catagory).first()
    if not upcatagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    if data.name_sm is not None:
        upcatagory.name_db = data.name_sm
    db.commit()
    return {"message":"อัพเดทสำเร็จ"}

def delete_catagory(uuid_catagory: UUID, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    db.delete(catagory)
    db.commit()
    return {"messege":f"ลบหมวดหมู่ {catagory.name_db} สำเร็จแล้ว"}
#====================================================================================================

def create_product(data: ProductCreate, db:Session):
    oldproduct = db.query(ProductDATABASE).filter(ProductDATABASE.name_db == data.name_sm, ProductDATABASE.price_db == data.price_per_packorkilogram).first()
    if oldproduct:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีรายการนี้แล้ว")
    uuidCT = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == data.uuid_catagory).first()
    if not uuidCT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่มีหมวดหมู่นี้")
    newproduct = ProductDATABASE(catagory_id_db=data.uuid_catagory,name_db=data.name_sm,price_db=data.price_per_packorkilogram)
    db.add(newproduct)
    db.commit()
    return {"message":"สร้างProductเรียบร้อย"}

def all_product(db:Session, search: Optional[str] = None):
    name = db.query(ProductDATABASE)
    if search:
        name = name.filter(ProductDATABASE.name_db.ilike(f"%{search}%"))
    products = name.all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้านี้")
    return products

def search_product(data: UUID, db: Session):
    products = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == data).first()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบหมวดหมู่นี้") 
    return {
            "uuid_product": products.id_db,             
            "uuid_catagory": products.catagory_id_db,
            "name_catagory": products.catagorys.name_db,
            "name_Product": products.name_db,
            "price": products.price_db,
            "image_url": products.image_db
        }

def update_product(data: ProductUpdate, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == data.uuid_product).first()
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
    db.delete(product)
    db.commit()
    return {"message":f"ลบสินค้า {product.name_db} สำเร็จแล้ว"}

#===============================================================================================================

def upload_product_image(uuid_product: UUID, file:UploadFile, db: Session):
    product =db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้า")
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
    product.image_db = file_path
    db.commit()
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": file_path}

def update_product_image(uuid_product: UUID, file: UploadFile, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="ไม่รองรับไฟล์นี้")
    if product.image_db and os.path.exists(product.image_db):
        os.remove(product.image_db)
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid_product}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="เกิดข้อผิดพลาดในการอัปโหลด")
    product.image_db = file_path
    db.commit()
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": file_path}

def delete_product_image(uuid_product: UUID, db: Session):
    product = db.query(ProductDATABASE).filter(ProductDATABASE.id_db == uuid_product).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    if not product.image_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="สินค้านี้ยังไม่มีรูปภาพ")
    if os.path.exists(product.image_db):
        os.remove(product.image_db)
    product.image_db = None
    db.commit()
    return {"message": "ลบรูปภาพสำเร็จ"}

#====================================================================================================================

def upload_catagory_image(uuid_catagory: UUID, file:UploadFile, db: Session):
    catagory =db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg","image/png","image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่รองรับไฟล์นี้")
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid_catagory}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="เกิดข้อผิดพลาด")
    catagory.image_db = file_path
    db.commit()
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": file_path}

def update_catagory_image(uuid_catagory: UUID, file: UploadFile, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="ไม่รองรับไฟล์นี้")
    if catagory.image_db and os.path.exists(catagory.image_db):
        os.remove(catagory.image_db)
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid_catagory}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="เกิดข้อผิดพลาดในการอัปโหลด")
    catagory.image_db = file_path
    db.commit()
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": file_path}

def delete_catagory_image(uuid_catagory: UUID, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    if not catagory.image_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="สินค้านี้ยังไม่มีรูปภาพ")
    if os.path.exists(catagory.image_db):
        os.remove(catagory.image_db)
    catagory.image_db = None
    db.commit()
    return {"message": "ลบรูปภาพสำเร็จ"}