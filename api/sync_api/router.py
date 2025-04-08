from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from db import get_db_sync
from models import Product, User

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/users")
def get_users(db: Session = Depends(get_db_sync)):
    """Get all users using psycopg2."""
    users = db.query(User).all()
    return {
        "users": [
            {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}
            for user in users
        ]
    }


@router.post("/users")
def create_user(username: str, email: str, full_name: str = None, db: Session = Depends(get_db_sync)):
    """Create a new user using psycopg2."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Create new user
    user = User(username=username, email=email, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}


@router.get("/products")
def get_products(db: Session = Depends(get_db_sync)):
    """Get all products using psycopg2."""
    products = db.query(Product).all()
    return {
        "products": [
            {"id": product.id, "name": product.name, "price": product.price, "sku": product.sku} for product in products
        ]
    }


@router.post("/products")
def create_product(name: str, price: float, sku: str, description: str = None, db: Session = Depends(get_db_sync)):
    """Create a new product using psycopg2."""
    # Check if product already exists
    existing_product = db.query(Product).filter(Product.sku == sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    # Create new product
    product = Product(name=name, price=price, sku=sku, description=description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "sku": product.sku,
        "description": product.description,
    }


@router.get("/benchmark")
def benchmark(count: int = 100, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that performs multiple database operations using psycopg2."""
    start_time = func.now()

    # Perform multiple select operations
    for _ in range(count):
        db.query(User).all()
        db.query(Product).all()

    # Get execution time
    execution_time = db.query(func.now() - start_time).scalar()
    execution_seconds = float(execution_time.total_seconds())

    # Avoid division by zero
    operations_per_second = 0
    if execution_seconds > 0:
        operations_per_second = (count * 2) / execution_seconds

    return {
        "database": "psycopg2",
        "operations": count * 2,  # 2 queries per iteration
        "execution_time_seconds": execution_seconds,
        "operations_per_second": operations_per_second,
    }
