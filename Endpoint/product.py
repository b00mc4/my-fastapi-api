from fastapi import APIRouter, Depends, UploadFile, File, Request 
from schemas import (
    ProductCreate, ProductUpdate, StockAdjust,
    ProductCreatedResponse, ProductItem,
    ProductUpdateResponse, StockResponse,
    ImageResponsePRODUCT, SimpleMessage,
)
from sqlalchemy.orm import Session
from Database.database import get_db
from function import def_product
from uuid import UUID
from Database.model import UserDATABASE
from function.def_auth import get_current_admin,get_current_user
from typing import Optional,List

router = APIRouter(prefix="/products",tags=["Product"])

#=============================================================================================================

@router.post("",status_code=201,summary="สร้างสินค้า",response_model=ProductCreatedResponse)
def createproduct(body: ProductCreate, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.create_product(body,db)

@router.get("", summary="สินค้าทั้งหมด",response_model=List[ProductItem])
def allproduct(request: Request,db:Session = Depends(get_db),name: Optional[str]=None ,current: UserDATABASE = Depends(get_current_user)):
    return def_product.all_product(request,db,name)

@router.get("/{uuid_product}",summary="ค้นหาสินค้า(UUID)",response_model=ProductItem)
def allproduct(uuid_product:UUID,request: Request,db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_user)):
    return def_product.search_product(uuid_product,request,db)

@router.put("/{uuid_product}",status_code=200,summary="เปลี่ยนข้อมูลสินค้า",response_model=ProductUpdateResponse)
def updatecatagory(uuid_product:UUID,body: ProductUpdate , db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_product(uuid_product,body,db)

@router.patch("/{uuid_product}/stock", summary="แก้ไข stock สินค้า",response_model=StockResponse)
def add_stock(uuid_product: UUID, body: StockAdjust, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.add_stock(uuid_product, body, db)

@router.delete("/{uuid_product}",status_code=200,summary="ลบสินค้า",response_model=SimpleMessage)
def deleteproduct(uuid_product:UUID, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_product(uuid_product,db)

#============================================================================================================================

@router.post("/{uuid_product}/image", summary="อัปโหลดรูปภาพสินค้า",response_model=ImageResponsePRODUCT)
def upload_image(uuid_product: UUID,request :Request ,file: UploadFile = File(...),db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin) ):
    return def_product.upload_product_image(uuid_product,request ,file, db)

@router.put("/{uuid_product}/image", summary="อัปเดตรูปภาพสินค้า",response_model=ImageResponsePRODUCT)
def update_image(uuid_product: UUID,request :Request ,file: UploadFile = File(...),db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.update_product_image(uuid_product,request ,file, db)

@router.delete("/{uuid_product}/image", summary="ลบรูปภาพสินค้า",response_model=SimpleMessage)
def delete_image(uuid_product: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_product.delete_product_image(uuid_product, db)

#=========================================================================================================================================