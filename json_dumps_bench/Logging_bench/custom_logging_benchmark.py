#!/usr/bin/env python3
import argparse
import io
import json
import os
import statistics as stats
import sys
import tempfile
import time
from typing import Dict, Any, List, Tuple

# ------------------------ Safe helpers ------------------------

def _install_module_as_logging(module_path: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "my_logging", os.path.join(os.path.dirname(__file__), module_path)
    )
    my_logging = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(my_logging)  # type: ignore
    sys.modules["logging"] = my_logging

def _build_logger(use_queue: bool, handler_type: str, formatter: str, propagate: bool):
    import logging

    logger = logging.getLogger("bench_logger")
    logger.handlers[:] = []  # clear previous
    logger.propagate = propagate
    logger.setLevel(logging.DEBUG)

    # formatter choice
    if formatter == "message":
        fmt = "%(message)s"
    elif formatter == "simple":
        fmt = "%(levelname)s:%(name)s:%(message)s"
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s [%(process)d/%(thread)d] %(message)s"

    formatter_obj = logging.Formatter(fmt)

    # handler choice (avoid real disk I/O by default)
    if handler_type == "null":
        class NullHandler(logging.Handler):
            def emit(self, record):  # no-op
                pass
        h = NullHandler()
    elif handler_type == "file":
        # Use a NamedTemporaryFile to avoid blocking issues with StringIO/fileno quirks
        tmp = tempfile.NamedTemporaryFile(prefix="logbench_", suffix=".log", delete=False, mode="w", encoding="utf-8")
        # We won't flush/close it during the hot loop
        h = logging.StreamHandler(tmp)
        logger._bench_tmpfile = tmp.name  # for cleanup
    else:
        h = logging.StreamHandler()

    h.setFormatter(formatter_obj)

    if use_queue:
        # Use queue handler only if explicitly requested
        try:
            from logging.handlers import QueueHandler, QueueListener
            import queue
            q = queue.Queue()
            qh = QueueHandler(q)
            listener = QueueListener(q, h, respect_handler_level=False)
            logger.addHandler(qh)
            listener.start()
            logger._bench_listener = listener  # type: ignore[attr-defined]
        except Exception:
            # fallback safely to direct handler
            logger.addHandler(h)
    else:
        logger.addHandler(h)

    return logger

def _teardown_logger(logger):
    import logging
    # stop listener if exists
    listener = getattr(logger, "_bench_listener", None)
    if listener:
        try:
            listener.stop()
        except Exception:
            pass
        try:
            delattr(logger, "_bench_listener")
        except Exception:
            pass
    # close temp file if opened
    tmpfile = getattr(logger, "_bench_tmpfile", None)
    if tmpfile:
        try:
            # best effort cleanup
            pass
        finally:
            try:
                os.unlink(tmpfile)
            except Exception:
                pass
        try:
            delattr(logger, "_bench_tmpfile")
        except Exception:
            pass
    # remove handlers
    logger.handlers[:] = []

def _generate_messages(n: int) -> List[str]:
    # fixed content to avoid per-iteration string building surprises
    return [f"msg {i} value={i%97}" for i in range(n)]

def _make_level_sequence(n: int, ratios: Dict[str, float]) -> List[str]:
    """
    Build a deterministic list of level names with counts proportional to ratios.
    No per-iteration RNG. Guarantees termination and predictable workload.
    """
    order = [("DEBUG", ratios.get("debug", 0.25)),
             ("INFO", ratios.get("info", 0.25)),
             ("WARNING", ratios.get("warning", 0.25)),
             ("ERROR", ratios.get("error", 0.25))]
    total = sum(p for _, p in order) or 1.0
    order = [(name, p/total) for (name, p) in order]

    # proportional counts
    counts = [int(round(n * p)) for _, p in order]
    diff = n - sum(counts)
    # fix rounding drift
    if diff != 0:
        # adjust the largest bucket
        idx = max(range(len(counts)), key=lambda i: order[i][1])
        counts[idx] += diff

    seq = []
    for (name, _), c in zip(order, counts):
        seq.extend([name] * c)
    # deterministic shuffle-like interleave to avoid long runs of same level
    # simple round-robin interleave:
    buckets = [[name] * c for (name, _), c in zip(order, counts)]
    seq_rr: List[str] = []
    offsets = [0, 0, 0, 0]
    remaining = sum(counts)
    while remaining > 0:
        progressed = False
        for i, ((name, _), c) in enumerate(zip(order, counts)):
            if offsets[i] < c:
                seq_rr.append(name)
                offsets[i] += 1
                remaining -= 1
                progressed = True
        if not progressed:  # safety
            break
    return seq_rr if seq_rr else seq

def _run_once(logger, messages: List[str], levels: List[str], do_enabled_checks: bool, max_seconds: float = 0.0):
    import logging
    # local bindings (faster attribute access)
    isEnabledFor = logger.isEnabledFor
    debug = logger.debug
    info = logger.info
    warning = logger.warning
    error = logger.error

    level_func = {
        "DEBUG": (logging.DEBUG, debug),
        "INFO": (logging.INFO, info),
        "WARNING": (logging.WARNING, warning),
        "ERROR": (logging.ERROR, error),
    }

    start = time.perf_counter()
    deadline = start + max_seconds if max_seconds > 0 else None

    # Iterate deterministically
    for m, lname in zip(messages, levels):
        lvl, fn = level_func[lname]
        if do_enabled_checks:
            if isEnabledFor(lvl):
                fn("%s", m)
        else:
            fn("%s", m)
        if deadline and time.perf_counter() >= deadline:
            break

    end = time.perf_counter()
    return end - start

# ------------------------ Benchmark core ------------------------

def _level_mix(args) -> Dict[str, float]:
    return {
        "debug": args.debug_ratio,
        "info": args.info_ratio,
        "warning": args.warning_ratio,
        "error": args.error_ratio,
    }

def run_benchmark(args) -> Dict[str, Any]:
    if args.mode == "my":
        _install_module_as_logging("my_logging.py")

    import logging

    logger = _build_logger(
        use_queue=args.use_queue,
        handler_type=args.handler,
        formatter=args.formatter,
        propagate=args.propagate,
    )

    # Effective filter level
    logger.setLevel(logging.DEBUG if args.debug_ratio > 0 else logging.INFO)

    # Prepare deterministic workload upfront
    msgs = _generate_messages(args.num_messages)
    levels = _make_level_sequence(args.num_messages, _level_mix(args))

    times: List[float] = []
    try:
        # Warmup
        for _ in range(args.warmup):
            _run_once(logger, msgs[: max(1, args.num_messages // 10)], levels[: max(1, args.num_messages // 10)],
                      args.enabled_checks, max_seconds=min(0.5, args.max_seconds))

        # Repeats (timed)
        for _ in range(args.repeat):
            dt = _run_once(logger, msgs, levels, args.enabled_checks, max_seconds=args.max_seconds)
            times.append(dt)
    finally:
        _teardown_logger(logger)

    return {
        "benchmark": "custom_logging_benchmark",
        "mode": args.mode,
        "params": {
            "num_messages": args.num_messages,
            "repeat": args.repeat,
            "warmup": args.warmup,
            "enabled_checks": args.enabled_checks,
            "use_queue": args.use_queue,
            "handler": args.handler,
            "formatter": args.formatter,
            "propagate": args.propagate,
            "debug_ratio": args.debug_ratio,
            "info_ratio": args.info_ratio,
            "warning_ratio": args.warning_ratio,
            "error_ratio": args.error_ratio,
            "max_seconds": args.max_seconds,
        },
        "stats": {
            "mean_sec": stats.mean(times) if times else None,
            "stdev_sec": stats.pstdev(times) if len(times) > 1 else 0.0,
            "runs": times,
            "throughput_msgs_per_sec": (args.num_messages / stats.mean(times)) if times and stats.mean(times) > 0 else None,
        },
        "env": {
            "python": sys.version,
            "platform": sys.platform,
        },
    }

# ------------------------ CLI ------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Enhanced logging benchmark (std vs my) — safe & deterministic")
    p.add_argument("--mode", choices=["std", "my"], required=True,
                   help="Use stdlib logging (std) or my_logging (my).")
    p.add_argument("-n", "--num-messages", type=int, default=200_000,
                   help="Number of log messages per run.")
    p.add_argument("-r", "--repeat", type=int, default=1,
                   help="How many timed runs.")
    p.add_argument("--warmup", type=int, default=1,
                   help="Warmup runs (not measured).")
    p.add_argument("--enabled-checks", action="store_true",
                   help="Use logger.isEnabledFor() guards.")
    p.add_argument("--use-queue", action="store_true",
                   help="Use QueueHandler + QueueListener (async logging).")
    p.add_argument("--handler", choices=["stream", "null", "file"], default="stream",
                   help="Handler type (avoid 'file' unless you need it).")
    p.add_argument("--formatter", choices=["message", "simple", "detailed"], default="message",
                   help="Formatter format.")
    p.add_argument("--propagate", action="store_true",
                   help="Enable propagation to parent loggers.")
    p.add_argument("--debug-ratio", type=float, default=0.7)
    p.add_argument("--info-ratio", type=float, default=0.2)
    p.add_argument("--warning-ratio", type=float, default=0.08)
    p.add_argument("--error-ratio", type=float, default=0.02)
    p.add_argument("--out", type=str, default="")
    p.add_argument("--show", action="store_true")
    p.add_argument("--max-seconds", type=float, default=0.0,
                   help="Optional safety cap per timed run (0 = unlimited).")
    args = p.parse_args()

    s = args.debug_ratio + args.info_ratio + args.warning_ratio + args.error_ratio
    if s <= 0:
        args.debug_ratio = 1.0
        args.info_ratio = args.warning_ratio = args.error_ratio = 0.0
        s = 1.0
    args.debug_ratio   /= s
    args.info_ratio    /= s
    args.warning_ratio /= s
    args.error_ratio   /= s

    if args.num_messages < 1000:
        args.num_messages = 1000
    return args

def main():
    args = parse_args()
    result = run_benchmark(args)

    mean = result["stats"]["mean_sec"]
    stdev = result["stats"]["stdev_sec"]

    # Simple one-line summary
    print(f"logging: Mean +- std dev: {mean:.3f} s +- {stdev:.3f} s")

    # Optional JSON export if --out was given
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f">> Saved results to: {args.out}")

if __name__ == "__main__":
    main()
