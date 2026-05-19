from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Database.database import get_db
from Database.model import UserDATABASE
from function import def_order
from function.def_auth import get_current_regular_user
from schemas import OrderSearch
from uuid import UUID

router = APIRouter(prefix="/order", tags=["Order"])

@router.post("/checkout", status_code=201, summary="จ่ายตังจ้า")
def checkout(db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.checkout_cart(db, current_user)

@router.get("", status_code=201, summary="ค้นหาบิลของชั้นทั้งหมด")
def checkout(db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.all_orders(db, current_user)

@router.get("/name", summary="ค้นหาบิล(ชื่อสินค้า)")
def my_orders(body: OrderSearch = Depends(),db: Session = Depends(get_db),current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.search_my_orders(body, db, current_user)

@router.get("/{uuid_orders}", summary="ค้นหาบิล(UUID)")
def my_orders(uuid_orders: UUID,db: Session = Depends(get_db),current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.search_order_uuid(uuid_orders, db, current_user)