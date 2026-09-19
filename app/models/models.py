import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    price = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)

    category_id = Column(
        String,
        ForeignKey("categories.id"),
        nullable=False
    )

    supplier_id = Column(
        String,
        ForeignKey("suppliers.id"),
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    total_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=generate_uuid)

    order_id = Column(
        String,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        String,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)