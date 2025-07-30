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
- Easy-to-modify structure for performance improvements

## Usage

### Running Benchmarks

1. **Basic benchmark with all test cases:**
   ```bash
   python3 custom_json_benchmark.py
   ```

2. **Benchmark specific test cases:**
   ```bash
   python3 custom_json_benchmark.py --cases SIMPLE,NESTED,HUGE
   ```

3. **Benchmark with custom JSON file:**
   - Edit `custom_json_benchmark.py` and change `/path/to/your/file.json` to your file path
   - Run: `python3 custom_json_benchmark.py --cases CUSTOM`

4. **Performance profiling with perf:**
   ```bash
   perf record -F 999 -g -- python3 custom_json_benchmark.py --cases CUSTOM
   perf report
   ```

### Comparing Performance

To compare original vs optimized versions:

1. **Run original benchmark:**
   ```bash
   python3 -m pyperformance run --bench json_dumps -o original_results.json
   ```

2. **Run custom benchmark:**
   ```bash
   python3 custom_json_benchmark.py -o custom_results.json
   ```

3. **Compare results:**
   ```bash
   python3 -m pyperformance compare original_results.json custom_results.json
   ```

## Optimization Strategy

Based on perf analysis, the main bottlenecks are:

1. **Memory management** (25% of CPU time)
   - Debug memory validation overhead
   - Unicode string validation
   - Memory allocation/deallocation

2. **JSON processing** (5% of CPU time)
   - String escaping
   - Dictionary/object encoding

3. **Python interpreter overhead** (10% of CPU time)
   - Main interpreter loop
   - Dictionary lookups

### Recommended Optimizations

1. **Use production Python build** (not python3-dbg)
2. **Integrate faster JSON libraries** (orjson, ujson)
3. **Optimize memory allocation patterns**
4. **Use compact separators by default**

## Dependencies

- `pyperf` - for benchmarking
- `orjson` (optional) - for faster JSON processing
- `ujson` (optional) - alternative fast JSON library

Install with:
```bash
pip install pyperf orjson ujson
```

## Performance Analysis

Use the perf report from your original benchmark to identify:
- Memory allocation bottlenecks
- String processing overhead
- Interpreter loop optimization opportunities

Expected improvements:
- **15-20%** from production Python build
- **10-15%** from faster JSON libraries
- **5-10%** from memory optimizations
- **Total: 30-50%** performance improvement
