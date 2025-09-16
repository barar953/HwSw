# HwSwProject - Performance Benchmarking Suite

A comprehensive benchmarking toolkit for analyzing and optimizing Python performance in JSON serialization and logging operations.

## Project Overview

This project provides specialized benchmarking tools and acceleration for two critical Python operations:
1. JSON Dumps
2. Logging System

## Project Structure

```
HwSwProject/
├── Benchmark_execution_scripts/    # Scripts for executing various benchmark scenarios
├── json_dumps_bench/              # JSON serialization benchmarking tools
│   ├── custom_json_benchmark.py   # Enhanced benchmark for JSON operations
│   ├── my_json_dumps.py          # Optimized JSON dumps implementation
│   └── README.md                 # JSON benchmarking documentation
├── logging_bench/                # Logging performance optimization tools
│   ├── custom_logging_benchmark.py # Configurable logging benchmarks
│   ├── my_logging.py             # Optimized logging implementation
│   └── README.md                 # Logging benchmarking documentation
└── README.md                     # Main project documentation
```

## Components

### 1. JSON Dumps Benchmarking

The JSON benchmarking component provides tools for testing and optimizing JSON serialization performance:

- **custom_json_benchmark.py**: Enhanced benchmark supporting custom JSON files with comprehensive test scenarios
- **my_json_dumps.py**: Optimized JSON dumps implementation with performance hooks and memory efficiency improvements

Implementation Details:
- Fast-path recognition for common data structures
- Caching collections to reduce allocation overhead
- Compact separators for reduced output size
- Integration with high-performance libraries (orjson, ujson)
- Support for various test cases: EMPTY, SIMPLE, NESTED, HUGE

Key Features:
- Custom JSON file support
- Multiple test cases (EMPTY, SIMPLE, NESTED, HUGE)
- Integration with faster JSON libraries
- Smart caching mechanisms

### 2. Logging Benchmarking

The logging benchmarking component focuses on optimizing Python logging operations:

- **custom_logging_benchmark.py**: Configurable logging performance tests with multiple execution modes
- **my_logging.py**: Optimized logging implementation with enhanced handler chain processing

Implementation Details:
- Adaptive field computation to minimize overhead
- PID caching for process identification
- Fast-path message operations for common scenarios
- Handler chain optimization for reduced latency
- Configurable test parameters for various workloads

Key Features:
- Configurable message counts and formats
- Multiple handler support
- Smart caching mechanisms
- Adaptive field computation

### 3. Benchmark Execution Scripts

The Benchmark_execution_scripts directory contains tools for automated benchmark execution and analysis:
- Automated benchmark runners for both JSON and logging components
- Result collection and analysis utilities
- Performance comparison tools
- Batch processing capabilities

## Quick Start

### JSON Dumps Benchmarking

```bash
# Run basic benchmark
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl baseline

# Benchmark specific test cases
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl optimized
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl fast
```

### Logging Benchmarking

```bash
# Run standard benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode std -n 300000 --enabled-checks --handler null -r 5

# Run optimized benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode my -n 300000 --enabled-checks --handler null -r 5
```

## Dependencies

Core Requirements:
- Python 3.x
- pyperf (benchmarking)

JSON Dumps Additional Requirements:
- orjson
- ujson

Logging Additional Requirements:
- Logging pyhton library
  
Install dependencies:
```bash
pip install pyperf orjson ujson
```

## Performance Improvements

### JSON Dumps Component
- Optimizations through:
    - Fast-path recognition 
    - Caching collections
    - Compact separators 
- **Total: x8.85 performance improvement**
  
### Logging Component
- Optimizations through:
  - Adaptive fields
  - PID caching
  - Fast-path message operations
  - Handler chain optimization
- **Total: 10-12% performance improvement** 

## Detailed Documentation

For more detailed information about each component, please refer to:
- JSON Dumps: [json_dumps_bench/README.md](json_dumps_bench/README.md)
- Logging: [logging_bench/README.md](logging_bench/README.md)
