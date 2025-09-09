#!/usr/bin/env python3
"""
Run stdlib logging and my_logging in the same process, same thread,
with a fixed timestamp, and compare outputs byte-for-byte.
"""

import io, sys, importlib.util, os, time

# --- Fixed-time formatter (keeps output identical across runs) ---
import logging as stdlog


class FixedTimeFormatter(stdlog.Formatter):
    def __init__(self, fmt, fixed_epoch):
        super().__init__(fmt)
        self.fixed_epoch = fixed_epoch

    def formatTime(self, record, datefmt=None):
        """
        Return a fully fixed timestamp, ignoring record.created/msecs so both
        STD and MY produce byte-identical output.
        """
        ct = time.localtime(self.fixed_epoch)
        if datefmt:
            return time.strftime(datefmt, ct)
        # Use fixed seconds + fixed milliseconds (000) to avoid per-record jitter
        base = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return f"{base},000"

def build_logger(mod, stream, fmt, fixed_epoch):
    """Build a logger for either stdlib logging (mod=stdlog) or my_logging (mod=mylog)."""
    lg = mod.getLogger("demo")
    lg.handlers[:] = []
    lg.propagate = False
    lg.setLevel(mod.DEBUG)
    h = mod.StreamHandler(stream)
    # Use fixed-time formatter so timestamps are identical
    h.setFormatter(FixedTimeFormatter(fmt, fixed_epoch))
    lg.addHandler(h)
    return lg

def load_my_logging_module():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "my_logging.py")
    spec = importlib.util.spec_from_file_location("my_logging", path)
    my = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(my)  # type: ignore
    return my

def emit_sequence(lg_module, logger):
    """Emit the exact same log sequence (caller/process/thread/asctime are requested)."""
    # NOTE: Single thread => same TID; same process => same PID
    logger.debug("warmup start")
    logger.info("iteration=%d starting", 0)
    logger.warning("check point i=%d", 0)
    logger.info("iteration=%d starting", 1)
    try:
        raise ValueError("demo error")
    except Exception:
        logger.exception("caught exception (i=%d)", 1)
    logger.warning("check point i=%d", 1)
    logger.info("iteration=%d starting", 2)
    logger.warning("check point i=%d", 2)
    logger.error("final error code=%d", 42)

def main():
    # Realistic format using caller/process/thread/time fields
    fmt = "%(asctime)s %(levelname)s %(name)s [pid=%(process)d tid=%(thread)d] %(filename)s:%(lineno)d - %(message)s"
    fixed_epoch = 1_725_875_200  # any fixed epoch; here just an example

    # STD run
    buf_std = io.StringIO()
    lg_std = build_logger(stdlog, buf_std, fmt, fixed_epoch)
    emit_sequence(stdlog, lg_std)
    out_std = buf_std.getvalue()

    # MY run (same process, same thread, fixed time)
    mylog = load_my_logging_module()
    # Ensure my_logging detects the formatter fields
    if hasattr(mylog, "refresh_logging_needs"):
        mylog.refresh_logging_needs()
    buf_my = io.StringIO()
    lg_my = build_logger(mylog, buf_my, fmt, fixed_epoch)
    emit_sequence(mylog, lg_my)
    out_my = buf_my.getvalue()

    # Compare
    if out_std == out_my:
        print("OK: Outputs are IDENTICAL.")
    else:
        sys.stdout.write("DIFF START\n")
        import difflib
        for line in difflib.unified_diff(
            out_std.splitlines(True), out_my.splitlines(True),
            fromfile="STD", tofile="MY"
        ):
            sys.stdout.write(line)

if __name__ == "__main__":
    main()
