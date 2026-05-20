from fastapi import APIRouter, Depends, UploadFile, File, Request
from fastapi.responses import FileResponse
from schemas import CatagoryCreate, CatagoryUpdate
from sqlalchemy.orm import Session
from Database.database import get_db
from function import def_catagory
from uuid import UUID
from Database.model import UserDATABASE
from function.def_auth import get_current_admin,get_current_user
from typing import Optional

router = APIRouter(prefix="/catagories",tags=["Catagory"])

@router.post("",status_code=201,summary="สร้างหมวดหมู่")
def createcatagory(body: CatagoryCreate, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_catagory.create_catagory(body,db)

@router.get("", summary="หมวดหมู่ทั้งหมด")
def allcatagory(request:Request, db:Session = Depends(get_db),name: Optional[str]=None,current: UserDATABASE = Depends(get_current_user)):
    """ค้นหาหมวดหมู่ได้จากการพิมพ์ชื่อหมวดหมู่ หรือถ้าไม่พิมพ์ก็จะแสดงทั้งหมด"""
    return def_catagory.all_catagory(request,db,name)

@router.get("/{uuid_catagory}",summary="ค้นหาหมวดหมู่(UUID)")
def allcatagorys(uuid_catagory: UUID,request:Request ,db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_user)):
    """ค้นหาด้วย UUID เท่านั้น อันนี้ก็จะแสดง product ด้วย"""
    return def_catagory.search_catagory_uuid(uuid_catagory,request,db)

@router.put("/{uuid_catagory}",status_code=200,summary="เปลี่ยนข้อมูลหมวดหมู่")
def updatecatagory(uuid_catagory:UUID,body: CatagoryUpdate , db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_catagory.update_catagory(uuid_catagory,body,db)

@router.delete("/{uuid_catagory}",status_code=200,summary="ลบหมวดหมู่")
def deletecatagory(uuid_catagory:UUID, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_catagory.delete_catagory(uuid_catagory,db)

@router.post("/{uuid_catagory}/image", summary="อัปโหลดรูปภาพหมวดหมู่")
def upload_image(uuid_catagory: UUID,request:Request ,file: UploadFile = File(...),db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin) ):
    return def_catagory.upload_catagory_image(uuid_catagory,request ,file, db)

@router.put("/{uuid_catagory}/image", summary="อัปเดตรูปภาพหมวดหมู่")
def update_image(uuid_catagory: UUID,request:Request,file: UploadFile = File(...),db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_catagory.update_catagory_image(uuid_catagory,request ,file, db)

@router.delete("/{uuid_catagory}/image", summary="ลบรูปภาพหมวดหมู่")
def delete_image(uuid_catagory: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_catagory.delete_catagory_image(uuid_catagory, db)