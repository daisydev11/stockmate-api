from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.models import models
from app.routers import products, categories, suppliers, orders


Base.metadata.create_all(bind=engine)


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


app = FastAPI(
    title="StockMate API",
    description="A REST API for managing inventory and ordering data.",
    version="1.0.0"
)

app.state.limiter = limiter


# -------------------------
# ERROR HANDLERS
# -------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", "An error occurred")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid or missing data"
            }
        }
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded
):
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later."
            }
        }
    )


# -------------------------
# ROUTERS
# -------------------------

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(orders.router)


# -------------------------
# BASIC ENDPOINTS
# -------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to StockMate API",
        "status": "running"
    }


@app.get("/api/v1/health")
@limiter.limit("10/minute")
def health_check(request: Request):
    return {
        "data": {
            "status": "healthy"
        }
    }