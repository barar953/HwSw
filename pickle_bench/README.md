# HwSwProject - Pickle Performance Benchmarking

This directory contains tools for benchmarking and optimizing pickle serialization performance in Python, following the same methodology as the JSON dumps benchmarking project.

## Project Structure

```
pickle_bench/
├── custom_pickle_benchmark.py   # Enhanced benchmark based on pyperformance
├── my_pickle.py                 # Copy of original pickle.py implementation  
└── README.md                   # This file
```

## Files Description

### custom_pickle_benchmark.py
Enhanced version of the pyperformance pickle benchmarks that:
- Supports all original pyperformance pickle benchmark types
- Uses our custom `my_pickle.py` implementation
- Maintains compatibility with original test cases
- Supports both C-accelerated and pure Python modes
- Provides detailed metadata about the benchmark
- Easy switching between original and custom pickle implementations

### my_pickle.py
Complete copy of the original Python pickle.py implementation:
- Full original functionality preserved
- Ready for performance optimizations
- Supports all pickle protocols
- Easy-to-modify structure for improvements

## Available Benchmarks

Based on pyperformance pickle benchmarks:

1. **`pickle`** - General pickle benchmark testing:
   - User profile dictionary (DICT)
   - Number tuple (TUPLE) 
   - Dictionary group (DICT_GROUP)

2. **`pickle_dict`** - Dictionary-focused benchmark:
   - Nested dictionary structure (MICRO_DICT)
   - 100 keys with 10 sub-keys each

3. **`pickle_list`** - List pickling benchmark:
   - Nested list structures
   - Multiple list operations

4. **`unpickle`** - General unpickle benchmark
5. **`unpickle_list`** - List unpickle benchmark

## Usage

### Basic Benchmarking

1. **Run pickle_dict benchmark (default):**
   ```bash
   python3 custom_pickle_benchmark.py
   ```

2. **Run specific benchmark:**
   ```bash
   python3 custom_pickle_benchmark.py pickle
   python3 custom_pickle_benchmark.py pickle_list
   python3 custom_pickle_benchmark.py unpickle
   ```

3. **Use pure Python implementation (disable C extensions):**
   ```bash
   python3 custom_pickle_benchmark.py --pure-python pickle_dict
   ```

4. **Specify pickle protocol:**
   ```bash
   python3 custom_pickle_benchmark.py --protocol 4 pickle_dict
   ```

### Switching Between Implementations

To test original vs custom pickle:

1. **Edit `custom_pickle_benchmark.py`:**
   ```python
   # Use original pickle
   import pickle
   # import my_pickle as pickle
   
   # OR use custom pickle
   # import pickle  
   import my_pickle as pickle
   ```

2. **Run benchmark and compare results**

### Performance Analysis

1. **Basic performance measurement:**
   ```bash
   python3 custom_pickle_benchmark.py pickle_dict
   ```

2. **Compare C-accelerated vs Pure Python:**
   ```bash
   # C-accelerated (default)
   python3 custom_pickle_benchmark.py pickle_dict
   
   # Pure Python
   python3 custom_pickle_benchmark.py --pure-python pickle_dict
   ```

3. **Profile with perf:**
   ```bash
   perf record -F 999 -g -- python3 custom_pickle_benchmark.py pickle_dict
   perf report
   ```

## Understanding C Extensions vs Pure Python

### C Extensions (`_pickle` module):
- **What it does:** Provides C-implemented versions of:
  - `Pickler` class (serialization)
  - `Unpickler` class (deserialization) 
  - Core operations (`dumps`, `loads`, etc.)
- **Performance:** Significantly faster than pure Python
- **Location:** Built into Python as `_pickle` C extension module

### Pure Python Implementation:
- **What it does:** Python-only implementation in `pickle.py`
- **When used:** When C extensions disabled or unavailable
- **Performance:** Slower but easier to modify and optimize
- **Access:** `--pure-python` flag disables C extensions

### Benchmark Behavior:
- **Default:** Uses C extensions if available
- **`--pure-python`:** Forces pure Python implementation
- **Detection:** `is_accelerated_module()` checks which is being used

## Test Data

The benchmarks use realistic test objects from pyperformance:

- **DICT:** User profile with mixed data types (strings, integers, dates, lists)
- **TUPLE:** Large tuple with number list and integer
- **LIST:** Nested list structure `[[0,1,2...], [0,1,2...]]` repeated
- **MICRO_DICT:** 100 keys, each containing dict with 10 sub-keys
- **DICT_GROUP:** 3 variations of the user profile dict

## Optimization Strategy

Based on pickle module analysis:

### Current Performance Bottlenecks:
1. **Object serialization overhead**
2. **Protocol encoding/decoding**
3. **Memory allocation patterns**
4. **Type checking and validation**

### Recommended Optimizations:
1. **Protocol optimization** - Use most efficient protocol
2. **Memory management** - Reduce allocation overhead  
3. **Type-specific optimizations** - Fast paths for common types
4. **Buffering improvements** - Optimize I/O operations

Expected improvements:
- **Protocol tuning:** 5-15% improvement
- **Memory optimization:** 10-20% improvement  
- **Type-specific paths:** 15-25% improvement
- **Total potential:** 30-60% performance improvement

## Dependencies

```bash
pip install pyperf
```

## Comparison with JSON Dumps Project

This pickle benchmarking follows the same methodology as `json_dumps_bench/`:
- Custom implementation copy (`my_pickle.py` vs `my_json_dumps.py`)
- Enhanced benchmark (`custom_pickle_benchmark.py` vs `custom_json_benchmark.py`)
- Performance analysis and optimization hooks
- Easy switching between original and custom implementations

## Next Steps

1. **Baseline measurements:** Establish current performance
2. **Profiling:** Identify specific bottlenecks with perf
3. **Targeted optimizations:** Implement improvements in `my_pickle.py`
4. **Validation:** Ensure compatibility and correctness
5. **Performance comparison:** Measure improvement gains
