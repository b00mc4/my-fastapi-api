import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from Database.database import Base


class UserDATABASE(Base):
    __tablename__ = "users"

    id_db           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username_db     = Column(String, unique=True, index=True, nullable=False)
    email_db        = Column(String, unique=True, index=True, nullable=False)
    hashpassword_db = Column(String, nullable=False)
    role_db         = Column(String, nullable=False, default="user")

    otps   = relationship("OTPDATABASE",      back_populates="users", cascade="all, delete-orphan")
    carts  = relationship("CartUserDATABASE", back_populates="user",  cascade="all, delete-orphan")
    orders = relationship("OrderDATABASE",    back_populates="user",  cascade="all, delete-orphan")


class OTPDATABASE(Base):
    __tablename__ = "otps"

    id_db        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id_db   = Column(UUID(as_uuid=True), ForeignKey("users.id_db", ondelete="CASCADE"), nullable=False)
    otpcode_db   = Column(String, nullable=False)
    timestamp_db = Column(DateTime, nullable=False, server_default=func.now())
    expire_db    = Column(DateTime, nullable=False)
    verify_db    = Column(Boolean, nullable=False, default=False)

    users = relationship("UserDATABASE", back_populates="otps")


class CatagoryDATABASE(Base):
    __tablename__ = "catagorys"

    id_db   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name_db = Column(String, unique=True, nullable=False)

    products = relationship("ProductDATABASE", back_populates="catagorys", cascade="all, delete-orphan")


class ProductDATABASE(Base):
    __tablename__ = "products"

    id_db          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    catagory_id_db = Column(UUID(as_uuid=True), ForeignKey("catagorys.id_db", ondelete="CASCADE"), nullable=False)
    name_db        = Column(String, nullable=False)
    price_db       = Column(Float, nullable=False)
    timecreate_db  = Column(DateTime, nullable=False, server_default=func.now())
    image_db       = Column(String, nullable=True)

    catagorys   = relationship("CatagoryDATABASE",  back_populates="products")
    cart_items  = relationship("CartItemDATABASE",  back_populates="product",  cascade="all, delete-orphan")
    order_items = relationship("OrderItemDATABASE", back_populates="product")


class CartUserDATABASE(Base):
    __tablename__ = "cart"

    id_db      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id_db = Column(UUID(as_uuid=True), ForeignKey("users.id_db", ondelete="CASCADE"), nullable=False)
    create_at  = Column(DateTime, server_default=func.now())

    items = relationship("CartItemDATABASE", back_populates="cart", cascade="all, delete-orphan")
    user  = relationship("UserDATABASE",     back_populates="carts")


class CartItemDATABASE(Base):
    __tablename__ = "cart_item"

    id_db         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    cart_id_db    = Column(UUID(as_uuid=True), ForeignKey("cart.id_db",     ondelete="CASCADE"), nullable=False)
    product_id_db = Column(UUID(as_uuid=True), ForeignKey("products.id_db", ondelete="CASCADE"), nullable=False)
    quantity_db   = Column(Integer, nullable=False, default=1)

    cart    = relationship("CartUserDATABASE", back_populates="items")
    product = relationship("ProductDATABASE",  back_populates="cart_items")


class OrderDATABASE(Base):
    __tablename__ = "order"

    id_db       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id_db  = Column(UUID(as_uuid=True), ForeignKey("users.id_db", ondelete="CASCADE"), nullable=False)
    total_price = Column(Float, nullable=False)
    create_at   = Column(DateTime, server_default=func.now())

    items = relationship("OrderItemDATABASE", back_populates="order", cascade="all, delete-orphan")
    user  = relationship("UserDATABASE",      back_populates="orders")


class OrderItemDATABASE(Base):
    __tablename__ = "orderItem"

    id_db              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_id_db        = Column(UUID(as_uuid=True), ForeignKey("order.id_db",    ondelete="CASCADE"),  nullable=False)
    product_id_db      = Column(UUID(as_uuid=True), ForeignKey("products.id_db", ondelete="SET NULL"), nullable=True)
    quantity_db        = Column(Integer, nullable=False)
    price_per_piece_db = Column(Float, nullable=True)

    order   = relationship("OrderDATABASE",  back_populates="items")
    product = relationship("ProductDATABASE", back_populates="order_items")