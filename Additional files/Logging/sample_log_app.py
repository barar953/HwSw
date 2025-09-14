#!/usr/bin/env python3
import io, sys, importlib.util, os, time
import logging as stdlog

# --- Fixed-time formatter (keeps output identical across runs) ---
class FixedTimeFormatter(stdlog.Formatter):
    def __init__(self, fmt, fixed_epoch):
        super().__init__(fmt)
        self.fixed_epoch = fixed_epoch

    def formatTime(self, record, datefmt=None):
        ct = time.localtime(self.fixed_epoch)
        if datefmt:
            return time.strftime(datefmt, ct)
        base = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return f"{base},000"

def build_logger(mod, stream, fmt, fixed_epoch):
    lg = mod.getLogger("demo")
    lg.handlers[:] = []
    lg.propagate = False
    lg.setLevel(mod.DEBUG)
    h = mod.StreamHandler(stream)
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

def save_log(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    fmt = "%(asctime)s %(levelname)s %(name)s [pid=%(process)d tid=%(thread)d] %(filename)s:%(lineno)d - %(message)s"
    fixed_epoch = 1_725_875_200

    # STD run
    buf_std = io.StringIO()
    lg_std = build_logger(stdlog, buf_std, fmt, fixed_epoch)
    emit_sequence(stdlog, lg_std)
    out_std = buf_std.getvalue()
    print("=== STD OUTPUT ===")
    print(out_std)
    save_log("std_log.txt", out_std)

    # MY run
    mylog = load_my_logging_module()
    if hasattr(mylog, "refresh_logging_needs"):
        mylog.refresh_logging_needs()
    buf_my = io.StringIO()
    lg_my = build_logger(mylog, buf_my, fmt, fixed_epoch)
    emit_sequence(mylog, lg_my)
    out_my = buf_my.getvalue()
    print("=== MY OUTPUT ===")
    print(out_my)
    save_log("my_log.txt", out_my)

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
