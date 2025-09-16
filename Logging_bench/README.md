# HwSwProject - Logging Performance & Analysis

This directory contains tools and resources for benchmarking and optimizing logging performance in Python for the HwSwCoDesign final project.

## Directory Structure
```
HwSwProject/ 
    └── logging_bench/ 
    ├── custom_logging_benchmark.py # Enhanced benchmark script for logging performance testing 
    ├── my_logging.py # Optimized logging implementation for performance
    ├── compare_logging.py # script to comapre the output log of the original benchmark and the optimized verison
    └── README.md # This file
```

## Files Description

### custom_logging_benchmark.py
Enhanced version of the logging benchmark that:
- Supports configurable message counts and formats
- Maintains compatibility with original test cases
- Automatically adjusts iteration counts
- Provides detailed benchmark metrics and statistics
- Handles various logging configurations (handlers, formatters, queues)

### my_logging.py
Optimized implementation of Python's logging module that:
- Maintains complete compatibility with standard logging output
- Implements performance optimizations for common logging patterns
- Provides adaptive computation of expensive fields
- Includes smart caching of process/thread information
- Optimizes message formatting and handler chains

### compare_logging.py
Comapre the output log of the original benchmarke and the optimized verison :
- Run both verisons with the same time stamp and same proccess. 
- Present both outputs in stdout.
- Compare outputs. 

## Usage

### Running Benchmarks

```bash
# Run standard benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode std -n 30000 --enabled-checks --handler null -r 5

# Run optimized benchmark
perf record -F 99 -g -- python3 logging_bench/custom_logging_benchmark.py --mode my -n 30000 --enabled-checks --handler null -r 5
```

## Dependencies
   - Python 3.x
   - Python standard logging library
   -  `pyperf` - for benchmarking

## Optimization Strategy
   - Recognize bottlenecks and repetitive operations
   - Recognize unnecessary actions
   - Keeping identical output 

## Key Changes
    - Adaptive fields
    - PID caching 
    - Fast-path for repetitive get_message operation
    - Handler chain caching 

## Expected improvements :
- **5-20% faster than basic logging verison**
