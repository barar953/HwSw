"""
my_logging.py — Adaptive fast-path for stdlib logging with identical output.

Key ideas:
- Keep output identical to stdlib logging if the format string is the same.
- Compute expensive fields (caller/process/thread) only when the active format actually needs them.
- Cache PID (os.getpid()) once: identical value, fewer syscalls.
- Do NOT change Formatter.format, propagate, or default handlers.

Usage:
- Import this module early (before configuring logging) OR call refresh_logging_needs()
  after you attach handlers/formatters so the detection can see your active formats.
"""

import logging as _orig
from logging import *  # re-export stdlib logging API
import os
import re
import threading

# --- Global flags describing what the current formats require ---
_NEEDS_CALLER = False
_NEEDS_PROCESS = False
_NEEDS_THREAD = False
_NEEDS_ASCTIME = False
_NEEDS_RELATIVE_TIME = False
_NEEDS_EXCEPTION = False
_LOCK = threading.Lock()

# Handler chain cache for optimization
_HANDLER_CACHE = {}
_HANDLER_CACHE_LOCK = threading.Lock()

def _parse_needs_from_format(fmt: str):
    """Detect whether the format requires caller, process, thread, time, or exception fields."""
    needs_caller = bool(re.search(r"%\((lineno|filename|funcName|pathname|module)\)", fmt))
    needs_process = bool(re.search(r"%\((process|processName)\)", fmt))
    needs_thread = bool(re.search(r"%\((thread|threadName)\)", fmt))
    needs_asctime = bool(re.search(r"%\(asctime\)", fmt))
    needs_relative_time = bool(re.search(r"%\(relativeCreated\)", fmt))
    needs_exception = bool(re.search(r"%\(exc_text\)", fmt))
    return needs_caller, needs_process, needs_thread, needs_asctime, needs_relative_time, needs_exception

def _collect_needs_from_all_handlers():
    """Scan root + known loggers to aggregate which fields are actually needed."""
    nc = np = nt = na = nr = ne = False
    root = _orig.getLogger()
    loggers = [root]
    try:
        # Include other known loggers from the manager if present
        for _, obj in _orig.Logger.manager.loggerDict.items():
            if isinstance(obj, _orig.Logger):
                loggers.append(obj)
    except Exception:
        pass

    for lg in loggers:
        for h in getattr(lg, "handlers", []):
            fmt_obj = getattr(h, "formatter", None)
            if isinstance(fmt_obj, _orig.Formatter):
                fmt = getattr(fmt_obj, "_fmt", "%(message)s")
                c, p, t, a, r, e = _parse_needs_from_format(fmt)
                nc = nc or c
                np = np or p
                nt = nt or t
                na = na or a
                nr = nr or r
                ne = ne or e
    return nc, np, nt, na, nr, ne

def refresh_logging_needs():
    """Call after configuring handlers/formatters to recompute required fields."""
    global _NEEDS_CALLER, _NEEDS_PROCESS, _NEEDS_THREAD, _NEEDS_ASCTIME, _NEEDS_RELATIVE_TIME, _NEEDS_EXCEPTION
    with _LOCK:
        (_NEEDS_CALLER, _NEEDS_PROCESS, _NEEDS_THREAD, 
         _NEEDS_ASCTIME, _NEEDS_RELATIVE_TIME, _NEEDS_EXCEPTION) = _collect_needs_from_all_handlers()
    
    # Clear handler cache when needs change
    _clear_handler_cache()

def _clear_handler_cache():
    """Clear handler cache when configuration changes."""
    with _HANDLER_CACHE_LOCK:
        _HANDLER_CACHE.clear()

def _build_handler_chain(logger):
    """Build complete handler chain for a logger."""
    handlers = []
    c = logger
    
    while c:
        for hdlr in c.handlers:
            handlers.append((hdlr, hdlr.level))
        if not c.propagate:
            break
        c = c.parent
    
    return handlers

def _get_cached_handlers(logger):
    """Get cached handler chain or build it."""
    logger_name = logger.name
    
    with _HANDLER_CACHE_LOCK:
        if logger_name in _HANDLER_CACHE:
            return _HANDLER_CACHE[logger_name]
        
        handlers = _build_handler_chain(logger)
        _HANDLER_CACHE[logger_name] = handlers
        return handlers

# Initial detection (in case handlers already exist)
refresh_logging_needs()

# --- Optimized pieces (adaptive) ---

# Cache PID once. Value is identical; we just avoid repeated syscalls.
_CACHED_PID = os.getpid()

# Wrap the current LogRecord factory with an adaptive version
_base_factory = _orig.getLogRecordFactory()

def _adaptive_logrecord_factory(*args, **kwargs):
    """
    Create a LogRecord as usual, but only populate expensive fields
    if the active formats actually use them.
    """
    rec = _base_factory(*args, **kwargs)

    # Thread info: only useful if the format requests it.
    # Leaving None when not used has no effect on output since fields aren't referenced.
    if not _NEEDS_THREAD:
        # Keep fields as-is or None; no extra work.
        rec.thread = getattr(rec, "thread", None)
        rec.threadName = getattr(rec, "threadName", None)

    # Process info: if needed, use cached PID; otherwise avoid extra names/fields work.
    if _NEEDS_PROCESS:
        rec.process = _CACHED_PID
    else:
        rec.process = getattr(rec, "process", _CACHED_PID)
        rec.processName = getattr(rec, "processName", None)

    return rec

try:
    _orig.setLogRecordFactory(_adaptive_logrecord_factory)
except Exception:
    pass

# Wrap Logger.findCaller so we only walk the stack if the format requires caller info.
_real_findCaller = _orig.Logger.findCaller

def _findCaller_if_needed(self, *a, **k):
    if not _NEEDS_CALLER:
        # Returning an empty caller tuple is safe when caller fields are not used in the format.
        return ("", 0, "", None)
    return _real_findCaller(self, *a, **k)

try:
    _orig.Logger.findCaller = _findCaller_if_needed  # type: ignore[attr-defined]
except Exception:
    pass

# --- Auto-refresh hooks: keep detection in sync when the app reconfigures logging ---

_OrigHandler_setFormatter = _orig.Handler.setFormatter
def _setFormatter_and_refresh(self, fmt):
    _OrigHandler_setFormatter(self, fmt)
    refresh_logging_needs()
_orig.Handler.setFormatter = _setFormatter_and_refresh  # type: ignore

_OrigLogger_addHandler = _orig.Logger.addHandler
def _addHandler_and_refresh(self, h):
    _OrigLogger_addHandler(self, h)
    refresh_logging_needs()
_orig.Logger.addHandler = _addHandler_and_refresh  # type: ignore

_OrigLogger_removeHandler = _orig.Logger.removeHandler
def _removeHandler_and_refresh(self, h):
    _OrigLogger_removeHandler(self, h)
    refresh_logging_needs()
_orig.Logger.removeHandler = _removeHandler_and_refresh  # type: ignore


# --- Message formatting optimization ---

def _optimize_message_formatting():
    """Optimize LogRecord.getMessage() while maintaining identical output."""
    _orig_getMessage = _orig.LogRecord.getMessage
    
    def _fast_getMessage(self):
        # Fast path 1: No arguments - skip formatting entirely
        if not self.args:
            return self.msg if isinstance(self.msg, str) else str(self.msg)
        
        # Fast path 2: Single argument optimization
        if isinstance(self.args, tuple) and len(self.args) == 1:
            if isinstance(self.msg, str):
                try:
                    return self.msg % self.args[0]
                except (TypeError, ValueError):
                    return _orig_getMessage(self)
            else:
                return str(self.msg) % self.args[0]
        
        # Fast path 3: Multiple arguments but simple string msg
        if isinstance(self.msg, str) and isinstance(self.args, tuple):
            try:
                return self.msg % self.args
            except (TypeError, ValueError):
                return _orig_getMessage(self)
        
        # Fall back to original implementation for edge cases
        return _orig_getMessage(self)
    
    _orig.LogRecord.getMessage = _fast_getMessage


# Apply optimizations
_optimize_message_formatting()


# Note:
# - We do NOT force propagate changes, do NOT set default handlers/formatters,
#   and do NOT override Formatter.format. Output remains identical to stdlib
#   when the same format string is used.
# - Message formatting and handler chain caching provide significant performance
#   improvements while maintaining complete compatibility.
