from fastapi import FastAPI
from app.database import engine, Base
from app.models import models
from app.routers import products, categories, suppliers, orders

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="StockMate API",
    description="A REST API for managing inventory and ordering data.",
    version="1.0.0"
)

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to StockMate API",
        "status": "running"
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "data": {
            "status": "healthy"
        }
    }