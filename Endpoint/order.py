from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from Database.database import get_db
from Database.model import UserDATABASE
from function import def_order
from function.def_auth import get_current_regular_user
from schemas import (
    OrderSearch, SelectiveCheckout,
    CheckoutResponse, OrderListResponse,
)
from uuid import UUID

router = APIRouter(prefix="/order", tags=["Order"])

@router.post("/checkout", status_code=201, summary="จ่ายเงินทั้งตะกร้า",response_model=CheckoutResponse)
def checkout(db: Session = Depends(get_db),current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.checkout_cart(db, current_user)

@router.post("/checkout/selective", status_code=201, summary="จ่ายเงินเฉพาะสินค้าที่เลือก", response_model=CheckoutResponse)
def checkout_selective(body: SelectiveCheckout,db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.checkout_selective(body, db, current_user)

@router.get("", status_code=200, summary="ค้นหาบิลของชั้นทั้งหมด", response_model=OrderListResponse)
def my_all_orders(request:Request, db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.all_orders(request,db, current_user)

@router.get("/search", summary="ค้นหาบิล(วันที่)",response_model=OrderListResponse)
def my_name_orders( request : Request ,body: OrderSearch = Depends(),db: Session = Depends(get_db),current_user: UserDATABASE = Depends(get_current_regular_user)):
    """"เวลาค้นหา ให้ค้นหาโดยใช้ yyyy-mm-dd นะจ๊ะคนดีของชั้น"""
    return def_order.search_my_orders(request,body ,db, current_user)

@router.get("/{uuid_orders}", summary="ค้นหาบิล(UUID)",response_model=OrderListResponse)
def my_uuid_orders(uuid_orders: UUID,request:Request,db: Session = Depends(get_db),current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_order.search_order_uuid(uuid_orders,request ,db, current_user)