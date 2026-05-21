from pydantic import BaseModel, EmailStr,field_validator,Field
import re
from uuid import UUID
from typing import Optional, Annotated, List,Literal
from datetime import date

_SPECIAL_CHARS_PATTERN = re.compile(r"[!@#$%^&*()_+=\[\]{};':\"\\|,.<>/?`~]")

class UserRegister(BaseModel):
    username : str
    email : EmailStr
    password : str
    password_confirm : str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value:str):
        if _SPECIAL_CHARS_PATTERN.search(value):
            raise ValueError("ห้ามมีอักขระพิเศษ")
        word = value.strip()
        if len(word)<4:
            raise ValueError("กรุณากรอกจำนวน4ตัวอักษรขึ้นไป")
        return value
    
class ChangePassword(BaseModel):
    oldpassword_sm : str
    newpassword_sm : str
    confirm_newpassword_sm :str

class ForgotPassword(BaseModel):
    email : EmailStr

class ResetPassword(BaseModel):
    otp_sm : str
    newpassword_sm : str
    confirm_newpassword_sm : str

class CatagoryCreate(BaseModel):
    name_sm:str

class ProductCreate(BaseModel):
    uuid_catagory : UUID = None
    name_sm : str
    price : Optional[Annotated[float, Field(gt=0)]]
    price_type : Literal["pack", "kilo"] = "kilo"
    pack_size : Optional[Annotated[int, Field(gt=0)]] = None
    stock : Annotated[int, Field(ge=0)] = 0
    
class CatagoryUpdate(BaseModel):
    name_sm : str

class ProductUpdate(BaseModel):
    uuid_catagory : Optional[UUID] = None
    name_sm : Optional[str] = None
    price : Optional[Annotated[float, Field(gt=0)]] = None
    price_type : Optional[Literal["pack", "kilo"]] = None
    pack_size : Optional[Annotated[int, Field(gt=0)]] = None

class CatagorySearch(BaseModel):
    name_catagory : Optional[str] = None
    uuid_catagory : Optional[UUID] = None

class ProductSearch(BaseModel):
    uuid_product : Optional[UUID] = None
    name_sm : Optional[str] = None

class SaiCart(BaseModel):
    uuid_product : UUID
    quantity : Annotated[int, Field(ge=1)]

class OrderSearch(BaseModel):   
    start_date   : Optional[date] = None
    end_date     : Optional[date] = None

class AdminOrder(BaseModel):
    user_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_price   : Optional[Annotated[float, Field(ge=0)]] = None   
    max_price   : Optional[Annotated[float, Field(ge=0)]] = None  

class StockAdjust(BaseModel):
    amount : Annotated[int, Field(ge=1)]

class Quantity(BaseModel):
    quantity_sm : Annotated[int, Field(ge=1)]

class SelectiveCheckout(BaseModel):
    product_ids : List[UUID] = Field(..., min_length=1, description="ระบุ UUID ของสินค้าในตะกร้าที่ต้องการจ่ายเงิน")

# ============================================================================================================================
 
class TokenResponse(BaseModel):
    access_token : str
    token_type : str
 
class MeResponse(BaseModel):
    message : str
    username : str
    email : str
    role : str
 
# ── Simple generic responses ─────────────────
class SimpleMessage(BaseModel):
    """ใช้สำหรับ endpoint ที่ return แค่ message เดียว"""
    message : str
 
# ── Category responses ──────────────────────
class CategoryCreatedResponse(BaseModel):
    message : str
    uuid_catagory : UUID
    catagory_name : str
 
class CategoryItem(BaseModel):
    uuid_catagory : UUID
    name : str
    image_url : Optional[str] = None
 
class ProductInCategory(BaseModel):
    uuid_product : UUID
    name : str
    price : float
    price_type : str
    price_label : str
    pack_size : Optional[int] = None
    stock : int
    image_url : Optional[str] = None
 
class CategoryDetailResponse(BaseModel):
    uuid_catagory : UUID
    catagory_name : str
    image_url : Optional[str] = None
    total_products : int
    products : List[ProductInCategory]
 
class CategoryUpdateResponse(BaseModel):
    message : str
    uuid_catagory : UUID
 
# ── Product responses ────────────────────────
class ProductCreatedResponse(BaseModel):
    message : str
    uuid_product : UUID
    name : str
    price : float
    price_type : str
    price_label : str
    pack_size : Optional[int] = None
    stock : int
 
class ProductItem(BaseModel):
    uuid_product : UUID
    uuid_catagory : UUID
    name_catagory : str
    name_product : str
    price : float
    price_type : str
    price_label : str
    pack_size : Optional[int] = None
    stock : int
    image_url : Optional[str] = None
 
class ProductUpdateResponse(BaseModel):
    message : str
    uuid_product : UUID
 
class StockResponse(BaseModel):
    message : str
    uuid_product : UUID
    stock : int
 
class ImageResponseCATAGORY(BaseModel):
    message : str
    image_url : str
    uuid_catagory : UUID
 
class ImageResponsePRODUCT(BaseModel):
    message : str
    image_url : str
    uuid_product : UUID
 
# ── Cart responses ───────────────────────────
class CartItemDetail(BaseModel):
    product_id : UUID
    product_name : str
    image_url : Optional[str] = None
    price : float
    price_label : str
    quantity : int
    item_total_price : float

class CartResponse(BaseModel):
    cart_id : Optional[UUID] = None
    items : List[CartItemDetail]
    item_count : int
    grand_total : float
    vat : float
    final_total : float
    message : str
 
class AddToCartResponse(BaseModel):
    message : str
    product_id : UUID
    product_name : str
    quantity_added : int
    quantity_in_cart : int
    price : float
    total_price : float
    price_label : str
 
class UpdateQuantityResponse(BaseModel):
    message : str
    product_id : UUID
    product_name : str
    new_quantity : int
    price_per_piece : float
    item_total_price : float
 
# ── Order responses ──────────────────────────
class OrderItemDetail(BaseModel):
    product_name : str
    image_url : Optional[str] = None
    quantity : int
    price_per_piece : float
    subtotal : float
 
class CheckoutResponse(BaseModel):
    message : str
    order_id : UUID
    items_purchased : int
    items : List[dict]
    price_before_vat : float
    vat_7_percent : float
    final_price : float
    items_remaining_in_cart : int
 
class OrderSummary(BaseModel):
    order_id : UUID
    created_at : str
    total_price : float
    items : List[dict]
 
class OrderListResponse(BaseModel):
    total : int
    orders : List[OrderSummary]
 
# ── Admin responses ──────────────────────────
class UserAdminView(BaseModel):
    uuid : UUID
    username : str
    email : str
    role : str
    total_orders : int
    total_spent : float
 
class AdminUserListResponse(BaseModel):
    total : int
    users : List[UserAdminView]
 
class TopProduct(BaseModel):
    product_name : str
    total_sold : int
 
class SaleStaticResponse(BaseModel):
    total_revenue : float
    total_orders : int
    average_order : float
    top5_products : List[TopProduct]
 
# ── Legacy (ใช้ใน catagory PUT) ──────────────
class MessageResponse(BaseModel):
    message : str
    uuid_catagory : UUID