#!/usr/bin/env bash

# ================================
# Script for benchmarking json_dumps
# ================================

# Note: in order to run the script you must change the mode and get an execute permission:
# so run : chmod +x script_json_dumps.sh

set -e  # exit on first error

REPO_URL="https://github.com/barar953/HwSw.git"
BENCH_DIR="json_dumps_bench"

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

# Update package lists
sudo apt-get update

# Install Python and pip if not already installed
sudo apt-get install -y python3 python3-pip python3-venv git

# Install perf for profiling
sudo apt-get install -y linux-tools-common linux-tools-generic linux-tools-$(uname -r)

# Install FlameGraph
if [ ! -d "FlameGraph" ]; then
    git clone https://github.com/brendangregg/FlameGraph.git
fi

# Create virtual environment for the benchmark
if [ ! -d "venv_json_dumps" ]; then
    python3 -m venv venv_json_dumps
fi

source venv_json_dumps/bin/activate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install pyperformance orjson ujson

echo "Step 1 completed: Environment is ready."
echo

echo "=== Step 2: Benchmark execution ==="

cd "$BENCH_DIR/json_dumps_bench" || { echo "Cannot cd into benchmark directory"; exit 1; }

python3 custom_json_benchmark.py --cases NESTED --impl baseline -o baseline.json
echo "  -- Ran baseline"
python3 custom_json_benchmark.py --cases NESTED --impl optimized -o optimized.json
echo "  -- Ran optimized"
python3 custom_json_benchmark.py --cases NESTED --impl fast -o fast.json
echo "  -- Ran fast"

echo "Step 2 completed: Benchmarks executed (baseline, optimized, fast)."
echo

echo "=== Step 3: FlameGraph and perf data generation ==="

perf record -F 99 -g -- python3 custom_json_benchmark.py --cases NESTED --impl baseline
perf script > out_baseline.perf
../../FlameGraph/stackcollapse-perf.pl out_baseline.perf > out_baseline.folded
../../FlameGraph/flamegraph.pl out_baseline.folded > flamegraph_baseline.svg
echo "  -- FlameGraph baseline done"

perf record -F 99 -g -- python3 custom_json_benchmark.py --cases NESTED --impl optimized
perf script > out_optimized.perf
../../FlameGraph/stackcollapse-perf.pl out_optimized.perf > out_optimized.folded
../../FlameGraph/flamegraph.pl out_optimized.folded > flamegraph_optimized.svg
echo "  -- FlameGraph optimized done"

perf record -F 99 -g -- python3 custom_json_benchmark.py --cases NESTED --impl fast
perf script > out_fast.perf
../../FlameGraph/stackcollapse-perf.pl out_fast.perf > out_fast.folded
../../FlameGraph/flamegraph.pl out_fast.folded > flamegraph_fast.svg
echo "  -- FlameGraph fast done"

echo "Step 3 completed: FlameGraphs generated (baseline, optimized, fast)."
echo

echo "=== Step 4: Post-optimization comparison ==="

python3 -m pyperf compare_to baseline.json fast.json > comparison_baseline_vs_fast.txt
echo "  -- comparison baseline vs fast done"
python3 -m pyperf compare_to baseline.json optimized.json > comparison_baseline_vs_optimized.txt
echo "  -- comparison baseline vs optimized done"

echo "Step 4 completed: Post-optimization comparison done."
echo

echo "=== All steps completed successfully! ==="

echo "=== Output Summary ==="
echo "FlameGraphs saved in:   $BENCH_DIR/$BENCH_DIR/"
echo "Comparison results in:  $BENCH_DIR/$BENCH_DIR/comparison_baseline_vs_fast.txt, comparison_baseline_vs_optimized.txt"
echo "Benchmark results in:   $BENCH_DIR/$BENCH_DIR/baseline.json, optimized.json, fast.json"
