# HwSwProject - Performance Benchmarking Suite

A comprehensive benchmarking toolkit for analyzing and optimizing Python performance in JSON serialization and logging operations.

## Project Overview

This project provides specialized benchmarking tools and acceleration for two critical Python operations:
1. JSON Dumps
2. Logging System

## Project Structure

```
HwSwProject/
├── json_dumps_bench/                    # JSON serialization benchmarking suite
│   ├── custom_json_benchmark.py         # Enhanced benchmark with custom JSON file support
│   ├── my_json_dumps.py                 # Optimized JSON dumps implementation
│   └── README.md                        # Detailed JSON benchmarking documentation
├── Logging_bench/                       # Python logging performance analysis
│   ├── custom_logging_benchmark.py      # Configurable logging performance tests
│   ├── my_logging.py                    # Optimized logging implementation
│   ├── compare_logging.py               # Comparative analysis between standard and optimized logging
│   └── README.md                        # Detailed logging benchmarking documentation
├── Benchmark_execution_scripts/         # Automated benchmark execution tools
│   ├── script_json_dumps.sh             # Complete JSON benchmarking automation script
│   ├── script_logging.sh                # Complete logging benchmarking automation script
│   └── README.md                        # Scripts documentation and usage guide
├── Additional files/                    # Supporting materials and analysis results
│   ├── Json_dumps/                      # JSON benchmarking outputs and flame graphs
│   │   ├── check_outputs.py             # Output validation utility
│   │   ├── flamegraph_self_opt.svg      # Flame graph visualization for optimized JSON
│   │   ├── json_flamegraph_baseline.svg # Baseline JSON performance flame graph
│   │   ├── json_flamegraph_optimize.svg # Optimized JSON performance flame graph
│   │   └── out_self_opt.txt             # Performance output logs
│   └── Logging/                         # Logging benchmarking outputs and analysis
│       ├── compare_logging.py           # Logging comparison utilities
│       ├── flamegraph_base_log.svg      # Baseline logging flame graph
│       ├── flamegraph_opt2_log.svg      # Optimized logging flame graph
│       ├── sample_log_app.py            # Sample logging application
│       └── *.txt                        # Various performance output logs
├── Project _HWSW_Tomer_Ben_Aroush__Bar_Arama.pdf  # Project documentation
├── final project HwSw co-design.pptx   # Project presentation
├── prompt.txt                           # Project requirements and specifications
└── qemu ssh tutorial.txt               # QEMU SSH setup instructions
```

### Directory Descriptions

- **json_dumps_bench/**: Core JSON serialization benchmarking module containing optimized implementations and comprehensive testing framework for JSON performance analysis.

- **Logging_bench/**: Python logging system performance analysis suite with custom implementations and comparative tools for logging optimization.

- **Benchmark_execution_scripts/**: Automated execution scripts that handle complete benchmarking workflows, including environment setup, dependency installation, benchmark execution, and flame graph generation.

- **Additional files/**: Supporting materials including performance analysis outputs, flame graph visualizations, validation utilities, and sample applications for both JSON and logging components.

## Components

### 1. JSON Dumps Benchmarking

The JSON benchmarking component provides comprehensive tools for testing and optimizing JSON serialization performance across multiple implementations and test scenarios:

- **custom_json_benchmark.py**: Enhanced benchmark framework supporting custom JSON files with multiple test cases
- **my_json_dumps.py**: High-performance JSON dumps implementation featuring optimization hooks and smart caching

**Key Features:**
- Custom JSON file support with flexible input handling
- Multiple test cases: EMPTY (minimal data), SIMPLE (basic structures), NESTED (complex hierarchies), HUGE (large datasets)
- Integration with high-performance JSON libraries (orjson, ujson)
- Smart caching mechanisms for frequently accessed data
- Fast-path recognition for common serialization patterns
- Compact separators optimization for reduced output size
- **Performance Achievement: x8.85 speed improvement over baseline**

**Implementation Details:**
- Adaptive algorithm selection based on data characteristics
- Memory-efficient processing for large datasets
- Comprehensive error handling and validation
- Detailed performance metrics and timing analysis

### 2. Logging Benchmarking

The logging benchmarking component focuses on optimizing Python logging operations through intelligent caching and adaptive processing:

- **custom_logging_benchmark.py**: Configurable logging performance test suite with multiple scenarios
- **my_logging.py**: Optimized logging implementation with performance enhancements
- **compare_logging.py**: Comparative analysis tool for baseline vs. optimized implementations

**Key Features:**
- Configurable message counts and diverse formatting options
- Multiple handler support (console, file, null for testing)
- Smart caching mechanisms for repeated operations
- Adaptive field computation based on usage patterns
- PID caching for improved process identification performance
- Fast-path message operations for common logging scenarios
- Handler chain optimization for reduced overhead
- **Performance Achievement: 10-12% improvement in logging throughput**

**Implementation Details:**
- Lazy evaluation of expensive operations
- Optimized string formatting and concatenation
- Reduced function call overhead in critical paths
- Memory pool management for frequent allocations
- Thread-safe implementations with minimal locking

### 3. Benchmark Execution Scripts

Automated execution framework providing end-to-end benchmarking workflows:

- **script_json_dumps.sh**: Complete automation for JSON benchmarking including environment setup, dependency management, benchmark execution, and flame graph generation
- **script_logging.sh**: Comprehensive logging benchmark automation with comparative analysis and visualization

**Key Features:**
- Automated environment setup and dependency installation
- Virtual environment management for isolated testing
- Performance profiling with perf and flame graph generation
- Comparative analysis between different implementations
- Automated result collection and organization
- Error handling and recovery mechanisms

**Workflow Capabilities:**
- Repository cloning and setup
- Python environment configuration
- Required package installation (pyperf, orjson, ujson)
- FlameGraph tool installation and setup
- Benchmark execution across multiple scenarios
- Performance data collection and analysis
- Visual flame graph generation for performance profiling
- Automated comparison report generation

### 4. Additional Analysis Tools

Supporting utilities and analysis results for comprehensive performance evaluation:

**JSON Analysis Tools:**
- Output validation utilities for correctness verification
- Multiple flame graph visualizations for different optimization levels
- Performance comparison reports and statistical analysis

**Logging Analysis Tools:**
- Comparative logging analysis between standard and optimized implementations
- Sample applications demonstrating real-world usage scenarios
- Performance output logs with detailed timing information
- Visual performance profiling through flame graphs

## Quick Start

### Option 1: Automated Execution (Recommended)

Use the provided automation scripts for complete benchmarking workflows:

```bash
# JSON Dumps Benchmarking (Complete automation)
cd Benchmark_execution_scripts
chmod +x script_json_dumps.sh
./script_json_dumps.sh

# Logging Benchmarking (Complete automation)
chmod +x script_logging.sh
./script_logging.sh
```

These scripts handle:
- Environment setup and dependency installation
- Virtual environment creation
- Benchmark execution across all test cases
- Performance profiling and flame graph generation
- Comparative analysis and result collection

### Option 2: Manual Execution

#### JSON Dumps Benchmarking

```bash
# Run basic benchmark
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl baseline

# Benchmark specific test cases
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl optimized
perf record -F 99 -g -- python3 json_dumps_bench/custom_json_benchmark.py --cases NESTED --impl fast
```

#### Logging Benchmarking

```bash
# Run standard benchmark
perf record -F 99 -g -- python3 Logging_bench/custom_logging_benchmark.py --mode std -n 300000 --enabled-checks --handler null -r 5

# Run optimized benchmark
perf record -F 99 -g -- python3 Logging_bench/custom_logging_benchmark.py --mode my -n 300000 --enabled-checks --handler null -r 5

# Run comparative analysis
python3 Logging_bench/compare_logging.py --bench custom_logging_benchmark.py -n 300000 -r 5 --enabled-checks --handler null
```

## Dependencies

### Core Requirements:
- Python 3.x
- pyperf (benchmarking framework)
- perf (Linux performance profiling tool)
- git (version control)

### JSON Dumps Additional Requirements:
- orjson (high-performance JSON library)
- ujson (ultra-fast JSON library)

### Logging Additional Requirements:
- Standard Python logging library (included in Python)

### Profiling and Visualization:
- FlameGraph (performance visualization)
- linux-tools (perf profiling utilities)

### Installation Options:

#### Option 1: Automated Installation
The benchmark execution scripts automatically handle all dependencies:
```bash
# All dependencies installed automatically by the scripts
./Benchmark_execution_scripts/script_json_dumps.sh
./Benchmark_execution_scripts/script_logging.sh
```

#### Option 2: Manual Installation
```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
sudo apt-get install -y linux-tools-common linux-tools-generic linux-tools-$(uname -r)

# Python dependencies
pip install pyperf orjson ujson

# FlameGraph (for visualization)
git clone https://github.com/brendangregg/FlameGraph.git
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

### Component Documentation:
- **JSON Dumps**: [json_dumps_bench/README.md](json_dumps_bench/README.md)
- **Logging**: [Logging_bench/README.md](Logging_bench/README.md)
- **Benchmark Scripts**: [Benchmark_execution_scripts/README.md](Benchmark_execution_scripts/README.md)

### Additional Resources:
- **Project Report**: [Project _HWSW_Tomer_Ben_Aroush__Bar_Arama.pdf](Project%20_HWSW_Tomer_Ben_Aroush__Bar_Arama.pdf)
- **Project Presentation**: [final project HwSw co-design.pptx](final%20project%20HwSw%20co-design.pptx)
- **Analysis Results**: Available in the `Additional files/` directory with flame graphs and performance outputs
- **Setup Guide**: [qemu ssh tutorial.txt](qemu%20ssh%20tutorial.txt) for QEMU SSH configuration
