import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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


@router.put("/users/{user_id}")
async def update_user(
    user_id: int, username: str = None, email: str = None, full_name: str = None, db: AsyncSession = Depends(get_db)
):
    """Update a user using asyncpg."""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields if provided
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name

    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a user using asyncpg."""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    await db.delete(user)
    await db.commit()
    return {"message": f"User {user_id} deleted successfully"}


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


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    name: str = None,
    price: float = None,
    sku: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a product using asyncpg."""
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update product fields if provided
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if sku is not None:
        product.sku = sku
    if description is not None:
        product.description = description

    await db.commit()
    await db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "sku": product.sku,
        "description": product.description,
    }


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a product using asyncpg."""
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete product
    await db.delete(product)
    await db.commit()
    return {"message": f"Product {product_id} deleted successfully"}


@router.get("/benchmark")
async def benchmark(count: int = 100, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that performs multiple database operations using asyncpg."""
    start_time = time.time()

    # Perform multiple select operations
    for _ in range(count):
        await db.execute(select(User))
        await db.execute(select(Product))

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = (count * 2) / execution_time

    return {
        "database": "asyncpg",
        "operations": count * 2,  # 2 queries per iteration
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
    }


@router.get("/benchmark/mixed")
async def benchmark_mixed(count: int = 100, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that performs mixed database operations (INSERT, UPDATE, DELETE, GET) using asyncpg."""

    start_time = time.time()
    operations = 0
    timestamp = int(time.time() * 1000)  # Millisecond timestamp for uniqueness

    # Perform mixed operations
    for i in range(count):
        # CREATE operation (25% of operations)
        if i % 4 == 0:
            user = User(
                username=f"bench_user_{timestamp}_{i}",
                email=f"bench_user_{timestamp}_{i}@example.com",
                full_name=f"Benchmark User {timestamp} {i}",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            product = Product(
                name=f"Bench Product {timestamp} {i}",
                price=10.99 + i,
                sku=f"BENCH-SKU-{timestamp}-{i}",
                description=f"Benchmark product {timestamp} {i}",
            )
            db.add(product)
            await db.commit()
            await db.refresh(product)
            operations += 2

        # READ operation (25% of operations)
        elif i % 4 == 1:
            await db.execute(select(User))
            await db.execute(select(Product))
            operations += 2

        # UPDATE operation (25% of operations)
        elif i % 4 == 2:
            # Update first user and product if they exist
            result_user = await db.execute(select(User).limit(1))
            user = result_user.scalars().first()
            if user:
                user.full_name = f"Updated User {timestamp} {i}"
                await db.commit()
                operations += 1

            result_product = await db.execute(select(Product).limit(1))
            product = result_product.scalars().first()
            if product:
                product.price = 20.99 + i
                await db.commit()
                operations += 1

        # DELETE operation (25% of operations)
        else:
            # Delete last user and product if they exist
            result_user = await db.execute(select(User).order_by(User.id.desc()).limit(1))
            user = result_user.scalars().first()
            if user:
                await db.delete(user)
                await db.commit()
                operations += 1

            result_product = await db.execute(select(Product).order_by(Product.id.desc()).limit(1))
            product = result_product.scalars().first()
            if product:
                await db.delete(product)
                await db.commit()
                operations += 1

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "asyncpg",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
    }


@router.get("/benchmark/parallel")
async def benchmark_parallel(count: int = 100, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that performs multiple database operations in parallel using asyncpg."""
    import asyncio

    from db import get_db_session

    start_time = time.time()
    operations = 0

    # Define async query functions
    async def query_users():
        async with get_db_session() as task_db:
            return await task_db.execute(select(User))

    async def query_products():
        async with get_db_session() as task_db:
            return await task_db.execute(select(Product).where(Product.price > 10.0).order_by(Product.price.desc()))

    async def query_users_with_filter():
        async with get_db_session() as task_db:
            return await task_db.execute(select(User).where(User.username.like("user%")))

    async def query_products_with_join():
        # Simulate a more complex query with a join
        async with get_db_session() as task_db:
            stmt = select(Product, User).join(User, Product.id == User.id, isouter=True).where(Product.price > 5.0)
            return await task_db.execute(stmt)

    # Run queries in parallel batches
    for _ in range(count):
        # Execute 4 queries in parallel
        results = await asyncio.gather(
            query_users(), query_products(), query_users_with_filter(), query_products_with_join()
        )

        # Process results to ensure they're fully consumed
        for result in results:
            result.fetchall()

        operations += 4  # 4 queries per iteration

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "asyncpg",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "parallel": True,
    }


@router.get("/benchmark/complex")
async def benchmark_complex(count: int = 100, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that performs complex database operations using asyncpg."""
    start_time = time.time()
    operations = 0

    for _ in range(count):
        # Complex query 1: Aggregation with group by
        stmt1 = (
            select(
                User.full_name,
                func.count(Product.id).label("product_count"),
                func.avg(Product.price).label("avg_price"),
            )
            .select_from(User)
            .join(Product, User.id == Product.id, isouter=True)
            .group_by(User.full_name)
            .having(func.avg(Product.price) > 0)
        )
        await db.execute(stmt1)
        operations += 1

        # Complex query 2: Subquery with order by
        subq = select(Product.id, func.rank().over(order_by=Product.price.desc()).label("price_rank")).subquery()

        stmt2 = select(Product).join(subq, Product.id == subq.c.id).where(subq.c.price_rank <= 5)
        await db.execute(stmt2)
        operations += 1

        # Complex query 3: Window functions
        stmt3 = select(User.username, User.email, func.row_number().over(order_by=User.username).label("row_num"))
        await db.execute(stmt3)
        operations += 1

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "asyncpg",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "complex": True,
    }


@router.get("/benchmark/concurrent")
async def benchmark_concurrent(count: int = 100, concurrency: int = 5, db: AsyncSession = Depends(get_db)):
    """Benchmark endpoint that simulates concurrent database operations using asyncpg."""
    import asyncio

    from db import async_session

    start_time = time.time()

    # Define a single task that performs database operations
    async def db_task(task_id: int):
        task_operations = 0
        # Her görev için yeni bir oturum oluştur
        async with async_session() as task_db:
            # Perform a mix of operations
            for i in range(count // concurrency):
                # SELECT operation
                await task_db.execute(select(User).where(User.id > task_id % 5))
                await task_db.execute(select(Product).where(Product.price > 10 + task_id % 10))
                task_operations += 2

                # More complex SELECT
                stmt = select(User, Product).outerjoin(Product, User.id == Product.id)
                await task_db.execute(stmt)
                task_operations += 1

        return task_operations

    # Create and run concurrent tasks
    tasks = [db_task(i) for i in range(concurrency)]
    results = await asyncio.gather(*tasks)

    # Sum up all operations
    total_operations = sum(results)

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = total_operations / execution_time

    return {
        "database": "asyncpg",
        "operations": total_operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "concurrency": concurrency,
    }
