# FastAPI AsyncPG vs Psycopg2 Benchmark

Benchmarking FastAPI performance using asyncpg (async) vs psycopg2-binary (sync) with PostgreSQL

## Project Overview

This project compares the performance of two popular PostgreSQL database drivers in a FastAPI application:
- **asyncpg**: An asynchronous PostgreSQL driver
- **psycopg2**: A synchronous PostgreSQL driver

The goal is to provide data-driven insights to help developers choose the most appropriate driver for their specific use cases.

## Benchmark Results

Three different test scenarios were used to evaluate performance:

1. **Standard Benchmark**: Simple queries containing only SELECT operations
2. **Mixed Benchmark**: Mixed queries containing INSERT, UPDATE, DELETE, and SELECT operations
3. **Advanced Benchmark**: Complex queries, parallel operations, and concurrent client tests

### Standard Benchmark Results (SELECT Operations)

Operations per second (higher is better):

| Operation Count | Asyncpg (ops/s) | Psycopg2 (ops/s) | Diff % | Faster | Notes |
|-----------------|-----------------|------------------|--------|--------|-------|
| 10              | 3801.29         | 3451.66          | +10.13% | asyncpg | Significant advantage for asyncpg |
| 50              | 5328.41         | 4602.99          | +15.76% | asyncpg | **Largest advantage** for asyncpg in any test |
| 100             | 5236.95         | 5140.69          | +1.87%  | asyncpg | Small advantage for asyncpg |
| 500             | 5229.45         | 5106.91          | +2.40%  | asyncpg | Small advantage for asyncpg |
| 1000            | 5189.18         | 5236.20          | -0.90%  | psycopg2 | Very slight advantage for psycopg2 |
| 2000            | 5202.93         | 5167.63          | +0.68%  | asyncpg | Very slight advantage for asyncpg |
| 5000            | 4881.89         | 5238.65          | -6.81%  | psycopg2 | Moderate advantage for psycopg2 |
| 10000           | 4899.33         | 5368.84          | -8.75%  | psycopg2 | **Largest advantage** for psycopg2 in SELECT tests |
| 20000           | 5091.14         | 5196.03          | -2.02%  | psycopg2 | Small advantage for psycopg2 |
| 50000           | 5180.29         | 5113.43          | +1.31%  | asyncpg | Asyncpg regains a small advantage at very high counts |

![Standard Benchmark Results](./images/Standard%20Benchmark.png)

### Mixed Benchmark Results (INSERT, UPDATE, DELETE, SELECT)

Operations per second (higher is better):

| Operation Count | Asyncpg (ops/s) | Psycopg2 (ops/s) | Diff % | Faster | Notes |
|-----------------|-----------------|------------------|--------|--------|-------|
| 10              | 1369.80         | 1696.97          | -19.28% | psycopg2 | **Largest difference** in any test, strongly favoring psycopg2 |
| 50              | 2116.49         | 2025.60          | +4.49%  | asyncpg | Moderate advantage for asyncpg |
| 100             | 2175.55         | 2071.04          | +5.05%  | asyncpg | **Largest advantage** for asyncpg in mixed tests |
| 500             | 1945.09         | 2056.38          | -5.41%  | psycopg2 | Moderate advantage for psycopg2 |
| 1000            | 2143.12         | 2137.40          | +0.27%  | asyncpg | Nearly identical performance |
| 2000            | 1994.93         | 2160.55          | -7.67%  | psycopg2 | Significant advantage for psycopg2 |
| 5000            | 2107.17         | 2119.35          | -0.57%  | psycopg2 | Nearly identical performance |
| 10000           | 2192.66         | 2152.99          | +1.84%  | asyncpg | Small advantage for asyncpg |

![Mixed Benchmark Results](./images/Mixed%20Benchmark.png)

### Advanced Benchmark Results

#### Parallel Operations Benchmark (10,000 operations)

| Database Driver | Operations per second | Comparison |
|-----------------|----------------------|------------|
| asyncpg         | 1,612.77             | +17.88%    |
| psycopg2        | 1,368.14             | baseline   |

**Analysis**: At high operation counts (10,000), asyncpg outperforms psycopg2 by 17.88% in parallel operations. This demonstrates asyncpg's advantage in handling multiple concurrent database operations.

#### Complex Query Benchmark (10,000 operations)

| Database Driver | Operations per second | Comparison |
|-----------------|----------------------|------------|
| asyncpg         | 2,538.99             | +12.61%    |
| psycopg2        | 2,254.68             | baseline   |

**Analysis**: For complex queries with joins and filters at high operation counts (10,000), asyncpg shows a 12.61% performance advantage over psycopg2.

#### Concurrent Client Benchmark (100,000 operations, 5 concurrent clients)

| Database Driver | Operations per second | Comparison |
|-----------------|----------------------|------------|
| asyncpg         | 2,400.94             | +1.95%     |
| psycopg2        | 2,355.13             | baseline   |

**Analysis**: With multiple concurrent clients and very high operation counts (100,000), asyncpg maintains a slight advantage (1.95%) over psycopg2.

![Advanced Benchmark Results](./images/Advanced%20Benchmark.png)

## Analysis and Results

### Standard Benchmark Analysis (SELECT Operations)

1. **Low Operation Counts (10-500)**:
   - Asyncpg consistently outperforms psycopg2
   - Performance advantage ranges from +1.87% to +15.76%
   - Most significant advantage at 50 operations (+15.76%)

2. **Medium Operation Counts (1000-5000)**:
   - Mixed results with both drivers showing advantages
   - Psycopg2 shows up to 6.81% better performance at 5000 operations
   - Asyncpg maintains a slight edge at 2000 operations (+0.68%)

3. **High Operation Counts (10000-50000)**:
   - Psycopg2 dominates at 10000-20000 operations (up to 8.75% faster)
   - Asyncpg regains advantage at 50000 operations (+1.31%)

### Mixed Benchmark Analysis (INSERT, UPDATE, DELETE, SELECT)

1. **Overall Performance**:
   - Both drivers show lower performance compared to SELECT-only operations
   - Performance drops by approximately 60% (from ~5000-5300 ops/s to ~2000-2200 ops/s)

2. **Performance Pattern**:
   - More variable results than SELECT-only tests
   - Psycopg2 shows strongest advantage at very low counts (10 operations: -19.28%)
   - Asyncpg performs best at 100 operations (+5.05%)
   - At high counts (10000), asyncpg regains a small advantage (+1.84%)

3. **Consistency**:
   - Less consistent pattern than SELECT-only operations
   - Performance differences fluctuate more between operation counts
   - At 1000 and 5000 operations, performance is nearly identical (differences < 1%)

### Advanced Benchmark Analysis

1. **Parallel Operations**:
   - Asyncpg shows a significant advantage (17.88%) at high operation counts
   - This demonstrates asyncpg's strength in handling multiple parallel database operations
   - The asynchronous nature of asyncpg allows for better resource utilization in parallel scenarios

2. **Complex Queries**:
   - Asyncpg outperforms psycopg2 by 12.61% for complex queries at high operation counts
   - This suggests that asyncpg's connection pooling and async execution model provides benefits for complex database operations

3. **Concurrent Clients**:
   - With multiple concurrent clients, asyncpg maintains a slight advantage (1.95%)
   - This indicates that asyncpg scales well with increased concurrency
   - The difference is smaller than in other tests, suggesting that both drivers handle concurrency well at this level

## Key Findings and Recommendations

1. **Asyncpg's Sweet Spot**:
   - Low operation counts (10-500) for SELECT operations
   - Medium operation counts (50-100) for mixed operations
   - Very high operation counts (50000+) for SELECT operations
   - Parallel operations and complex queries at high operation counts
   - Applications with high concurrency requirements

2. **Psycopg2's Sweet Spot**:
   - High operation counts (5000-20000) for SELECT operations
   - Very low operation counts (10) and medium counts (500-2000) for mixed operations
   - Applications with simpler query patterns and lower concurrency needs

3. **Selection Based on Use Case**:
   - **Read-heavy applications with low operation counts**: Choose asyncpg
   - **Read-heavy applications with high operation counts**: Consider psycopg2, but test with your specific workload
   - **Balanced CRUD applications**: Either driver works well, with slight variations based on operation count
   - **Applications with complex queries and high parallelism**: Asyncpg shows clear advantages

4. **Concurrency Considerations**:
   - With multiple concurrent clients, asyncpg's asynchronous nature provides measurable advantages
   - For high-concurrency scenarios, asyncpg is likely to scale better
   - The performance gap widens in favor of asyncpg as operation complexity and parallelism increase

## Project Structure

- `api/async_api`: Asynchronous API endpoints using asyncpg
- `api/sync_api`: Synchronous API endpoints using psycopg2
- `models`: Database models (User, Product)
- `db`: Database connection configurations
- `benchmark_test.py`: Script that runs benchmark tests

## How to Run

1. To run with Docker:
   ```bash
   docker-compose up -d
   ```

2. To run benchmark tests:
   ```bash
   python benchmark_test.py
   ```

3. Results are saved to the `benchmark_report.json` file.

## Conclusion

Both database drivers offer high performance with specific advantages in different scenarios:

- **Asyncpg excels at**:
  - Low operation counts (up to 15.76% faster)
  - Very high operation counts for SELECT operations
  - Potentially better scalability for concurrent access
  - Parallel operations and complex queries (up to 17.88% faster)

- **Psycopg2 excels at**:
  - High operation counts for SELECT operations (up to 8.75% faster)
  - Very low operation counts for mixed operations (up to 19.28% faster)

Since the performance differences are generally modest (mostly under 10%), the choice should largely depend on your project's specific requirements, expected load patterns, and concurrency needs. For applications with high concurrency and complex queries, asyncpg provides measurable advantages that may be worth considering.
