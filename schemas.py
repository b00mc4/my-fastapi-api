from pydantic import BaseModel, EmailStr,field_validator,Field
import re
from uuid import UUID
from typing import Optional, Annotated
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
    price_per_packorkilogram : Optional[Annotated[float, Field(gt=0)]]

class CatagoryUpdate(BaseModel):
    uuid_catagory : UUID
    name_sm : str

class ProductUpdate(BaseModel):
    uuid_product : UUID
    uuid_catagory : Optional[UUID] = None
    name_sm : Optional[str] = None
    price_per_packorkilogram : Optional[Annotated[float, Field(gt=0)]]

class CatagorySearch(BaseModel):
    name_catagory : Optional[str] = None
    uuid_catagory : Optional[UUID] = None

class ProductSearch(BaseModel):
    uuid_product : Optional[UUID] = None
    name_sm : Optional[str] = None

class SaiCart(BaseModel):
    uuid_product : UUID
    quantity_sm : Annotated[int, Field(ge=1)]

class OrderSearch(BaseModel):    
    product_name: Optional[str] = None   

class AdminOrder(BaseModel):
    user_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_price   : Optional[Annotated[float, Field(ge=0)]] = None   
    max_price   : Optional[Annotated[float, Field(ge=0)]] = None 
    product_name: Optional[str] = None   
