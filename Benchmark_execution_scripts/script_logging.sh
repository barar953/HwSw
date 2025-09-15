#!/usr/bin/env bash

# ================================
# Script for benchmarking Logging (with compare_logging.py)
# ================================

# Note: in order to run the script you must change the mode and get an execute permission:
# so run : chmod +x script_logging.sh

set -e  # exit on first error

REPO_URL="https://github.com/barar953/HwSw.git"
BENCH_DIR="Logging_bench"

echo "=== Step 0: Clone repository if missing ==="

if [ ! -d "$BENCH_DIR" ]; then
    echo "Cloning repo from $REPO_URL ..."
    git clone "$REPO_URL" "$BENCH_DIR"
else
    echo "Directory $BENCH_DIR already exists, skipping clone."
fi

echo "Step 0 completed: Repository ready."
echo

echo "=== Step 1: Environment setup and dependency installation ==="

sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
sudo apt-get install -y linux-tools-common linux-tools-generic linux-tools-$(uname -r)

if [ ! -d "FlameGraph" ]; then
    git clone https://github.com/brendangregg/FlameGraph.git
fi

if [ ! -d "venv_logging" ]; then
    python3 -m venv venv_logging
fi

source venv_logging/bin/activate
pip install --upgrade pip
pip install pyperformance

echo "Step 1 completed: Environment is ready."
echo

echo "=== Step 2: Run compare_logging.py (STD vs MY) ==="

cd "$BENCH_DIR/Logging_bench" || { echo "Cannot cd into benchmark directory"; exit 1; }

# Run comparison script (same directory as custom_logging_benchmark.py)
python3 compare_logging.py \
    --bench custom_logging_benchmark.py \
    -n 300000 -r 5 --enabled-checks --handler null --formatter message \
    --std-json logging_std.json --my-json logging_my.json \
    --std-perf perf_std.data --my-perf perf_my.data | tee comparison_logging.txt

echo "Step 2 completed: compare_logging.py finished."
echo ">> Comparison results also saved to comparison_logging.txt"
echo

echo "=== Step 3: FlameGraph generation ==="

perf script -i perf_std.data > out_std.perf
../../FlameGraph/stackcollapse-perf.pl out_std.perf > out_std.folded
../../FlameGraph/flamegraph.pl out_std.folded > flamegraph_std.svg
echo "  -- FlameGraph std done"

perf script -i perf_my.data > out_my.perf
../../FlameGraph/stackcollapse-perf.pl out_my.perf > out_my.folded
../../FlameGraph/flamegraph.pl out_my.folded > flamegraph_my.svg
echo "  -- FlameGraph my done"

echo "Step 3 completed: FlameGraphs generated."
echo

echo "=== All steps completed successfully! ==="

echo "=== Output Summary ==="
echo "FlameGraphs saved in:   $BENCH_DIR/Logging_bench/"
echo "Perf data saved in:     $BENCH_DIR/Logging_bench/perf_std.data, perf_my.data"
echo "Benchmark results in:   $BENCH_DIR/Logging_bench/logging_std.json, logging_my.json"
echo ">> Comparison results saved in :  $BENCH_DIR/Logging_bench/"
echo