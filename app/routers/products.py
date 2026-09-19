from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Product


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)


@router.get("")
def get_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_price: Optional[int] = Query(default=None, ge=0),
    category_id: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # Filtering
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    # Validate sorting
    allowed_sort_fields = {
        "name": Product.name,
        "price": Product.price,
        "stock_quantity": Product.stock_quantity,
        "created_at": Product.created_at
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_FIELD",
                "message": f"Cannot sort products by '{sort}'"
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

    products = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "category_id": product.category_id,
                "supplier_id": product.supplier_id,
                "created_at": product.created_at
            }
            for product in products
        ],
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + len(products) < total
        }
    }


@router.get("/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Product not found"
            }
        )

    return {
        "data": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "supplier_id": product.supplier_id,
            "created_at": product.created_at
        }
    }