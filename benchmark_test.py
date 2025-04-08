import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median, stdev

import aiohttp
import requests


async def async_request(session, url, count):
    """Make an async request to the benchmark endpoint."""
    params = {"count": count}
    async with session.get(url, params=params) as response:
        return await response.json()


async def run_async_tests(base_url, counts, iterations):
    """Run async tests with different counts and iterations."""
    results = []

    async with aiohttp.ClientSession() as session:
        for count in counts:
            count_results = []
            for _ in range(iterations):
                start_time = time.time()
                result = await async_request(session, f"{base_url}/async/benchmark", count)
                end_time = time.time()

                # Calculate total time including network latency
                total_time = end_time - start_time

                count_results.append(
                    {
                        "count": count,
                        "db_execution_time": result["execution_time_seconds"],
                        "total_time": total_time,
                        "operations_per_second": result["operations_per_second"],
                    }
                )

            results.append(count_results)

    return results


async def run_async_mixed_tests(base_url, counts, iterations):
    """Run async mixed operation tests with different counts and iterations."""
    results = []

    async with aiohttp.ClientSession() as session:
        for count in counts:
            count_results = []
            for _ in range(iterations):
                start_time = time.time()
                result = await async_request(session, f"{base_url}/async/benchmark/mixed", count)
                end_time = time.time()

                # Calculate total time including network latency
                total_time = end_time - start_time

                count_results.append(
                    {
                        "count": count,
                        "db_execution_time": result["execution_time_seconds"],
                        "total_time": total_time,
                        "operations_per_second": result["operations_per_second"],
                        "operations": result["operations"],
                    }
                )

            results.append(count_results)

    return results


def sync_request(url, count):
    """Make a sync request to the benchmark endpoint."""
    params = {"count": count}
    response = requests.get(url, params=params)
    return response.json()


def run_sync_tests(base_url, counts, iterations):
    """Run sync tests with different counts and iterations."""
    results = []

    for count in counts:
        count_results = []
        for _ in range(iterations):
            start_time = time.time()
            result = sync_request(f"{base_url}/sync/benchmark", count)
            end_time = time.time()

            # Calculate total time including network latency
            total_time = end_time - start_time

            count_results.append(
                {
                    "count": count,
                    "db_execution_time": result["execution_time_seconds"],
                    "total_time": total_time,
                    "operations_per_second": result["operations_per_second"],
                }
            )

        results.append(count_results)

    return results


def run_sync_mixed_tests(base_url, counts, iterations):
    """Run sync mixed operation tests with different counts and iterations."""
    results = []

    for count in counts:
        count_results = []
        for _ in range(iterations):
            start_time = time.time()
            result = sync_request(f"{base_url}/sync/benchmark/mixed", count)
            end_time = time.time()

            # Calculate total time including network latency
            total_time = end_time - start_time

            count_results.append(
                {
                    "count": count,
                    "db_execution_time": result["execution_time_seconds"],
                    "total_time": total_time,
                    "operations_per_second": result["operations_per_second"],
                    "operations": result["operations"],
                }
            )

        results.append(count_results)

    return results


def analyze_results(results, test_type):
    """Analyze test results and return statistics."""
    analysis = []

    for count_results in results:
        if not count_results:
            continue

        count = count_results[0]["count"]
        db_times = [r["db_execution_time"] for r in count_results]
        total_times = [r["total_time"] for r in count_results]
        ops_per_second = [r["operations_per_second"] for r in count_results]

        # Get operations count if available (for mixed tests)
        operations = count_results[0].get("operations", count * 2)

        analysis.append(
            {
                "test_type": test_type,
                "count": count,
                "operations": operations,
                "iterations": len(count_results),
                "db_execution_time": {
                    "mean": mean(db_times),
                    "median": median(db_times),
                    "min": min(db_times),
                    "max": max(db_times),
                    "stdev": stdev(db_times) if len(db_times) > 1 else 0,
                },
                "total_time": {
                    "mean": mean(total_times),
                    "median": median(total_times),
                    "min": min(total_times),
                    "max": max(total_times),
                    "stdev": stdev(total_times) if len(total_times) > 1 else 0,
                },
                "operations_per_second": {
                    "mean": mean(ops_per_second),
                    "median": median(ops_per_second),
                    "min": min(ops_per_second),
                    "max": max(ops_per_second),
                    "stdev": stdev(ops_per_second) if len(ops_per_second) > 1 else 0,
                },
            }
        )

    return analysis


def generate_report(async_analysis, sync_analysis, test_type="standard"):
    """Generate a comparison report between async and sync results."""
    report = {"test_type": test_type, "async_results": async_analysis, "sync_results": sync_analysis, "comparison": []}

    # Match async and sync results by count for comparison
    for async_result in async_analysis:
        count = async_result["count"]
        sync_result = next((r for r in sync_analysis if r["count"] == count), None)

        if sync_result:
            # Calculate performance difference
            async_mean_ops = async_result["operations_per_second"]["mean"]
            sync_mean_ops = sync_result["operations_per_second"]["mean"]

            if sync_mean_ops > 0:
                performance_diff_percent = ((async_mean_ops - sync_mean_ops) / sync_mean_ops) * 100
            else:
                performance_diff_percent = float("inf") if async_mean_ops > 0 else 0

            report["comparison"].append(
                {
                    "count": count,
                    "operations": async_result.get("operations", count * 2),
                    "async_ops_per_second": async_mean_ops,
                    "sync_ops_per_second": sync_mean_ops,
                    "performance_difference_percent": performance_diff_percent,
                    "faster": "async" if async_mean_ops > sync_mean_ops else "sync",
                }
            )

    return report


def print_comparison_table(report):
    """Print a formatted comparison table for the report."""
    print(f"\n=== {report['test_type'].upper()} BENCHMARK RESULTS SUMMARY ===\n")
    print("Operations per second (higher is better):\n")

    print(f"{'Count':<10} {'Asyncpg':<15} {'Psycopg2':<15} {'Diff %':<10} {'Faster'}")
    print("-" * 60)

    for comp in sorted(report["comparison"], key=lambda x: x["count"]):
        diff_percent = f"{comp['performance_difference_percent']:.2f}%"
        print(
            f"{comp['count']:<10} {comp['async_ops_per_second']:<15.2f} {comp['sync_ops_per_second']:<15.2f} "
            f"{diff_percent:<10} {comp['faster']}"
        )


async def main():
    """Run benchmark tests and generate report."""
    base_url = "http://localhost:8000"

    # Define test parameters
    # Standard select-only tests
    standard_counts = [10, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    standard_iterations = 3

    # Mixed operation tests (INSERT, UPDATE, DELETE, GET)
    # Using smaller counts for mixed tests as they are more resource-intensive
    mixed_counts = [10, 50, 100, 500, 1000, 2000, 5000, 10000]
    mixed_iterations = 3

    print(
        f"Running standard benchmark tests with counts {standard_counts} and {standard_iterations} iterations each..."
    )
    print(f"Running mixed benchmark tests with counts {mixed_counts} and {mixed_iterations} iterations each...")

    print("Creating test data...")
    for i in range(20):
        requests.post(
            f"{base_url}/async/users",
            params={"username": f"user{i}", "email": f"user{i}@example.com", "full_name": f"Test User {i}"},
        )
        requests.post(
            f"{base_url}/async/products",
            params={"name": f"Product {i}", "price": 10.99 + i, "sku": f"SKU{i}", "description": f"Test product {i}"},
        )

    # Run standard tests (SELECT operations only)
    print("\nRunning standard async tests...")
    async_results = await run_async_tests(base_url, standard_counts, standard_iterations)

    print("Running standard sync tests...")
    with ThreadPoolExecutor() as executor:
        sync_results = await asyncio.get_event_loop().run_in_executor(
            executor, run_sync_tests, base_url, standard_counts, standard_iterations
        )

    print("Analyzing standard results...")
    async_analysis = analyze_results(async_results, "asyncpg")
    sync_analysis = analyze_results(sync_results, "psycopg2")

    print("Generating standard report...")
    standard_report = generate_report(async_analysis, sync_analysis, "standard")

    # Run mixed tests (INSERT, UPDATE, DELETE, GET)
    print("\nRunning mixed async tests...")
    async_mixed_results = await run_async_mixed_tests(base_url, mixed_counts, mixed_iterations)

    print("Running mixed sync tests...")
    with ThreadPoolExecutor() as executor:
        sync_mixed_results = await asyncio.get_event_loop().run_in_executor(
            executor, run_sync_mixed_tests, base_url, mixed_counts, mixed_iterations
        )

    print("Analyzing mixed results...")
    async_mixed_analysis = analyze_results(async_mixed_results, "asyncpg_mixed")
    sync_mixed_analysis = analyze_results(sync_mixed_results, "psycopg2_mixed")

    print("Generating mixed report...")
    mixed_report = generate_report(async_mixed_analysis, sync_mixed_analysis, "mixed")

    # Save combined report to file
    combined_report = {
        "standard_tests": standard_report,
        "mixed_tests": mixed_report,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open("benchmark_report.json", "w") as f:
        json.dump(combined_report, f, indent=2)

    # Print summary tables
    print_comparison_table(standard_report)
    print_comparison_table(mixed_report)

    print("\nBenchmark complete! Full results saved to benchmark_report.json")


if __name__ == "__main__":
    asyncio.run(main())
