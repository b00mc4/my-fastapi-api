# 🍉 Fruit Store API

ระบบ Backend สำหรับร้านค้าขายผลไม้ รองรับการสมัครสมาชิก เข้าสู่ระบบด้วย JWT จัดการหมวดหมู่ สินค้า ตะกร้า และการสั่งซื้อ พร้อม Admin Dashboard

---

## 🛠️ Tech Stack

| ส่วน | เทคโนโลยี |
|------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT (python-jose) |
| Password Hashing | bcrypt |
| Validation | Pydantic v2 |
| Server | Uvicorn |

> ⚠️ **ต้องใช้ Python 3.9 ขึ้นไปเท่านั้น** (ใช้ `zoneinfo` ซึ่งไม่มีใน Python 3.8)

---

## 📦 การติดตั้ง (Installation)

### 1. Clone repository

```bash
git clone https://github.com/yourname/fruit-store.git
cd fruit-store
```

### 2. สร้าง Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

---

## 📚 Libraries ที่ใช้ (requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-jose[cryptography]
bcrypt
pydantic[email]
pydantic-settings
python-multipart
```

---

## ⚙️ ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ที่ root ของโปรเจกต์ โดยดูจากไฟล์ `_env` ในโปรเจกต์เป็นแม่แบบ แล้วคัดลอกเป็นไฟล์ใหม่ชื่อ `.env`

```bash
# Windows
copy _env .env

# Mac / Linux
cp _env .env
```

แล้วแก้ไขค่าใน `.env` ให้ตรงกับของตัวเอง

### ตัวอย่างไฟล์ `.env`

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/fruitstore

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTE=60
```

### อธิบายแต่ละตัวแปร

| ตัวแปร | คำอธิบาย | ตัวอย่าง |
|--------|----------|---------|
| `DATABASE_URL` | URL เชื่อมต่อ PostgreSQL | `postgresql://user:pass@localhost:5432/fruitstore` |
| `SECRET_KEY` | Key สำหรับเข้ารหัส JWT (ตั้งยาก ๆ) | `mys3cr3tk3y!@#` |
| `ALGORITHM` | Algorithm ที่ใช้เข้ารหัส JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTE` | อายุของ Token (นาที) | `60` |

---

## 🗄️ ตั้งค่า Database

ต้องสร้าง Database ใน PostgreSQL ก่อน

```sql
CREATE DATABASE fruitstore;
```

ระบบจะสร้าง Table อัตโนมัติตอนรัน Server ครั้งแรก (ผ่าน `init_db()`)

---

## 🚀 วิธีรัน

```bash
uvicorn main:app --reload
```

หรือระบุ host และ port

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📄 API Documentation

เมื่อรัน Server แล้วเปิดได้ที่

| หน้า | URL |
|------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 👤 สร้าง Admin คนแรก

ระบบไม่มี endpoint สมัครแบบ admin โดยตรง ต้องทำผ่าน SQL หลังจากสมัครสมาชิกด้วย `/auth/register` แล้ว

**ขั้นตอน:**

1. สมัครสมาชิกปกติผ่าน `POST /auth/register` ก่อน
2. เปิด psql หรือ pgAdmin แล้วรันคำสั่งนี้

```sql
UPDATE users SET role_db = 'admin' WHERE username = 'your_username';
```

3. Login ใหม่อีกครั้งเพื่อรับ Token ที่มีสิทธิ์ admin

> ⚠️ ทำขั้นตอนนี้แค่ครั้งเดียวตอน setup ระบบใหม่เท่านั้น

---

## 🔑 เงื่อนไขรหัสผ่าน

รหัสผ่านทุกช่องในระบบ (สมัครสมาชิก / เปลี่ยนรหัส / รีเซต) ต้องผ่านเงื่อนไขดังนี้

| เงื่อนไข | รายละเอียด |
|---------|-----------|
| ความยาว | อย่างน้อย **8 ตัวอักษร** |
| ตัวอักษร | ต้องมีตัวอักษรภาษาอังกฤษอย่างน้อย 1 ตัว |
| ตัวเลข | ต้องมีตัวเลขอย่างน้อย 1 ตัว |
| อักขระพิเศษ | ต้องมีอย่างน้อย 1 ตัว เช่น `!@#$%^&*` |

ตัวอย่างรหัสผ่านที่ผ่านเงื่อนไข: `MyPass1!`

---

## 📮 ระบบ OTP (Forgot Password)

> ⚠️ **Dev Mode เท่านั้น** — ระบบยังไม่ได้ต่อ Email จริง

เมื่อเรียก `POST /auth/password/forgot` ระบบจะ **คืนรหัส OTP กลับมาใน response โดยตรง** ไม่ได้ส่งอีเมล ให้นำรหัสนั้นไปใช้กับ `POST /auth/password/reset` ได้เลย

OTP มีอายุ **10 นาที** และใช้ได้ครั้งเดียว

---

## 🗂️ โครงสร้างโปรเจกต์

```
fruit-store/
├── Database/
│   ├── config.py        # โหลด Environment Variables
│   ├── database.py      # เชื่อมต่อ Database
│   └── model.py         # Database Models
├── Endpoint/
│   ├── auth.py          # Auth endpoints
│   ├── catagory.py      # Category endpoints
│   ├── product.py       # Product endpoints
│   ├── cart.py          # Cart endpoints
│   ├── order.py         # Order endpoints
│   └── admin.py         # Admin endpoints
├── function/
│   ├── def_auth.py      # Auth business logic
│   ├── def_catagory.py  # Category business logic
│   ├── def_product.py   # Product business logic
│   ├── def_cart.py      # Cart business logic
│   ├── def_order.py     # Order business logic
│   └── def_admin.py     # Admin business logic
├── static/image/        # รูปภาพสินค้า
├── Catagory/image/      # รูปภาพหมวดหมู่
├── schemas.py           # Pydantic Schemas
├── main.py              # Entry point
├── requirements.txt
├── _env                 # ตัวอย่าง Environment Variables (คัดลอกเป็น .env)
└── README.md
```

---

## 👤 ระดับสิทธิ์ (Roles)

| Role | สิทธิ์ |
|------|--------|
| `user` | ดูสินค้า จัดการตะกร้า สั่งซื้อ ดูประวัติบิล |
| `admin` | จัดการสินค้า หมวดหมู่ ดูออร์เดอร์ทั้งหมด ดูสถิติ ลบ user |
