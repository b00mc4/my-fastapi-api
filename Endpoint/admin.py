from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.database import get_db
from Database.model import UserDATABASE
from function.def_auth import get_current_admin
from function import def_admin
from uuid import UUID
from typing import Optional
from schemas import (
    AdminUserListResponse,
    SaleStaticResponse,
    SimpleMessage,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", summary="ดูรายชื่อผู้ใช้ทั้งหมด",response_model=AdminUserListResponse)
def all_users(search: Optional[str] = None, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.get_all_user(db, search)

@router.delete("/users/{user_id}", summary="ลบuserออกจากระบบ",response_model=SimpleMessage)
def delete_user(user_id: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.delete_user(user_id, db)

@router.get("/orders", summary="ดูออร์เดอร์ทั้งหมด")
def all_orders(db:Session = Depends(get_db),page: int =1,limit:int = 20 ,current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.search_orders(db,page,limit)

@router.get("/orders/{uuid_user}", summary="ดูออร์เดอร์ทั้งหมดของuser(UUID)")
def all_orders(uuid_user: UUID ,page: int = 1,limit: int = 20,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.search_orders_uuid(uuid_user,db, page, limit)

@router.get("/static", summary="ดูสถิติทั้งหมด")
def all_static(db:Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.get_sale_static(db)