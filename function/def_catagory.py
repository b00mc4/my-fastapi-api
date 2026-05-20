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

def create_catagory(data: CatagoryCreate, db: Session):
    oldcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.name_db == data.name_sm).first()
    if oldcatagory:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="มีหมวดหมู่นี้แล้ว")
    newcatagory = CatagoryDATABASE(name_db = data.name_sm)
    db.add(newcatagory)
    db.commit()
    return {"message":"สร้างหมวดหมู่สำเร็จ", "catagory_name":newcatagory.name_db}

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
    image = str(request.base_url).rstrip("/")
    if catagory.image_db:
        image_url = f"{image}{catagory.image_db}"
    else:
        image_url = None 
    return {
        "catagory_name": catagory.name_db,
        "products": [{
                "name": p.name_db,
                "price": p.price_db,
                "image_url": image_url,}
            for p in catagory.products]
            }

def update_catagory(uuid_catagory:UUID,data:CatagoryUpdate, db: Session):
    upcatagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
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
    if catagory.image_db:
        _delete_catagory_file(catagory.image_db)
    db.delete(catagory)
    db.commit()
    return {"messege":f"ลบหมวดหมู่ {catagory.name_db} สำเร็จแล้ว"}

#====================================================================================================================

def upload_catagory_image(uuid_catagory: UUID,request:Request, file:UploadFile, db: Session):
    catagory =db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่พบสินค้า")
    if catagory.image_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="หมวดหมู่นี้มีรูปภาพอยู่แล้ว กรุณาใช้ PUT /image เพื่ออัปเดตรูปภาพ")
    allowed_types = ["image/jpeg","image/png","image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ไม่รองรับไฟล์นี้")
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
    return {"message":"อัพโหลดรูปภาพสำเร็จ","image_url": full_url}

def update_catagory_image(uuid_catagory: UUID,request: Request ,file: UploadFile, db: Session):
    catagory = db.query(CatagoryDATABASE).filter(CatagoryDATABASE.id_db == uuid_catagory).first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบสินค้า")
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="ไม่รองรับไฟล์นี้")
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
    return {"message": "อัปเดตรูปภาพสำเร็จ", "image_url": full_url}

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