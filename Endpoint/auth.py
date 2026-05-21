from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Database.database import get_db
from function import def_auth
from schemas import (
    UserRegister, ChangePassword, ForgotPassword, ResetPassword,
    TokenResponse, MeResponse, SimpleMessage,
)
from Database.model import UserDATABASE

router = APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/register",status_code=201,summary="ระบบสมัครสมาชิก",response_model=SimpleMessage)
def register(body:UserRegister, db:Session = Depends(get_db)):
    return def_auth.register_user(db, body)

@router.post("/login",status_code=201,summary="เข้าสู่ระบบ",response_model=TokenResponse)
def login(data:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    return def_auth.login_user(db,username=data.username,password=data.password)

@router.get("/me",summary="ดูข้อมูลของตัวเอง", response_model=MeResponse)
def get_my_profile(current_user: UserDATABASE = Depends(def_auth.get_current_user)):
    return {"message":"ยินดีต้อนรับ", "username":current_user.username_db, "email":current_user.email_db, "role":current_user.role_db}

@router.put("/password",summary="เปลี่ยนรหัสผ่าน",response_model=SimpleMessage)
def changepassword(body: ChangePassword, db: Session = Depends(get_db), current_user: UserDATABASE = Depends(def_auth.get_current_user)):
    return def_auth.changepassword(db, current_user, body)  

@router.post("/password/forgot", summary="ลืมรหัสผ่าน")
def forgot_password(body:ForgotPassword, db:Session = Depends(get_db)):
    return def_auth.forgotpassword(body,db)

@router.post("/password/reset",summary="รีเซตรหัสผ่าน",response_model=SimpleMessage)
def reset_password(body:ResetPassword, db:Session = Depends(get_db)):
    return def_auth.resetpassword(body,db)