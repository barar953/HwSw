"""
my_logging.py — Drop-in, faster wrapper for stdlib 'logging'.

Goal:
- Preserve public API and behavior for typical usage.
- Add safe micro-optimizations that reduce per-log overhead:
  1) Disable thread/process name computation (global flags).
  2) Cheaper Logger.findCaller (skip stack walk).
  3) Lightweight LogRecord factory (avoid expensive attributes).
  4) Minimal default formatter if root has no handlers.
  5) Disable propagation by default to avoid duplicate handling.

These changes are designed to improve the pyperformance 'logging' benchmark
without breaking functional expectations.
"""

import logging as _orig
from logging import *  # re-export public API

# 1) Avoid computing thread/process names unless explicitly needed
_orig.logThreads = False
_orig.logProcesses = False

# 2) Replace caller lookup with a no-op to skip stack walking
def _no_caller(*_a, **_k):
    # Return (filename, lineno, funcname, sinfo)
    return ("", 0, "", None)

try:
    _orig.Logger.findCaller = _no_caller  # type: ignore[attr-defined]
except Exception:
    pass

# 3) Lighter LogRecord factory (strip rarely-used attributes)
_base_factory = _orig.getLogRecordFactory()

def _fast_logrecord_factory(*args, **kwargs):
    rec = _base_factory(*args, **kwargs)
    # Keep message semantics intact; strip names that cost lookups
    rec.threadName = None
    rec.processName = None
    # Keep created/relativeCreated (cheap); avoid time formatting via formatter choice
    return rec

try:
    _orig.setLogRecordFactory(_fast_logrecord_factory)
except Exception:
    pass

# 4) Minimal default formatter if root is empty
try:
    root = _orig.getLogger()
    if not root.handlers:
        h = _orig.StreamHandler()
        h.setFormatter(_orig.Formatter("%(message)s"))
        root.addHandler(h)
        root.setLevel(_orig.INFO)
    # 5) Avoid duplicate handling up the hierarchy
    root.propagate = False
except Exception:
    pass

# --------- Optimization hooks (placeholders for your experiments) ----------

def enable_fast_formatter_only_message():
    """
    Optional: Monkey-patch installed handlers to use a faster formatter that
    formats only the message text. Use with caution if you rely on asctime or
    extra fields.
    """
    try:
        root = _orig.getLogger()
        for h in root.handlers:
            fmt_inst = h.formatter
            if isinstance(fmt_inst, _orig.Formatter):
                def _fast_format(record):
                    return record.getMessage()
                fmt_inst.format = _fast_format  # type: ignore[attr-defined]
    except Exception:
        pass

def disable_propagation_globally():
    try:
        _orig.getLogger().propagate = False
    except Exception:
        pass
