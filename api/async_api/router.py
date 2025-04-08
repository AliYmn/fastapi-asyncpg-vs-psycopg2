from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from db import get_db
from models import Product, User

router = APIRouter(prefix="/async", tags=["async"])


@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users using asyncpg."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {
        "users": [
            {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}
            for user in users
        ]
    }


@router.post("/users")
async def create_user(username: str, email: str, full_name: str = None, db: AsyncSession = Depends(get_db)):
    """Create a new user using asyncpg."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user
    user = User(username=username, email=email, full_name=full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}


@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    """Get all products using asyncpg."""
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return {
        "products": [
            {"id": product.id, "name": product.name, "price": product.price, "sku": product.sku} for product in products
        ]
    }


@router.post("/products")
async def create_product(
    name: str, price: float, sku: str, description: str = None, db: AsyncSession = Depends(get_db)
):
    """Create a new product using asyncpg."""
    # Check if product already exists
    result = await db.execute(select(Product).where(Product.sku == sku))
    existing_product = result.scalars().first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    # Create new product
    product = Product(name=name, price=price, sku=sku, description=description)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "sku": product.sku,
        "description": product.description,
    }


@router.get("/benchmark")
async def benchmark(count: int = 100, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that performs multiple database operations using asyncpg."""
    start_time = func.now()

    # Perform multiple select operations
    for _ in range(count):
        await db.execute(select(User))
        await db.execute(select(Product))

    # Get execution time
    result = await db.execute(select(func.now() - start_time).as_scalar())
    execution_time = result.scalar()
    execution_seconds = float(execution_time.total_seconds())

    # Avoid division by zero
    operations_per_second = 0
    if execution_seconds > 0:
        operations_per_second = (count * 2) / execution_seconds

    return {
        "database": "asyncpg",
        "operations": count * 2,  # 2 queries per iteration
        "execution_time_seconds": execution_seconds,
        "operations_per_second": operations_per_second,
    }
