import random

from faker import Faker

from app.database import SessionLocal, engine, Base
from app.models.models import (
    Category,
    Supplier,
    Product,
    Order,
    OrderItem,
)


fake = Faker()

Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()

    try:
        # Prevent duplicate data when the seed script is run again
        if db.query(Category).first():
            print("Database already contains seed data. Skipping seed.")
            return

        print("Seeding database...")

        # -------------------------
        # CATEGORIES
        # -------------------------

        category_names = [
            "Electronics",
            "Fashion",
            "Home & Kitchen",
            "Beauty",
            "Sports",
            "Books",
            "Office Supplies",
            "Health",
            "Accessories",
            "Groceries",
        ]

        categories = []

        for name in category_names:
            category = Category(
                name=name,
                description=fake.sentence()
            )

            db.add(category)
            categories.append(category)

        db.flush()

        # -------------------------
        # SUPPLIERS
        # -------------------------

        suppliers = []

        for _ in range(200):
            supplier = Supplier(
                name=fake.company(),
                email=fake.unique.company_email(),
                phone=fake.phone_number(),
                address=fake.address()
            )

            db.add(supplier)
            suppliers.append(supplier)

        db.flush()

        # -------------------------
        # PRODUCTS
        # -------------------------

        products = []

        for _ in range(500):
            product = Product(
                name=fake.catch_phrase(),
                description=fake.sentence(),
                price=random.randint(1000, 50000000),
                stock_quantity=random.randint(0, 500),
                category_id=random.choice(categories).id,
                supplier_id=random.choice(suppliers).id
            )

            db.add(product)
            products.append(product)

        db.flush()

        # -------------------------
        # ORDERS + ORDER ITEMS
        # -------------------------

        statuses = [
            "pending",
            "processing",
            "shipped",
            "delivered",
            "cancelled"
        ]

        for _ in range(300):
            selected_products = random.sample(
                products,
                random.randint(1, 5)
            )

            order = Order(
                customer_name=fake.name(),
                customer_email=fake.email(),
                status=random.choice(statuses),
                total_amount=0
            )

            db.add(order)
            db.flush()

            total = 0

            for product in selected_products:
                quantity = random.randint(1, 4)

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price
                )

                total += product.price * quantity
                db.add(order_item)

            order.total_amount = total

        db.commit()

        print("Seed completed successfully!")
        print(f"Categories: {len(categories)}")
        print(f"Suppliers: {len(suppliers)}")
        print(f"Products: {len(products)}")
        print("Orders: 300")

    except Exception as error:
        db.rollback()
        print(f"Seed failed: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()