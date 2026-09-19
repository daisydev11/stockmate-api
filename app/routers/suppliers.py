from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Supplier


router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"]
)


@router.get("")
def get_suppliers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = "name",
    order: str = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)

    allowed_sort_fields = {
        "name": Supplier.name,
        "created_at": Supplier.created_at
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_FIELD",
                "message": f"Cannot sort suppliers by '{sort}'"
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

    suppliers = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": supplier.id,
                "name": supplier.name,
                "email": supplier.email,
                "phone": supplier.phone,
                "address": supplier.address,
                "created_at": supplier.created_at
            }
            for supplier in suppliers
        ],
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + len(suppliers) < total
        }
    }


@router.get("/{supplier_id}")
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Supplier not found"
            }
        )

    return {
        "data": {
            "id": supplier.id,
            "name": supplier.name,
            "email": supplier.email,
            "phone": supplier.phone,
            "address": supplier.address,
            "created_at": supplier.created_at
        }
    }