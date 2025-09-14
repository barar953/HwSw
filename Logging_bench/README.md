# HwSwProject - Logging Performance & Analysis

This directory contains tools and resources for benchmarking and optimizing logging performance in Python for the HwSwCoDesign final project.

## Directory Structure

```
└── logging/
HwSwProject/
└── logging_bench/
    ├── custom_logging_benchmark.py  # Enhanced benchmark with custom data support
    ├── my_logging_dumps.py         # Copy of original json.dumps with optimization hooks
    └── README.md               # This file
```

## Files Description

### main.py / logger.py / logging.py / logcall.py / log.py / server.py / factor.py / nox.py / setup.py
These Python scripts cover a wide variety of logging scenarios:
- Basic and advanced logging setup (file, console, email, Sentry, etc.)
- Custom logging decorators
- Integration with frameworks (Django, Flask)
- Performance profiling and benchmarking automation
- Example scripts (factorization, Labber integration)

### log_1.txt
Sample output from model training, including configuration parameters, logging directory, and performance profiling details.

### keywords.txt
Defines syntax highlighting keywords for log levels, methods/functions, constants, and logging library instances.

### slack.md
Step-by-step instructions for integrating logging with Slack, including Sentry, Netlify, and Heroku notifications.

### csv.txt
Example CSV data, useful for logging output or benchmarking analytics.

### INSTALL
Simple instructions for compiling logging-related code:
```
make
```

### Documentation Files (toc.md, index.md, _index.md, index.qmd)
- Table of contents, introductions, and advanced integration guides for logging components and best practices.

## Usage

### Running Logging Scripts

1. **Basic logging example:**
   ```bash
   python3 main.py
   ```

2. **Advanced logging and configuration:**
   ```bash
   python3 logger.py
   ```

3. **Django-style logging config:**
   ```python
   from logging import config
   config.dictConfig(LOGGING)
   ```

### Integrating with Slack

See `slack.md` for step-by-step instructions to send logging alerts and notifications to Slack.

### Performance Profiling

For advanced profiling and optimization:
- Use Python's built-in `logging` module for custom formats and handlers.
- Profile logging overhead using `perf` or similar tools to identify bottlenecks.

## Optimization Strategy

Based on profiling and analysis, focus on:
1. **Efficient log formatting and I/O** (avoid unnecessary string processing; use file or stream handlers).
2. **Log level filtering** (reduce logging at production; use DEBUG for development).
3. **Asynchronous logging** for high-throughput scenarios.

### Recommended Optimizations

- Use Python's `logging` built-in for flexibility and performance.
- Configure log rotation and external monitoring (e.g., Sentry, Slack).
- Avoid excessive logging in performance-critical paths.

## Dependencies

- Python standard `logging` module
- Optional: Sentry SDK, Flask, Django, Labber (for specialized integrations)

Install typical dependencies:
```bash
pip install sentry-sdk flask django
```

## Performance Analysis

Use profiling tools and log output to identify:
- I/O bottlenecks
- String formatting overhead
- Integration and notification delays

Expected improvements:
- **10-20%** from optimized logging configuration
- **5-15%** from handler and formatter tuning
- **Up to 30%** with asynchronous or batch logging

---
