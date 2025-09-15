# HwSwProject - Performance Benchmarking Suite

A comprehensive benchmarking toolkit for analyzing and optimizing Python performance in JSON serialization and logging operations.

## Project Overview

This project provides specialized benchmarking tools and acceleration for two critical Python operations:
1. JSON Dumps
2. Logging System

## Project Structure

```
HwSwProject/
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
- Smart caching mechanisms

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
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl baseline

# Benchmark specific test cases
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl optimized
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl fast
```

### Logging Benchmarking

```bash
# Run standard benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode std -n 300000 --enabled-c

# Run optimized benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode my -n 300000 --enabled-c
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
