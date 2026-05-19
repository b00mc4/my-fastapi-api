from fastapi import FastAPI, APIRouter
from Database.database import init_db
from contextlib import asynccontextmanager
from Endpoint import auth,product,cart,order, admin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield

app = FastAPI(title="ร้านค้าขายผลไม้", description="เป็นร้านเปิดใหม่ของมูมกะเบ ที่มีความสดตลอด พร้อมบวก", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

root_router = APIRouter(tags=["Fruit Store"])

@root_router.get("/")
def get_a_fruitstore():
    return{"status":"ok"}

app.include_router(root_router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = False,
    allow_methods=["*"],
    allow_headers=["*"]
)