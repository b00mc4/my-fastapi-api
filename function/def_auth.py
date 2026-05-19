from jose import jwt, JWTError
import random
import bcrypt
from Database.config import settings
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from Database.database import get_db
from Database.model import UserDATABASE,OTPDATABASE
from sqlalchemy.orm import Session
from schemas import UserRegister,ChangePassword,ForgotPassword,ResetPassword
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

THAI_TZ = ZoneInfo("Asia/Bangkok")
#=========================================================================================

def get_password_hash(text:str) -> str:
    return bcrypt.hashpw(text.encode(),bcrypt.gensalt()).decode("utf-8")

def verify_hash(loginPassword:str,databasePassword:str) -> bool:
    try:
        return bcrypt.checkpw(loginPassword.encode(),databasePassword.encode())
    except ValueError:
        return False

#==========================================================================================

def validate_password(password:str):
    special = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")
    error = []
    if len(password) < 8:
        error.append("ยาวอย่างน้อย8ตัวอักษร")
    if not any(word.isalpha() for word in password):
        error.append("ต้องมีตัวอักษรภาษาอังกฤษ")
    if not any(word.isdigit() for word in password):
        error.append("ต้องมีตัวเลข")
    if not any(word in special for word in password):
        error.append("ต้องมีอักขระพิเศษ")
    if error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"รหัสผ่านต้อง: {', '.join(error)}")
#=====================================================================================================

def generate_otp()->str:
    return str(random.randint(000000,999999)) 

def get_otp(natee:int=5)->datetime:
    return datetime.now(THAI_TZ) + timedelta(minutes=natee)

#===========================================================================================

def create_access_token(data:dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
    return jwt.encode(payload,settings.SECRET_KEY, algorithm = settings.ALGORITHM)

def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ไม่สามารถเข้าถึงได้ กรุณา login ก่อน", headers={"WWW-Authenticate":"Bearer"})
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise exc
    except JWTError:
        raise exc
    
    user = db.query(UserDATABASE).filter(UserDATABASE.username_db == username).first()
    if not user:
        raise exc
    return user

def get_current_admin(roleuser:UserDATABASE = Depends(get_current_user)):
    if roleuser.role_db != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="ปฎิเสธการเข้าถึง ต้องเป็นแอดมินเท่านั้นนะจ๊ะ")
    return roleuser

def get_current_regular_user(roleuser : UserDATABASE = Depends(get_current_user)):
    if roleuser.role_db == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="แอดมินไม่สามารถใช้งานฟีเจอร์นี้ได้ กรุณาใช้บัญชีผู้ใช้ทั่วไป")
    return roleuser

#=====================================================================================================

def register_user(db: Session, data:UserRegister) -> UserDATABASE:
    if db.query(UserDATABASE).filter(UserDATABASE.username_db == data.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="มีชื่อผู้ใช้ในนี้ในระบบแล้ว")
    if db.query(UserDATABASE).filter(UserDATABASE.email_db == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="มีอีเมลนี้ในระบบแล้ว")
    if data.password != data.password_confirm:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="รหัสผ่านไม่ตรงกัน")
    validate_password(data.password)
    user = UserDATABASE(id_db=uuid.uuid4(), username_db=data.username, email_db=data.email, hashpassword_db=get_password_hash(data.password), role_db="user")
    db.add(user)
    db.commit()
    return {"message":"สมัครแล้วเรียบร้อย พร้อมลุย"}

def login_user(db: Session, username:str, password:str)->dict:
    user = db.query(UserDATABASE).filter(UserDATABASE.username_db == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ชื่อหรือรหัสผ่านไม่ถูกต้อง")
    if not verify_hash(password, user.hashpassword_db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ชื่อหรือรหัสผ่านไม่ถูกต้อง")
    access_token = create_access_token(data={"sub":user.username_db})
    return {"access_token":access_token,"token_type":"Bearer"}

def changepassword(db: Session, current_user:UserDATABASE, data:ChangePassword):
    if not verify_hash(data.oldpassword_sm,current_user.hashpassword_db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="รหัสผ่านไม่ถูกต้อง")
    if data.newpassword_sm != data.confirm_newpassword_sm:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="รหัสผ่านไม่ตรงกัน")
    validate_password(data.newpassword_sm)
    current_user.hashpassword_db = get_password_hash(data.newpassword_sm)
    db.commit()
    return {"message":"เปลี่ยนรหัสผ่านเรียบร้อย"}

def forgotpassword(data:ForgotPassword , db:Session):
    user = db.query(UserDATABASE).filter(UserDATABASE.email_db == data.email).first()
    if not user:
        return {"messgae":"หากมี Email ในระบบจะส่ง OTP ไป"}
    otp_code = str(random.randint(100000,999999))
    expire_time = datetime.now(THAI_TZ) + timedelta(minutes=10)
    new_otp = OTPDATABASE(user_id_db=user.id_db, otpcode_db = otp_code, expire_db = expire_time, verify_db =False)
    db.add(new_otp)
    db.commit()
    return {"ส่ง OTP ไปทาง email เรียบร้อย"}

def resetpassword(data:ResetPassword, db:Session):
    current_time = datetime.now(THAI_TZ)
    record = db.query(OTPDATABASE).filter(OTPDATABASE.otpcode_db == data.otp_sm, OTPDATABASE.expire_db > current_time, OTPDATABASE.verify_db ==False ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="เลข OTP ไม่ถูกต้องหรือเลข OTP หมดอายุแล้ว")
    emailwillchange = db.query(UserDATABASE).filter(UserDATABASE.id_db == record.user_id_db).first()
    if not emailwillchange:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบบัญชีนี้")
    validate_password(data.newpassword_sm)
    if data.newpassword_sm != data.confirm_newpassword_sm:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="รหัสผ่านไม่ตรงกัน")
    emailwillchange.hashpassword_db = get_password_hash(data.newpassword_sm)
    record.verify_db = True
    db.commit()
    return {"message":"เปลี่ยนรหัสผ่านเรียบร้อย"}