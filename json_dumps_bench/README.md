# HwSwProject - JSON Dumps Performance Benchmarking

This project contains tools for benchmarking and optimizing JSON serialization performance in Python.

## Project Structure

```
HwSwProject/
└── json_dumps_bench/
    ├── custom_json_benchmark.py  # Enhanced benchmark with custom data support
    ├── my_json_dumps.py         # Copy of original json.dumps with optimization hooks
    └── README.md               # This file
```

## Files Description

### custom_json_benchmark.py
Enhanced version of the pyperformance json_dumps benchmark that:
- Supports loading custom JSON files for benchmarking
- Maintains compatibility with original test cases (EMPTY, SIMPLE, NESTED, HUGE)
- Automatically adjusts iteration counts based on file size
- Provides detailed metadata about the benchmark

### my_json_dumps.py
Copy of the original Python json.dumps implementation with:
- Complete original functionality preserved
- Optimization hooks added (dumps_optimized, dumps_fast)
- Support for faster JSON libraries (orjson, ujson)

## Usage

### Running Benchmarks

```bash
# Run basic benchmark
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl baseline

# Benchmark specific test cases
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl optimized
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl fast
```
     
## Dependencies

- `pyperf` - for benchmarking
- `orjson` - for faster JSON processing
- `ujson`  - alternative fast JSON library

Install with:
```bash
pip install pyperf orjson ujson
```

## Optimization Strategy
- Python interpreter as a main consumer
- Collections serialization is a main bottleneck  
- Repetitive actions – encode the same input again and again
- Keeping identical output 

### 2-way solution:
**1. Optimized_json:**
- Fast-path recognition
- Caching collections
- Compact separators
  
**2. Fast_json:**
- Orjson Rust library
- Compiled library
- Better Memory Management

## Expected improvements:(based on NESTED case)
- **5.56x Faster** Fast_json then baseline
- **8.85x Faster** Optimized_json then baseline
