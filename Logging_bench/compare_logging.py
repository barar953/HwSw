#!/usr/bin/env python3
import argparse, json, subprocess, sys, shlex, os, shutil

def run(cmd: str, quiet: bool = False):
    """Run a shell command with optional quiet mode (suppress stdout/stderr)."""
    if not quiet:
        print(">>", cmd)
    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
        check=True
    )

def run_one(mode: str, args, out_json: str, perf_data: str):
    """Run perf record ... python3 custom_logging_benchmark.py --mode <mode> ..."""
    bench_cmd = (
        f"python3 {shlex.quote(args.bench)} --mode {mode} "
        f"-n {args.num_messages} -r {args.repeat} "
        f"{'--enabled-checks' if args.enabled_checks else ''} "
        f"--handler {args.handler} "
        f"--formatter {args.formatter} "
        f"{'--use-queue' if args.use_queue else ''} "
        f"{'--propagate' if args.propagate else ''} "
        f"{f'--max-seconds {args.max_seconds}' if args.max_seconds > 0 else ''} "
        f"--out {shlex.quote(out_json)}"
    ).strip()

    perf_cmd = f"perf record -F {args.perf_freq} -g -o {shlex.quote(perf_data)} -- {bench_cmd}"
    run(perf_cmd, quiet=True)   # quiet mode suppresses perf output

def read_mean_std(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["stats"]["mean_sec"], data["stats"]["stdev_sec"]

def main():
    p = argparse.ArgumentParser(description="Run perf+benchmark for logging (STD vs MY) and compare.")
    p.add_argument("--bench", default="custom_logging_benchmark.py", help="Path to custom_logging_benchmark.py")
    p.add_argument("-n", "--num-messages", type=int, default=30_000)
    p.add_argument("-r", "--repeat", type=int, default=5)
    p.add_argument("--enabled-checks", action="store_true", default=True)
    p.add_argument("--handler", choices=["null", "stream", "file"], default="null")
    p.add_argument("--formatter", choices=["message", "simple", "detailed"], default="message")
    p.add_argument("--use-queue", action="store_true")
    p.add_argument("--propagate", action="store_true")
    p.add_argument("--max-seconds", type=float, default=0.0)
    p.add_argument("--perf-freq", type=int, default=99, help="perf sampling frequency (Hz)")
    p.add_argument("--std-json", default="logging_std.json")
    p.add_argument("--my-json",  default="logging_my.json")
    p.add_argument("--std-perf", default="perf_std.data")
    p.add_argument("--my-perf",  default="perf_my.data")
    args = p.parse_args()

    # 1) STD
    run_one("std", args, args.std_json, args.std_perf)

    # 2) MY
    run_one("my", args, args.my_json, args.my_perf)

    # 3) Compare
    ms, ss = read_mean_std(args.std_json)
    mm, sm = read_mean_std(args.my_json)
    speedup = (ms / mm - 1.0) * 100.0

    result_txt = (
        f"\nSTD logging: Mean +- std dev: {ms:.3f} s +- {ss:.3f} s\n"
        f"MY  logging: Mean +- std dev: {mm:.3f} s +- {sm:.3f} s\n"
        f"Improvement: {speedup:.2f}% faster\n"
    )

    print(result_txt)

    # Save also to file
    with open("comparison_logging.txt", "w", encoding="utf-8") as f:
        f.write(result_txt)
    print(">> Comparison results saved to comparison_logging.txt")

if __name__ == "__main__":
    if shutil.which("perf") is None:
        print("ERROR: 'perf' not found in PATH. Please install linux-tools/perf.")
        sys.exit(1)
    main()
