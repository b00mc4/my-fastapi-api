import os
from sqlalchemy.orm import Session
import shutil
from Database.model import CatagoryDATABASE
from schemas import CatagoryCreate, CatagoryUpdate
from fastapi import HTTPException, status, UploadFile,Request
from uuid import UUID
from typing import Optional
from fastapi import Request

UPLOAD_CIR = "Catagory/image"
os.makedirs(UPLOAD_CIR, exist_ok=True)

def _delete_catagory_file(image_url: str):
    """รับ URL ที่เก็บใน DB แล้วแปลงเป็น path จริงบน disk แล้วลบ"""
    filename = image_url.removeprefix("/images/categories/")
    file_path = os.path.join(UPLOAD_CIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

def _price_label(price: float, price_type: str) -> str:
    """สร้าง label ราคาให้ frontend ใช้แสดงผล เช่น '฿25.00 / แพ็ค'"""
    unit = "แพ็ค" if price_type == "pack" else "กิโล"
    return f"฿{price:,.2f} / {unit}"

#=================================================================================================================================================

def create_catagory(data: CatagoryCreate, db: Session):
    oldcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.name_db == data.name_sm).first()
    if oldcatagory:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีหมวดหมู่นี้แล้ว")
    newcatagory = CatagoryDATABASE(name_db = data.name_sm)
    db.add(newcatagory)
    db.commit()
    return {"message": "สร้างหมวดหมู่สำเร็จ", "uuid_catagory": newcatagory.id_db,"catagory_name": newcatagory.name_db}

def all_catagory(request:Request, db:Session, search: Optional[str]=None):
    name = db.query(CatagoryDATABASE)
    if search:
        name = name.filter(CatagoryDATABASE.name_db.ilike(f"%{search}%"))
    catagories = name.all()
    if not catagories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    image = str(request.base_url).rstrip("/")
    result = []
    for p in catagories:
        if p.image_db:
            image_url = f"{image}{p.image_db}"
        else:
            image_url = None
        result.append({
            "uuid_catagory": p.id_db,
            "name": p.name_db,
            "image_url": image_url,
        })
    
    return result

def search_catagory_uuid(search: UUID,request:Request, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == search).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบหมวดหมู่นี้")
    base = str(request.base_url).rstrip("/")
    cat_image = f"{base}{catagory.image_db}" if catagory.image_db else None
    products = []
    for p in catagory.products:
        p_image = f"{base}{p.image_db}" if p.image_db else None
        products.append({
            "uuid_product": p.id_db,
            "name"        : p.name_db,
            "price"       : p.price_db,
            "price_type"  : p.price_type_db,
            "price_label" : _price_label(p.price_db, p.price_type_db),
            "pack_size"   : p.pack_size_db,
            "stock"       : p.stock_db,
            "image_url"   : p_image,
        })
    return {
        "uuid_catagory" : catagory.id_db,
        "catagory_name" : catagory.name_db,
        "image_url"     : cat_image,
        "total_products": len(products),
        "products"      : products,
    }

def update_catagory(uuid_catagory:UUID,data:CatagoryUpdate, db: Session):
    upcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not upcatagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    if data.name_sm is not None:
        upcatagory.name_db = data.name_sm
    db.commit()
    return {"message":"อัพเดทสำเร็จ","uuid_catagory":upcatagory.id_db}

def delete_catagory(uuid_catagory: UUID, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบหมวดหมู่นี้")
    if catagory.image_db:
        _delete_catagory_file(catagory.image_db)
    db.delete(catagory)
    db.commit()
    return {"message":f"ลบหมวดหมู่ {catagory.name_db} สำเร็จแล้ว"}

#====================================================================================================================

def upload_catagory_image(uuid_catagory: UUID,request:Request, file:UploadFile, db: Session):
    catagory =db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้า")
    if catagory.image_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="หมวดหมู่นี้มีรูปภาพอยู่แล้ว กรุณาใช้ PUT /image เพื่ออัปเดตรูปภาพ")
    allowed_types = ["image/jpeg","image/png","image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ไฟล์ '{file.content_type}' ไม่รองรับ กรุณาใช้ {', '.join(allowed_types)} เท่านั้น")
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid_catagory}.{file_extension}"
    file_path = os.path.join(UPLOAD_CIR, new_filename)
    try:
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="เกิดข้อผิดพลาด")
    catagory.image_db = f"/images/categories/{new_filename}"
    db.commit()
    full_url = f"{request.base_url}images/categories/{new_filename}"
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": full_url,"uuid_catagory":catagory.id_db}

def update_catagory_image(uuid_catagory: UUID,request: Request ,file: UploadFile, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"ไฟล์ '{file.content_type}' ไม่รองรับ กรุณาใช้ {', '.join(allowed_types)} เท่านั้น")
    if catagory.image_db:
        _delete_catagory_file(catagory.image_db)
    file_extension = file.filename.split(".")[-1].lower()
    new_filename = f"{uuid_catagory}.{file_extension}"
    file_path = os.path.join(UPLOAD_CIR, new_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="เกิดข้อผิดพลาดในการอัปโหลด")
    catagory.image_db = f"/images/categories/{new_filename}"
    db.commit()
    full_url = f"{request.base_url}images/categories/{new_filename}"
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": full_url,"uuid_catagory":catagory.id_db}

def delete_catagory_image(uuid_catagory: UUID, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    if not catagory.image_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="สินค้านี้ยังไม่มีรูปภาพ")
    _delete_catagory_file(catagory.image_db)
    catagory.image_db = None
    db.commit()
    return {"message": "ลบรูปภาพสำเร็จ"}