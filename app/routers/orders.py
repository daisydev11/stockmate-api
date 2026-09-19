from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Order


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"]
)


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    total_amount: int = Field(gt=0)
    status: str = "pending"


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None


@router.get("")
def get_orders(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None,
    min_total: Optional[int] = Query(default=None, ge=0),
    sort: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Order)

    if status is not None:
        query = query.filter(Order.status == status)

    if min_total is not None:
        query = query.filter(Order.total_amount >= min_total)

    allowed_sort_fields = {
        "total_amount": Order.total_amount,
        "created_at": Order.created_at,
        "status": Order.status
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_FIELD",
                "message": f"Cannot sort orders by '{sort}'"
            }
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_ORDER",
                "message": "Order must be 'asc' or 'desc'"
            }
        )

    total = query.count()
    sort_column = allowed_sort_fields[sort]

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    orders = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": item.id,
                "customer_name": item.customer_name,
                "customer_email": item.customer_email,
                "status": item.status,
                "total_amount": item.total_amount,
                "created_at": item.created_at
            }
            for item in orders
        ],
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + len(orders) < total
        }
    }


@router.post("", status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total_amount=order.total_amount,
        status=order.status
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "data": {
            "id": new_order.id,
            "customer_name": new_order.customer_name,
            "customer_email": new_order.customer_email,
            "status": new_order.status,
            "total_amount": new_order.total_amount,
            "created_at": new_order.created_at
        }
    }


@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Order not found"
            }
        )

    return {
        "data": {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at
        }
    }


@router.patch("/{order_id}")
def update_order(
    order_id: str,
    update: OrderUpdate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Order not found"
            }
        )

    if update.customer_name is not None:
        order.customer_name = update.customer_name

    if update.customer_email is not None:
        order.customer_email = update.customer_email

    if update.status is not None:
        order.status = update.status

    db.commit()
    db.refresh(order)

    return {
        "data": {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "status": order.status,
            "total_amount": order.total_amount
        }
    }


@router.delete("/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Order not found"
            }
        )

    db.delete(order)
    db.commit()

    return {
        "data": {
            "message": "Order deleted successfully"
        }
    }