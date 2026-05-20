from pydantic import Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from Database.database import get_db
from Database.model import UserDATABASE
from schemas import SaiCart,Quantity
from function import def_cart
from function.def_auth import get_current_regular_user
from typing import Annotated

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("", summary="ดูตะกร้าสินค้าของฉัน")
def view_my_cart(db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_cart.view_cart(db, current_user)

@router.post("/items", status_code=201, summary="หยิบสินค้าใส่ตะกร้า")
def add_product_to_cart(body: SaiCart , db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_cart.add_to_cart_main(body, db, current_user)

@router.put("/items/{uuid_product}", summary="แก้ไขจำนวนสินค้าในตะกร้า")
def update_quantity(uuid_product:UUID, body :Quantity, db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_cart.edit_quantity(uuid_product,body, db, current_user)

@router.delete("/items/{uuid_product}", summary="ลบสินค้าชิ้นนี้ออกจากตะกร้า")
def delete_item(uuid_product: UUID, db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_cart.delete_cart_item(uuid_product, db, current_user)

@router.delete("", summary="ล้างตะกร้าสินค้าทั้งหมด")
def clear_all_cart(db: Session = Depends(get_db), current_user: UserDATABASE = Depends(get_current_regular_user)):
    return def_cart.clear_cart(db, current_user)