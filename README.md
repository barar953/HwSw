# HwSwProject - Performance Benchmarking Suite

A comprehensive benchmarking toolkit for analyzing and optimizing Python performance in JSON serialization and logging operations.

## Project Overview

This project provides specialized benchmarking tools for two critical Python operations:
1. JSON Dumps Performance Testing
2. Logging System Performance Analysis

## Project Structure

```
HwSwProject/
├── HwSwFinalProject (PDF format file in hebrew, includes all the project details and results, includes also hardware accelerator design.)
├── json_dumps_bench/
│   ├── custom_json_benchmark.py
│   ├── my_json_dumps.py
│   └── README.md
└── logging_bench/
    ├── custom_logging_benchmark.py
    ├── my_logging.py
    └── README.md
```

## Components

### 1. JSON Dumps Benchmarking

The JSON benchmarking component provides tools for testing and optimizing JSON serialization performance:

- **custom_json_benchmark.py**: Enhanced benchmark supporting custom JSON files
- **my_json_dumps.py**: Optimized JSON dumps implementation with performance hooks

Key Features:
- Custom JSON file support
- Multiple test cases (EMPTY, SIMPLE, NESTED, HUGE)
- Integration with faster JSON libraries
- Detailed performance metrics

### 2. Logging Benchmarking

The logging benchmarking component focuses on optimizing Python logging operations:

- **custom_logging_benchmark.py**: Configurable logging performance tests
- **my_logging.py**: Optimized logging implementation

Key Features:
- Configurable message counts and formats
- Multiple handler support
- Smart caching mechanisms
- Adaptive field computation

## Quick Start

### JSON Dumps Benchmarking

```bash
# Run basic benchmark
python3 json_dumps_bench/custom_json_benchmark.py

# Benchmark specific test cases
python3 json_dumps_bench/custom_json_benchmark.py --cases SIMPLE,NESTED
```

### Logging Benchmarking

```bash
# Run standard benchmark
python3 logging_bench/custom_logging_benchmark.py --mode std

# Run optimized benchmark
python3 logging_bench/custom_logging_benchmark.py --mode my
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
- 15-20% improvement from production Python build
- 10-15% improvement from faster JSON libraries
- 5-10% improvement from memory optimizations
- **Total: 30-50% performance improvement**

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
