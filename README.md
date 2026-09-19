# StockMate API

StockMate API is a REST API for managing inventory and ordering data.

It provides structured access to products, categories, suppliers, and orders while supporting pagination, filtering, sorting, validation, and consistent error handling.

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

Generated identifiers make resources harder to enumerate and allow records to be uniquely identified without exposing predictable sequential IDs.

## Relationship Overview

Category → Products

Supplier → Products

Order → Order Items → Products