from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.database import get_db
from Database.model import UserDATABASE
from function.def_auth import get_current_admin
from function import def_admin
from uuid import UUID
from typing import Optional
from datetime import date
from schemas import AdminOrder

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", summary="ดูรายชื่อผู้ใช้ทั้งหมด")
def all_users(search: Optional[UUID] = None, db: Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.get_all_user(db, search)


@router.delete("/users/{user_id}", summary="ลบuserออกจากระบบ")
def delete_user(user_id: UUID,db: Session = Depends(get_db),current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.delete_user(user_id, db)

@router.get("/orders", summary="ดูออร์เดอร์ทั้งหมด")
def all_orders(body:AdminOrder = Depends(),db:Session = Depends(get_db) ,current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.search_orders(body,db)

@router.get("/static", summary="ดูสถิติทั้งหมด")
def all_static(db:Session = Depends(get_db), current: UserDATABASE = Depends(get_current_admin)):
    return def_admin.get_sale_static(db)