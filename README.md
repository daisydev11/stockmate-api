# StockMate API

StockMate API is a REST API for managing inventory and ordering data.

It provides structured access to products, categories, suppliers, and orders while supporting pagination, filtering, sorting, validation, consistent error handling, and rate limiting.

## Features

- RESTful API design with versioned `/api/v1/` routes
- Products, categories, suppliers, orders, and order-item resources
- UUID-based resource identifiers
- Resource relationships and nested routes
- Pagination using `limit` and `offset`
- Filtering and sorting
- Input validation
- Consistent JSON error responses
- HTTP status codes including 200, 201, 400, 404, 422, and 429
- Rate limiting
- Repeatable database seed script
- Interactive Swagger/OpenAPI documentation
- Health-check endpoint

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL for production
- Faker for realistic seed data
- SlowAPI for rate limiting
- Uvicorn ASGI server

## Resource Design

### Category

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | Unique identifier for the category |
| name | String | Yes | Name of the category |
| description | String | No | Short description of the category |
| created_at | DateTime | Yes | Date and time the category was created |

### Product

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | Unique identifier for the product |
| name | String | Yes | Name of the product |
| description | String | No | Description of the product |
| price | Integer | Yes | Product price stored in minor currency units |
| stock_quantity | Integer | Yes | Number of units currently available |
| category_id | UUID | Yes | References the category the product belongs to |
| supplier_id | UUID | Yes | References the supplier of the product |
| created_at | DateTime | Yes | Date and time the product was created |

### Supplier

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | Unique identifier for the supplier |
| name | String | Yes | Name of the supplier |
| email | String | Yes | Supplier contact email |
| phone | String | No | Supplier contact phone number |
| address | String | No | Supplier address |
| created_at | DateTime | Yes | Date and time the supplier was created |

### Order

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | Unique identifier for the order |
| customer_name | String | Yes | Name of the customer |
| customer_email | String | Yes | Customer email address |
| status | String | Yes | Current status of the order |
| total_amount | Integer | Yes | Total order amount stored in minor currency units |
| created_at | DateTime | Yes | Date and time the order was created |

### Order Item

| Field | Type | Required | Description |
|---|---|---|---|
| id | UUID | Yes | Unique identifier for the order item |
| order_id | UUID | Yes | References the order |
| product_id | UUID | Yes | References the product |
| quantity | Integer | Yes | Number of units of the product ordered |
| unit_price | Integer | Yes | Price of one unit at the time the order was created |

## Resource Relationships

- A category can contain many products.
- A product belongs to one category.
- A supplier can supply many products.
- A product belongs to one supplier.
- An order can contain many order items.
- An order item belongs to one order.
- An order item references one product.
- A product can appear in many order items.

## Identifier Strategy

All resources use generated UUIDs instead of sequential integer identifiers.

Generated identifiers allow records to be uniquely identified without exposing predictable sequential IDs.

## Relationship Overview

```text
Category → Products

Supplier → Products

Order → Order Items → Products
```

## API Endpoints

### Products

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/products` | Retrieve products |
| GET | `/api/v1/products/{product_id}` | Retrieve a single product |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/categories` | Retrieve categories |
| GET | `/api/v1/categories/{category_id}` | Retrieve a category |
| GET | `/api/v1/categories/{category_id}/products` | Retrieve products in a category |

### Suppliers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/suppliers` | Retrieve suppliers |
| GET | `/api/v1/suppliers/{supplier_id}` | Retrieve a supplier |

### Orders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/orders` | Retrieve orders |
| POST | `/api/v1/orders` | Create an order |
| GET | `/api/v1/orders/{order_id}` | Retrieve a single order |
| PATCH | `/api/v1/orders/{order_id}` | Update an order |
| DELETE | `/api/v1/orders/{order_id}` | Delete an order |

### System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome/status endpoint |
| GET | `/api/v1/health` | Health-check endpoint |

## Pagination

Collection endpoints support pagination using `limit` and `offset`.

Example:

```text
GET /api/v1/products?limit=20&offset=0
```

A collection response includes pagination metadata:

```json
{
  "data": [],
  "meta": {
    "total": 500,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

The maximum allowed `limit` is 100.

## Filtering

Products can be filtered by minimum price and category.

```text
GET /api/v1/products?min_price=100000
GET /api/v1/products?category_id={category_id}
```

Orders can be filtered by status and minimum total amount.

```text
GET /api/v1/orders?status=pending
GET /api/v1/orders?min_total=100000
```

Filters can be combined with pagination and sorting.

## Sorting

Collection endpoints support sorting using the `sort` and `order` parameters.

Example:

```text
GET /api/v1/products?sort=price&order=asc
```

`order` accepts:

```text
asc
desc
```

Unsupported sort fields return an HTTP `400` response.

## Response Format

Successful collection requests use the following structure:

```json
{
  "data": [],
  "meta": {
    "total": 500,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

Single-resource responses use:

```json
{
  "data": {
    "id": "resource-uuid"
  }
}
```

## Error Handling

Errors use a consistent JSON envelope:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Product not found"
  }
}
```

Example invalid sorting request:

```text
GET /api/v1/products?sort=banana
```

Response:

```json
{
  "error": {
    "code": "INVALID_SORT_FIELD",
    "message": "Cannot sort products by 'banana'"
  }
}
```

## Rate Limiting

StockMate includes rate limiting using SlowAPI.

When a configured rate limit is exceeded, the API returns HTTP `429 Too Many Requests`.

Example:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later."
  }
}
```

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd stockmate-api
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Seed the database

```bash
python3 seed.py
```

The seed script creates realistic sample data for categories, suppliers, products, orders, and order items.

The script is repeatable. If seed data already exists, it does not create another duplicate dataset.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The local API is available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive OpenAPI documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

## Example Request

```bash
curl "http://127.0.0.1:8000/api/v1/products?limit=5&sort=price&order=asc"
```

## Example Order Creation

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Daisy Imhanzenobe",
    "customer_email": "daisy@example.com",
    "total_amount": 250000,
    "status": "pending"
  }'
```

## Deployment

Production API:

```text
TO BE ADDED AFTER DEPLOYMENT
```

Production API documentation:

```text
TO BE ADDED AFTER DEPLOYMENT
```

The production deployment will use a managed PostgreSQL database and environment-based configuration.

## Health Check

```text
GET /api/v1/health
```

Example successful response:

```json
{
  "data": {
    "status": "healthy"
  }
}
```

## Author

**Imhanzenobe Daisy Ehijie**

Built as part of a backend engineering assessment focused on API design, data modelling, documentation, deployment, and developer experience.