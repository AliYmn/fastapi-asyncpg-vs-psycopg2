import threading
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

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


@router.put("/users/{user_id}")
def update_user(
    user_id: int, username: str = None, email: str = None, full_name: str = None, db: Session = Depends(get_db_sync)
):
    """Update a user using psycopg2."""
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields if provided
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name

    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db_sync)):
    """Delete a user using psycopg2."""
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}


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


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: str = None,
    price: float = None,
    sku: str = None,
    description: str = None,
    db: Session = Depends(get_db_sync),
):
    """Update a product using psycopg2."""
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
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

    db.commit()
    db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "sku": product.sku,
        "description": product.description,
    }


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db_sync)):
    """Delete a product using psycopg2."""
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete product
    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}


@router.get("/benchmark")
def benchmark(count: int = 100, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that performs multiple database operations using psycopg2."""
    start_time = time.time()

    # Perform multiple select operations
    for _ in range(count):
        db.query(User).all()
        db.query(Product).all()

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = (count * 2) / execution_time

    return {
        "database": "psycopg2",
        "operations": count * 2,  # 2 queries per iteration
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
    }


@router.get("/benchmark/mixed")
def benchmark_mixed(count: int = 100, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that performs mixed database operations (INSERT, UPDATE, DELETE, GET) using psycopg2."""
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
            db.commit()
            db.refresh(user)

            product = Product(
                name=f"Bench Product {timestamp} {i}",
                price=10.99 + i,
                sku=f"BENCH-SKU-{timestamp}-{i}",
                description=f"Benchmark product {timestamp} {i}",
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            operations += 2

        # READ operation (25% of operations)
        elif i % 4 == 1:
            db.query(User).all()
            db.query(Product).all()
            operations += 2

        # UPDATE operation (25% of operations)
        elif i % 4 == 2:
            # Update first user and product if they exist
            user = db.query(User).first()
            if user:
                user.full_name = f"Updated User {timestamp} {i}"
                db.commit()
                operations += 1

            product = db.query(Product).first()
            if product:
                product.price = 20.99 + i
                db.commit()
                operations += 1

        # DELETE operation (25% of operations)
        else:
            # Delete last user and product if they exist
            user = db.query(User).order_by(User.id.desc()).first()
            if user:
                db.delete(user)
                db.commit()
                operations += 1

            product = db.query(Product).order_by(Product.id.desc()).first()
            if product:
                db.delete(product)
                db.commit()
                operations += 1

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "psycopg2",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
    }


@router.get("/benchmark/parallel")
def benchmark_parallel(count: int = 100, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that performs multiple database operations in parallel using psycopg2."""
    start_time = time.time()
    operations = 0

    # Define query functions
    def query_users():
        return db.query(User).all()

    def query_products():
        return db.query(Product).filter(Product.price > 10.0).order_by(Product.price.desc()).all()

    def query_users_with_filter():
        return db.query(User).filter(User.username.like("user%")).all()

    def query_products_with_join():
        # Simulate a more complex query with a join
        return db.query(Product, User).join(User, Product.id == User.id, isouter=True).filter(Product.price > 5.0).all()

    # Run queries in parallel batches using ThreadPoolExecutor
    for _ in range(count):
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Execute 4 queries in parallel
            futures = [
                executor.submit(query_users),
                executor.submit(query_products),
                executor.submit(query_users_with_filter),
                executor.submit(query_products_with_join),
            ]

            # Wait for all futures to complete and get results
            for future in futures:
                future.result()  # Ensure results are consumed

            operations += 4  # 4 queries per iteration

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "psycopg2",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "parallel": True,
    }


@router.get("/benchmark/complex")
def benchmark_complex(count: int = 100, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that performs complex database operations using psycopg2."""
    start_time = time.time()
    operations = 0

    for _ in range(count):
        # Complex query 1: Aggregation with group by
        db.query(
            User.full_name, func.count(Product.id).label("product_count"), func.avg(Product.price).label("avg_price")
        ).select_from(User).join(Product, User.id == Product.id, isouter=True).group_by(User.full_name).having(
            func.avg(Product.price) > 0
        ).all()
        operations += 1

        # Complex query 2: Subquery with order by
        subq = db.query(Product.id, func.rank().over(order_by=Product.price.desc()).label("price_rank")).subquery()

        db.query(Product).join(subq, Product.id == subq.c.id).filter(subq.c.price_rank <= 5).all()
        operations += 1

        # Complex query 3: Window functions
        db.query(User.username, User.email, func.row_number().over(order_by=User.username).label("row_num")).all()
        operations += 1

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = operations / execution_time

    return {
        "database": "psycopg2",
        "operations": operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "complex": True,
    }


@router.get("/benchmark/concurrent")
def benchmark_concurrent(count: int = 100, concurrency: int = 10, db: Session = Depends(get_db_sync)):
    """Benchmark endpoint that simulates concurrent database operations using psycopg2."""
    start_time = time.time()

    # Thread-local storage for results
    results = []

    # Define a function that performs database operations
    def db_task(task_id):
        # Get a new session for this thread
        from db.sync_db import SessionLocal

        thread_db = SessionLocal()
        task_operations = 0

        try:
            # Perform a mix of operations
            for i in range(count // concurrency):
                # SELECT operation
                thread_db.query(User).filter(User.id > task_id % 5).all()
                thread_db.query(Product).filter(Product.price > 10 + task_id % 10).all()
                task_operations += 2

                # More complex SELECT
                thread_db.query(User, Product).outerjoin(Product, User.id == Product.id).all()
                task_operations += 1

            return task_operations
        finally:
            thread_db.close()

    # Create and run concurrent threads
    threads = []
    for i in range(concurrency):
        thread = threading.Thread(target=lambda i=i: results.append(db_task(i)))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Sum up all operations
    total_operations = sum(results)

    # Get execution time
    execution_time = time.time() - start_time

    # Avoid division by zero
    operations_per_second = 0
    if execution_time > 0:
        operations_per_second = total_operations / execution_time

    return {
        "database": "psycopg2",
        "operations": total_operations,
        "execution_time_seconds": execution_time,
        "operations_per_second": operations_per_second,
        "concurrency": concurrency,
    }
