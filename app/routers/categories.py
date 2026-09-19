from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Category, Product


router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"]
)


@router.get("")
def get_categories(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = "name",
    order: str = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(Category)

    allowed_sort_fields = {
        "name": Category.name,
        "created_at": Category.created_at
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_FIELD",
                "message": f"Cannot sort categories by '{sort}'"
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

    categories = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at
            }
            for category in categories
        ],
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + len(categories) < total
        }
    }


@router.get("/{category_id}")
def get_category(category_id: str, db: Session = Depends(get_db)):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Category not found"
            }
        )

    return {
        "data": {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "created_at": category.created_at
        }
    }


@router.get("/{category_id}/products")
def get_category_products(
    category_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "Category not found"
            }
        )

    query = db.query(Product).filter(
        Product.category_id == category_id
    )

    total = query.count()
    products = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock_quantity": product.stock_quantity
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