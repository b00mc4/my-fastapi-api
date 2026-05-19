from fastapi import APIRouter, Depends, UploadFile, File
from schemas import CatagoryCreate,ProductCreate, CatagoryUpdate, ProductUpdate, ProductSearch, CatagorySearch
from sqlalchemy.orm import Session
from Database.database import get_db
from function import def_product
from uuid import UUID
from Database.model import UserDATABASE
from function.def_auth import get_current_admin,get_current_user
from typing import Optional

router = APIRouter(prefix="/catagory",tags=["Catagory and Product"])

#=============================================================================================================
@router.post("",status_code=201,summary="สร้างหมวดหมู่")
def createcatagory(body: CatagoryCreate, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.create_catagory(body,db)

@router.post("/products",status_code=201,summary="สร้างสินค้า")
def createproduct(body: ProductCreate, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.create_product(body,db)

@router.get("", summary="หมวดหมู่ทั้งหมด")
def allcatagory(db:Session = Depends(get_db),name: Optional[str]=None,current: UserDATABASE = Depends(get_current_user)):
    """ค้นหาหมวดหมู่ได้จากการพิมพ์ชื่อหมวดหมู่ หรือถ้าไม่พิมพ์ก็จะแสดงทั้งหมด"""
    return def_product.all_catagory(db,name)

@router.get("/products", summary="สินค้าทั้งหมด")
def allproduct(db:Session = Depends(get_db),name: Optional[str]=None ,current: UserDATABASE = Depends(get_current_user)):
    return def_product.all_product(db,name)

#==========================================================================================================================

@router.get("/{uuid_catagory}",summary="ค้นหาหมวดหมู่(UUID)")
def allcatagorys(uuid_catagory: UUID , db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_user)):
    """ค้นหาด้วย UUID เท่านั้น อันนี้ก็จะแสดง product ด้วย"""
    return def_product.search_catagory_uuid(uuid_catagory,db)

@router.put("/{uuid_catagory}",status_code=201,summary="เปลี่ยนข้อมูลหมวดหมู่")
def updatecatagory(body: CatagoryUpdate = Depends(), db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_catagory(body,db)

@router.delete("/{uuid_catagory}",status_code=201,summary="ลบหมวดหมู่")
def deletecatagory(uuid_catagory:UUID, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_catagory(uuid_catagory,db)

#=============================================================================================================

@router.post("/products",status_code=201,summary="สร้างสินค้า")
def createproduct(body: ProductCreate, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.create_product(body,db)

@router.get("/products/{uuid_product}",summary="ค้นหาสินค้า(UUID)")
def allproduct(uuid_product:UUID,db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_user)):
    return def_product.search_product(uuid_product,db)

@router.put("/products/{uuid_product}",status_code=201,summary="เปลี่ยนข้อมูลสินค้า")
def updatecatagory(body: ProductUpdate = Depends(), db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_product(body,db)

@router.delete("/products/{uuid_product}",status_code=201,summary="ลบสินค้า")
def deleteproduct(uuid_product:UUID, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_product(uuid_product,db)

#============================================================================================================================================

@router.post("/{uuid_catagory}/image", summary="อัปโหลดรูปภาพสินค้า")
def upload_image(uuid_catagory: UUID, file: UploadFile = File(...),db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin) ):
    return def_product.upload_catagory_image(uuid_catagory, file, db)

@router.put("/{uuid_catagory}/image", summary="อัปเดตรูปภาพสินค้า")
def update_image(uuid_catagory: UUID,file: UploadFile = File(...),db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_catagory_image(uuid_catagory, file, db)

@router.delete("/{uuid_catagory}/image", summary="ลบรูปภาพสินค้า")
def delete_image(uuid_catagory: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_catagory_image(uuid_catagory, db)

#============================================================================================================================

@router.post("/products/{uuid_product}/image", summary="อัปโหลดรูปภาพสินค้า")
def upload_image(uuid_product: UUID, file: UploadFile = File(...),db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin) ):
    return def_product.upload_product_image(uuid_product, file, db)

@router.put("/products/{uuid_product}/image", summary="อัปเดตรูปภาพสินค้า")
def update_image(uuid_product: UUID,file: UploadFile = File(...),db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_product_image(uuid_product, file, db)

@router.delete("/products/{uuid_product}/image", summary="ลบรูปภาพสินค้า")
def delete_image(uuid_product: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_product_image(uuid_product, db)

#=========================================================================================================================================