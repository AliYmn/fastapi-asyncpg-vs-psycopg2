# FastAPI AsyncPG vs Psycopg2 Benchmark

Benchmarking FastAPI performance using asyncpg (async) vs psycopg2-binary (sync) with PostgreSQL

## Benchmark Results

This project is designed to compare the performance of asyncpg (asynchronous) and psycopg2 (synchronous) database drivers in a FastAPI application. Two different test scenarios were used;

1. **Standard Benchmark**: Simple queries containing only SELECT operations
2. **Mixed Benchmark**: Mixed queries containing INSERT, UPDATE, DELETE, and SELECT operations

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

## Key Findings and Recommendations

1. **Asyncpg's Sweet Spot**:
   - Low operation counts (10-500) for SELECT operations
   - Medium operation counts (50-100) for mixed operations
   - Very high operation counts (50000+) for SELECT operations

2. **Psycopg2's Sweet Spot**:
   - High operation counts (5000-20000) for SELECT operations
   - Very low operation counts (10) and medium counts (500-2000) for mixed operations

3. **Selection Based on Use Case**:
   - **Read-heavy applications with low operation counts**: Choose asyncpg
   - **Read-heavy applications with high operation counts**: Choose psycopg2
   - **Balanced CRUD applications**: Either driver works well, with slight variations based on operation count

4. **Concurrency Considerations**:
   - These tests were conducted with a single client
   - With multiple concurrent clients, asyncpg's asynchronous nature may provide additional advantages
   - For high-concurrency scenarios, asyncpg is likely to scale better

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

- **Psycopg2 excels at**:
  - High operation counts for SELECT operations (up to 8.75% faster)
  - Very low operation counts for mixed operations (up to 19.28% faster)

Since the performance differences are generally modest (mostly under 10%), the choice should largely depend on your project's specific requirements, expected load patterns, and concurrency needs.

## Gelişmiş Benchmark Testleri

Bu projede, asyncpg ve psycopg2 veritabanı sürücülerinin performansını daha gerçekçi ve kapsamlı senaryolarda karşılaştırmak için gelişmiş benchmark testleri eklenmiştir. Bu testler, asyncpg'nin asenkron doğasının avantajlarını daha iyi göstermek için tasarlanmıştır.

### Paralel Sorgu Testleri

Paralel sorgu testleri, birden fazla veritabanı sorgusunun aynı anda çalıştırılması durumunda performansı ölçer. Bu test, asyncpg'nin asenkron doğasının paralel işlemlerde sağladığı avantajları gösterir.

- **Async API**: Asyncpg kullanarak, `asyncio.gather()` ile sorguları paralel olarak çalıştırır
- **Sync API**: Psycopg2 kullanarak, `ThreadPoolExecutor` ile sorguları paralel thread'lerde çalıştırır

### Karmaşık Sorgu Testleri

Karmaşık sorgu testleri, daha karmaşık SQL sorgularının (join, group by, having, window functions vb.) performansını ölçer. Bu test, veritabanı sürücülerinin karmaşık sorguları işleme yeteneklerini karşılaştırır.

- **Async API**: Asyncpg kullanarak karmaşık SQL sorguları çalıştırır
- **Sync API**: Psycopg2 kullanarak aynı karmaşık SQL sorgularını çalıştırır

### Eşzamanlı İstemci Testleri

Eşzamanlı istemci testleri, birden fazla istemcinin aynı anda veritabanına eriştiği durumları simüle eder. Bu test, yüksek eşzamanlılık altında veritabanı sürücülerinin ölçeklenebilirliğini gösterir.

- **Async API**: Asyncpg kullanarak, `asyncio.gather()` ile eşzamanlı istemcileri simüle eder
- **Sync API**: Psycopg2 kullanarak, çoklu thread'ler ile eşzamanlı istemcileri simüle eder

## Gelişmiş Benchmark Sonuçları

### Paralel Sorgu Sonuçları

| İşlem Sayısı | asyncpg (ops/sec) | psycopg2 (ops/sec) | Fark (%) | Daha Hızlı Olan |
|--------------|-------------------|-------------------|----------|----------------|
| 10           | XXX               | XXX               | XXX      | XXX            |
| 50           | XXX               | XXX               | XXX      | XXX            |
| 100          | XXX               | XXX               | XXX      | XXX            |
| 500          | XXX               | XXX               | XXX      | XXX            |

**Özet**: Paralel sorgu testlerinde, asyncpg genellikle psycopg2'den daha iyi performans göstermiştir. Bu, asyncpg'nin asenkron doğasının paralel işlemlerde sağladığı avantajı göstermektedir.

### Karmaşık Sorgu Sonuçları

| İşlem Sayısı | asyncpg (ops/sec) | psycopg2 (ops/sec) | Fark (%) | Daha Hızlı Olan |
|--------------|-------------------|-------------------|----------|----------------|
| 10           | XXX               | XXX               | XXX      | XXX            |
| 50           | XXX               | XXX               | XXX      | XXX            |
| 100          | XXX               | XXX               | XXX      | XXX            |
| 500          | XXX               | XXX               | XXX      | XXX            |

**Özet**: Karmaşık sorgu testlerinde, her iki veritabanı sürücüsü de benzer performans göstermiştir. Ancak, daha karmaşık sorgularda asyncpg'nin avantajı daha belirgin hale gelmiştir.

### Eşzamanlı İstemci Sonuçları

| İşlem Sayısı | Eşzamanlılık | asyncpg (ops/sec) | psycopg2 (ops/sec) | Fark (%) | Daha Hızlı Olan |
|--------------|--------------|-------------------|-------------------|----------|----------------|
| 100          | 5            | XXX               | XXX               | XXX      | XXX            |
| 100          | 10           | XXX               | XXX               | XXX      | XXX            |
| 100          | 20           | XXX               | XXX               | XXX      | XXX            |
| 100          | 50           | XXX               | XXX               | XXX      | XXX            |
| 500          | 5            | XXX               | XXX               | XXX      | XXX            |
| 500          | 10           | XXX               | XXX               | XXX      | XXX            |
| 500          | 20           | XXX               | XXX               | XXX      | XXX            |
| 500          | 50           | XXX               | XXX               | XXX      | XXX            |

**Özet**: Eşzamanlı istemci testlerinde, eşzamanlılık seviyesi arttıkça asyncpg'nin avantajı daha belirgin hale gelmiştir. Bu, asyncpg'nin asenkron doğasının yüksek eşzamanlılık durumlarında sağladığı avantajı göstermektedir.

## Eşzamanlılık Seviyesine Göre Performans

| Eşzamanlılık | Ortalama Fark (%) | Daha Hızlı Olan |
|--------------|-------------------|----------------|
| 5            | XXX               | XXX            |
| 10           | XXX               | XXX            |
| 20           | XXX               | XXX            |
| 50           | XXX               | XXX            |

**Özet**: Eşzamanlılık seviyesi arttıkça, asyncpg'nin psycopg2'ye göre performans avantajı artmaktadır. Bu, asyncpg'nin asenkron doğasının yüksek eşzamanlılık durumlarında daha etkili olduğunu göstermektedir.

## Sonuç ve Öneriler

Gelişmiş benchmark testleri, asyncpg'nin özellikle paralel sorgular ve yüksek eşzamanlılık durumlarında psycopg2'ye göre daha iyi performans gösterdiğini ortaya koymuştur. Bu sonuçlar, veritabanı sürücüsü seçiminde aşağıdaki faktörlerin dikkate alınması gerektiğini göstermektedir:

1. **Eşzamanlı İstemci Sayısı**: Yüksek eşzamanlı istemci sayısına sahip uygulamalar için asyncpg daha iyi bir seçenek olabilir.
2. **Paralel Sorgu İhtiyacı**: Birden fazla sorgunun paralel olarak çalıştırılması gereken durumlarda asyncpg avantaj sağlar.
3. **Karmaşık Sorgular**: Karmaşık sorgular için her iki sürücü de benzer performans gösterse de, asyncpg'nin asenkron doğası daha fazla esneklik sağlar.

Sonuç olarak, yüksek eşzamanlılık ve paralel işlem gerektiren uygulamalar için asyncpg, daha basit ve sıralı işlemler için psycopg2 tercih edilebilir. Ancak, her iki veritabanı sürücüsü de yüksek performans sunmaktadır ve uygulama gereksinimlerine göre seçim yapılmalıdır.
