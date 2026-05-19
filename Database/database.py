from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from Database.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from Database.model import(UserDATABASE, OTPDATABASE,
        CatagoryDATABASE, ProductDATABASE,
        CartUserDATABASE, CartItemDATABASE,
        OrderDATABASE, OrderItemDATABASE)
    Base.metadata.create_all(bind=engine)