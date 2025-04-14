import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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
    async_wins = 0
    sync_wins = 0
    total_diff_percent = 0
    comparison_count = 0

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

            # Track wins and total difference for summary
            if async_mean_ops > sync_mean_ops:
                async_wins += 1
            else:
                sync_wins += 1

            total_diff_percent += performance_diff_percent
            comparison_count += 1

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

    # Add summary section
    report["summary"] = {
        "overall_faster": "async" if async_wins > sync_wins else "sync",
        "async_wins": async_wins,
        "sync_wins": sync_wins,
        "avg_percentage_diff": total_diff_percent / comparison_count if comparison_count > 0 else 0,
    }

    return report


def print_comparison_table(report):
    """Print a formatted comparison table for the report."""
    print(f"\n=== {report['test_type'].upper()} BENCHMARK RESULTS SUMMARY ===\n")
    print("Operations per second (higher is better):\n")

    print(f"{'Count':<10} {'Async':<15} {'Sync':<15} {'Diff %':<10} {'Faster'}")
    print("-" * 60)

    for comp in sorted(report["comparison"], key=lambda x: x["count"]):
        diff_percent = f"{comp['performance_difference_percent']:.2f}%"
        print(
            f"{comp['count']:<10} {comp['async_ops_per_second']:<15.2f} {comp['sync_ops_per_second']:<15.2f} "
            f"{diff_percent:<10} {comp['faster']}"
        )


async def run_advanced_benchmarks():
    """Run advanced benchmarks for both async and sync APIs."""
    print("Running advanced benchmarks...")

    # Test configurations
    test_counts = [10000]  # Increased to 10k
    concurrency_levels = [5]

    # Results storage
    results = {
        "parallel": {"async": {}, "sync": {}},
        "complex": {"async": {}, "sync": {}},
        "concurrent": {"async": {}, "sync": {}},
    }

    try:
        # Run parallel benchmarks
        print("\nRunning parallel benchmarks...")
        for count in test_counts:
            print(f"  Testing with {count} operations...")

            try:
                # Async API
                url = f"http://localhost:8000/async/benchmark/parallel?count={count}"
                async_response = requests.get(url)
                if async_response.status_code == 200:
                    async_result = async_response.json()
                    results["parallel"]["async"][count] = async_result
                else:
                    print(f"    Error with async parallel benchmark: {async_response.status_code}")
                    results["parallel"]["async"][count] = {"error": f"HTTP {async_response.status_code}"}

                # Sync API
                url = f"http://localhost:8000/sync/benchmark/parallel?count={count}"
                sync_response = requests.get(url)
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    results["parallel"]["sync"][count] = sync_result
                else:
                    print(f"    Error with sync parallel benchmark: {sync_response.status_code}")
                    results["parallel"]["sync"][count] = {"error": f"HTTP {sync_response.status_code}"}

                # Calculate percentage difference if both results are available
                if async_response.status_code == 200 and sync_response.status_code == 200:
                    async_ops = async_result["operations_per_second"]
                    sync_ops = sync_result["operations_per_second"]

                    if sync_ops > 0:
                        percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                        print(f"    asyncpg: {async_ops:.2f} ops/sec, psycopg2: {sync_ops:.2f} ops/sec")
                        print(
                            f"    Difference: {percentage_diff:.2f}% ({'asyncpg faster' if percentage_diff > 0 else 'psycopg2 faster'})"
                        )
            except Exception as e:
                print(f"    Error running parallel benchmark with count {count}: {str(e)}")
                results["parallel"]["async"][count] = {"error": str(e)}
                results["parallel"]["sync"][count] = {"error": str(e)}

        # Run complex benchmarks
        print("\nRunning complex query benchmarks...")
        for count in test_counts:
            print(f"  Testing with {count} operations...")

            try:
                # Async API
                url = f"http://localhost:8000/async/benchmark/complex?count={count}"
                async_response = requests.get(url)
                if async_response.status_code == 200:
                    async_result = async_response.json()
                    results["complex"]["async"][count] = async_result
                else:
                    print(f"    Error with async complex benchmark: {async_response.status_code}")
                    results["complex"]["async"][count] = {"error": f"HTTP {async_response.status_code}"}

                # Sync API
                url = f"http://localhost:8000/sync/benchmark/complex?count={count}"
                sync_response = requests.get(url)
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    results["complex"]["sync"][count] = sync_result
                else:
                    print(f"    Error with sync complex benchmark: {sync_response.status_code}")
                    results["complex"]["sync"][count] = {"error": f"HTTP {sync_response.status_code}"}

                # Calculate percentage difference if both results are available
                if async_response.status_code == 200 and sync_response.status_code == 200:
                    async_ops = async_result["operations_per_second"]
                    sync_ops = sync_result["operations_per_second"]

                    if sync_ops > 0:
                        percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                        print(f"    asyncpg: {async_ops:.2f} ops/sec, psycopg2: {sync_ops:.2f} ops/sec")
                        print(
                            f"    Difference: {percentage_diff:.2f}% ({'asyncpg faster' if percentage_diff > 0 else 'psycopg2 faster'})"
                        )
            except Exception as e:
                print(f"    Error running complex benchmark with count {count}: {str(e)}")
                results["complex"]["async"][count] = {"error": str(e)}
                results["complex"]["sync"][count] = {"error": str(e)}

        # Run concurrent benchmarks
        print("\nRunning concurrent benchmarks...")
        for count in [100000]:  # Increased to 100k
            for concurrency in concurrency_levels:
                print(f"  Testing with {count} operations and {concurrency} concurrent clients...")

                try:
                    # Async API
                    url = f"http://localhost:8000/async/benchmark/concurrent?count={count}&concurrency={concurrency}"
                    async_response = requests.get(url)
                    if async_response.status_code == 200:
                        async_result = async_response.json()
                        if count not in results["concurrent"]["async"]:
                            results["concurrent"]["async"][count] = {}
                        results["concurrent"]["async"][count][concurrency] = async_result
                    else:
                        print(f"    Error with async concurrent benchmark: {async_response.status_code}")
                        if count not in results["concurrent"]["async"]:
                            results["concurrent"]["async"][count] = {}
                        results["concurrent"]["async"][count][concurrency] = {
                            "error": f"HTTP {async_response.status_code}"
                        }

                    # Sync API
                    url = f"http://localhost:8000/sync/benchmark/concurrent?count={count}&concurrency={concurrency}"
                    sync_response = requests.get(url)
                    if sync_response.status_code == 200:
                        sync_result = sync_response.json()
                        if count not in results["concurrent"]["sync"]:
                            results["concurrent"]["sync"][count] = {}
                        results["concurrent"]["sync"][count][concurrency] = sync_result
                    else:
                        print(f"    Error with sync concurrent benchmark: {sync_response.status_code}")
                        if count not in results["concurrent"]["sync"]:
                            results["concurrent"]["sync"][count] = {}
                        results["concurrent"]["sync"][count][concurrency] = {
                            "error": f"HTTP {sync_response.status_code}"
                        }

                    # Calculate percentage difference if both results are available
                    if async_response.status_code == 200 and sync_response.status_code == 200:
                        async_ops = async_result["operations_per_second"]
                        sync_ops = sync_result["operations_per_second"]

                        if sync_ops > 0:
                            percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                            print(f"    asyncpg: {async_ops:.2f} ops/sec, psycopg2: {sync_ops:.2f} ops/sec")
                            print(
                                f"    Difference: {percentage_diff:.2f}% ({'asyncpg faster' if percentage_diff > 0 else 'psycopg2 faster'})"
                            )
                except Exception as e:
                    err_msg = f"    Error running concurrent benchmark with count {count} and concurrency {concurrency}: {str(e)}"
                    print(err_msg)
                    if count not in results["concurrent"]["async"]:
                        results["concurrent"]["async"][count] = {}
                    if count not in results["concurrent"]["sync"]:
                        results["concurrent"]["sync"][count] = {}
                    results["concurrent"]["async"][count][concurrency] = {"error": str(e)}
                    results["concurrent"]["sync"][count][concurrency] = {"error": str(e)}
    except Exception as e:
        print(f"Error running advanced benchmarks: {str(e)}")

    return results


def analyze_advanced_results(results):
    """Analyze the advanced benchmark results."""
    analysis = {
        "parallel": {"overall_faster": None, "avg_percentage_diff": 0, "count_analysis": {}},
        "complex": {"overall_faster": None, "avg_percentage_diff": 0, "count_analysis": {}},
        "concurrent": {
            "overall_faster": None,
            "avg_percentage_diff": 0,
            "count_analysis": {},
            "concurrency_analysis": {},
        },
    }

    # Analyze parallel benchmark results
    async_wins = 0
    sync_wins = 0
    total_diff_percent = 0
    comparison_count = 0

    for count in results["parallel"]["async"]:
        if isinstance(count, int):
            async_result = results["parallel"]["async"][count]
            sync_result = results["parallel"]["sync"][count]

            # Skip error results
            if "error" in async_result or "error" in sync_result:
                continue

            async_ops = async_result.get("operations_per_second", 0)
            sync_ops = sync_result.get("operations_per_second", 0)

            # Avoid division by zero
            if sync_ops > 0:
                percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
            else:
                percentage_diff = 100 if async_ops > 0 else 0

            analysis["parallel"][count] = {
                "async": async_ops,
                "sync": sync_ops,
                "percentage_diff": percentage_diff,
                "faster": "asyncpg" if async_ops > sync_ops else "psycopg2",
            }

            if async_ops > sync_ops:
                async_wins += 1
            else:
                sync_wins += 1

            total_diff_percent += percentage_diff
            comparison_count += 1

    # Set overall results for parallel benchmarks
    if comparison_count > 0:
        analysis["parallel"]["overall_faster"] = "asyncpg" if async_wins > sync_wins else "psycopg2"
        analysis["parallel"]["avg_percentage_diff"] = total_diff_percent / comparison_count
    else:
        analysis["parallel"]["overall_faster"] = "unknown"
        analysis["parallel"]["avg_percentage_diff"] = 0

    # Analyze complex benchmark results
    async_wins = 0
    sync_wins = 0
    total_diff_percent = 0
    comparison_count = 0

    for count in results["complex"]["async"]:
        if isinstance(count, int):
            async_result = results["complex"]["async"][count]
            sync_result = results["complex"]["sync"][count]

            # Skip error results
            if "error" in async_result or "error" in sync_result:
                continue

            async_ops = async_result.get("operations_per_second", 0)
            sync_ops = sync_result.get("operations_per_second", 0)

            # Avoid division by zero
            if sync_ops > 0:
                percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
            else:
                percentage_diff = 100 if async_ops > 0 else 0

            analysis["complex"][count] = {
                "async": async_ops,
                "sync": sync_ops,
                "percentage_diff": percentage_diff,
                "faster": "asyncpg" if async_ops > sync_ops else "psycopg2",
            }

            if async_ops > sync_ops:
                async_wins += 1
            else:
                sync_wins += 1

            total_diff_percent += percentage_diff
            comparison_count += 1

    # Set overall results for complex benchmarks
    if comparison_count > 0:
        analysis["complex"]["overall_faster"] = "asyncpg" if async_wins > sync_wins else "psycopg2"
        analysis["complex"]["avg_percentage_diff"] = total_diff_percent / comparison_count
    else:
        analysis["complex"]["overall_faster"] = "unknown"
        analysis["complex"]["avg_percentage_diff"] = 0

    # Analyze concurrent benchmark results
    async_wins = 0
    sync_wins = 0
    total_diff_percent = 0
    comparison_count = 0

    # Also analyze by concurrency level
    concurrency_analysis = {}

    for count in results["concurrent"]["async"]:
        if isinstance(count, int):
            analysis["concurrent"][count] = {}
            for concurrency, result in results["concurrent"]["async"][count].items():
                sync_result = results["concurrent"]["sync"][count][concurrency]

                # Skip error results
                if "error" in result or "error" in sync_result:
                    continue

                async_ops = result.get("operations_per_second", 0)
                sync_ops = sync_result.get("operations_per_second", 0)

                # Avoid division by zero
                if sync_ops > 0:
                    percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                else:
                    percentage_diff = 100 if async_ops > 0 else 0

                analysis["concurrent"][count][concurrency] = {
                    "async": async_ops,
                    "sync": sync_ops,
                    "percentage_diff": percentage_diff,
                    "faster": "asyncpg" if async_ops > sync_ops else "psycopg2",
                }

                if async_ops > sync_ops:
                    async_wins += 1
                else:
                    sync_wins += 1

                total_diff_percent += percentage_diff
                comparison_count += 1

                # Track by concurrency level
                if concurrency not in concurrency_analysis:
                    concurrency_analysis[concurrency] = {
                        "async_wins": 0,
                        "sync_wins": 0,
                        "total_diff_percent": 0,
                        "comparison_count": 0,
                    }

                if async_ops > sync_ops:
                    concurrency_analysis[concurrency]["async_wins"] += 1
                else:
                    concurrency_analysis[concurrency]["sync_wins"] += 1

                concurrency_analysis[concurrency]["total_diff_percent"] += percentage_diff
                concurrency_analysis[concurrency]["comparison_count"] += 1

    # Set overall results for concurrent benchmarks
    if comparison_count > 0:
        analysis["concurrent"]["overall_faster"] = "asyncpg" if async_wins > sync_wins else "psycopg2"
        analysis["concurrent"]["avg_percentage_diff"] = total_diff_percent / comparison_count
    else:
        analysis["concurrent"]["overall_faster"] = "unknown"
        analysis["concurrent"]["avg_percentage_diff"] = 0

    # Calculate results by concurrency level
    for concurrency, data in concurrency_analysis.items():
        if data["comparison_count"] > 0:
            analysis["concurrent"]["concurrency_analysis"][concurrency] = {
                "overall_faster": "asyncpg" if data["async_wins"] > data["sync_wins"] else "psycopg2",
                "async_wins": data["async_wins"],
                "sync_wins": data["sync_wins"],
                "avg_percentage_diff": data["total_diff_percent"] / data["comparison_count"],
            }
        else:
            analysis["concurrent"]["concurrency_analysis"][concurrency] = {
                "overall_faster": "unknown",
                "async_wins": 0,
                "sync_wins": 0,
                "avg_percentage_diff": 0,
            }

    return analysis


def generate_advanced_report(analysis):
    """Generate a report from the advanced benchmark analysis."""
    report = {
        "parallel": {
            "title": "Parallel Query Benchmark Results",
            "description": "This benchmark tests the performance of executing multiple queries in parallel.",
            "results": analysis["parallel"],
        },
        "complex": {
            "title": "Complex Query Benchmark Results",
            "description": (
                "This benchmark tests the performance of executing complex SQL queries "
                "with joins, aggregations, and window functions."
            ),
            "results": analysis["complex"],
        },
        "concurrent": {
            "title": "Concurrent Client Benchmark Results",
            "description": (
                "This benchmark tests the performance under concurrent load "
                "with multiple clients making requests simultaneously."
            ),
            "results": analysis["concurrent"],
        },
    }

    # Add summary for each benchmark type
    for benchmark_type in ["parallel", "complex", "concurrent"]:
        if benchmark_type != "concurrent":
            # Count how many times each driver was faster
            asyncpg_faster_count = sum(
                1 for result in analysis[benchmark_type].values() if result["faster"] == "asyncpg"
            )
            psycopg2_faster_count = sum(
                1 for result in analysis[benchmark_type].values() if result["faster"] == "psycopg2"
            )
            total_tests = len(analysis[benchmark_type])

            # Calculate average percentage difference
            avg_diff = sum(abs(result["percentage_diff"]) for result in analysis[benchmark_type].values()) / total_tests

            report[benchmark_type]["summary"] = {
                "asyncpg_faster_count": asyncpg_faster_count,
                "psycopg2_faster_count": psycopg2_faster_count,
                "total_tests": total_tests,
                "avg_percentage_diff": avg_diff,
                "overall_faster": "asyncpg" if asyncpg_faster_count > psycopg2_faster_count else "psycopg2",
            }
        else:
            # For concurrent benchmarks, analyze by concurrency level
            asyncpg_faster_count = 0
            psycopg2_faster_count = 0
            total_tests = 0

            # Track performance by concurrency level
            concurrency_analysis = {}

            for count_results in analysis[benchmark_type].values():
                for concurrency, result in count_results.items():
                    if concurrency not in concurrency_analysis:
                        concurrency_analysis[concurrency] = {
                            "asyncpg_faster_count": 0,
                            "psycopg2_faster_count": 0,
                            "total_tests": 0,
                            "avg_percentage_diff": 0,
                        }

                    if result["faster"] == "asyncpg":
                        asyncpg_faster_count += 1
                        concurrency_analysis[concurrency]["asyncpg_faster_count"] += 1
                    else:
                        psycopg2_faster_count += 1
                        concurrency_analysis[concurrency]["psycopg2_faster_count"] += 1

                    concurrency_analysis[concurrency]["total_tests"] += 1
                    concurrency_analysis[concurrency]["avg_percentage_diff"] += abs(result["percentage_diff"])
                    total_tests += 1

            # Calculate averages for each concurrency level
            for concurrency, analysis_data in concurrency_analysis.items():
                if analysis_data["total_tests"] > 0:
                    analysis_data["avg_percentage_diff"] /= analysis_data["total_tests"]
                    analysis_data["overall_faster"] = (
                        "asyncpg"
                        if analysis_data["asyncpg_faster_count"] > analysis_data["psycopg2_faster_count"]
                        else "psycopg2"
                    )

            # Calculate overall average percentage difference
            avg_diff = (
                sum(
                    abs(result["percentage_diff"])
                    for count_results in analysis[benchmark_type].values()
                    for result in count_results.values()
                )
                / total_tests
                if total_tests > 0
                else 0
            )

            report[benchmark_type]["summary"] = {
                "asyncpg_faster_count": asyncpg_faster_count,
                "psycopg2_faster_count": psycopg2_faster_count,
                "total_tests": total_tests,
                "avg_percentage_diff": avg_diff,
                "overall_faster": "asyncpg" if asyncpg_faster_count > psycopg2_faster_count else "psycopg2",
                "concurrency_analysis": concurrency_analysis,
            }

    return report


async def main():
    """Main function to run all benchmarks."""
    print("Starting benchmark tests...")

    # Run standard benchmarks
    base_url = "http://localhost:8000"
    standard_counts = [10, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    standard_iterations = 3
    mixed_counts = [10, 50, 100, 500, 1000, 2000, 5000, 10000]
    mixed_iterations = 3

    print(
        f"Running standard benchmark tests with counts {standard_counts} and {standard_iterations} iterations each..."
    )
    print(f"Running mixed benchmark tests with counts {mixed_counts} and {mixed_iterations} iterations each...")

    # Test verisi oluşturmayı atlayalım
    # print("Creating test data...")
    # for i in range(20):
    #     requests.post(
    #         f"{base_url}/async/products",
    #         params={
    #             "name": f"Product {i}",
    #             "price": 10.99 + i,
    #             "sku": f"SKU{i}",
    #             "description": f"Test product {i}"
    #         },
    #     )

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

    # Run advanced benchmarks
    try:
        advanced_results = await run_advanced_benchmarks()
        advanced_analysis = analyze_advanced_results(advanced_results)
        advanced_report = generate_advanced_report(advanced_analysis)
    except Exception as e:
        print(f"Error with advanced benchmarks: {str(e)}")
        advanced_report = {"error": str(e)}

    # Combine all reports
    combined_report = {"standard": standard_report, "mixed": mixed_report, "timestamp": datetime.now().isoformat()}

    # Add advanced report if available
    if "error" not in advanced_report:
        combined_report["advanced"] = advanced_report

    # Save to file
    with open("benchmark_report.json", "w") as f:
        json.dump(combined_report, f, indent=2)

    print("\nBenchmark tests completed. Results saved to benchmark_report.json")

    # Print overall summary
    print("\n=== OVERALL SUMMARY ===")
    print("\nStandard Benchmark (SELECT operations):")
    print(f"  Overall faster: {standard_report['summary']['overall_faster']}")
    print(f"  Average difference: {standard_report['summary']['avg_percentage_diff']:.2f}%")

    print("\nMixed Benchmark (INSERT, UPDATE, DELETE, GET operations):")
    print(f"  Overall faster: {mixed_report['summary']['overall_faster']}")
    print(f"  Average difference: {mixed_report['summary']['avg_percentage_diff']:.2f}%")

    # Print advanced benchmark summary if available
    if "error" not in advanced_report:
        print("\nParallel Query Benchmark:")
        print(f"  Overall faster: {advanced_report['parallel']['summary']['overall_faster']}")
        print(f"  Average difference: {advanced_report['parallel']['summary']['avg_percentage_diff']:.2f}%")

        print("\nComplex Query Benchmark:")
        print(f"  Overall faster: {advanced_report['complex']['summary']['overall_faster']}")
        print(f"  Average difference: {advanced_report['complex']['summary']['avg_percentage_diff']:.2f}%")

        print("\nConcurrent Client Benchmark:")
        print(f"  Overall faster: {advanced_report['concurrent']['summary']['overall_faster']}")
        print(f"  Average difference: {advanced_report['concurrent']['summary']['avg_percentage_diff']:.2f}%")

        # Print concurrency analysis
        print("\nPerformance by Concurrency Level:")
        for concurrency, analysis in advanced_report["concurrent"]["summary"]["concurrency_analysis"].items():
            print(f"  Concurrency {concurrency}:")
            print(f"    Overall faster: {analysis['overall_faster']}")
            print(f"    Average difference: {analysis['avg_percentage_diff']:.2f}%")
    else:
        print("\nAdvanced benchmarks were not completed due to errors.")


async def test_advanced_benchmarks_only():
    """Function to test only advanced benchmarks."""
    print("Testing only advanced benchmarks...")

    try:
        # Run advanced benchmarks
        advanced_results = await run_advanced_benchmarks()

        # Print results
        print("\nAdvanced benchmark results:")

        # Complex benchmarks
        if "complex" in advanced_results and advanced_results["complex"]["async"]:
            print("\nComplex Query Benchmark:")
            for count, result in advanced_results["complex"]["async"].items():
                if isinstance(count, int) and "error" not in result:
                    async_ops = result.get("operations_per_second", 0)
                    sync_ops = advanced_results["complex"]["sync"][count].get("operations_per_second", 0)

                    if sync_ops > 0:
                        percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                        print(f"  Count {count}: asyncpg: {async_ops:.2f} ops/sec, psycopg2: {sync_ops:.2f} ops/sec")
                        print(
                            f"  Difference: {percentage_diff:.2f}% ({'asyncpg faster' if percentage_diff > 0 else 'psycopg2 faster'})"
                        )

        # Concurrent benchmarks
        if "concurrent" in advanced_results and advanced_results["concurrent"]["async"]:
            print("\nConcurrent Client Benchmark:")
            for count in advanced_results["concurrent"]["async"]:
                if isinstance(count, int):
                    for concurrency, result in advanced_results["concurrent"]["async"][count].items():
                        if "error" not in result:
                            async_ops = result.get("operations_per_second", 0)
                            sync_ops = advanced_results["concurrent"]["sync"][count][concurrency].get(
                                "operations_per_second", 0
                            )

                            if sync_ops > 0:
                                percentage_diff = ((async_ops - sync_ops) / sync_ops) * 100
                                print(
                                    f"  Count {count}, Concurrency {concurrency}: asyncpg: {async_ops:.2f} ops/sec, psycopg2: {sync_ops:.2f} ops/sec"
                                )
                                print(
                                    f"  Difference: {percentage_diff:.2f}% ({'asyncpg faster' if percentage_diff > 0 else 'psycopg2 faster'})"
                                )

    except Exception as e:
        print(f"Error running advanced benchmarks: {str(e)}")


if __name__ == "__main__":
    # Sadece gelişmiş benchmarkları test etmek için:
    asyncio.run(test_advanced_benchmarks_only())

    # Tüm benchmarkları çalıştırmak için:
    # asyncio.run(main())
