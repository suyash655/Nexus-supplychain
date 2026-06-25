import numpy as np

def _safe_str(val):
    if val is None:
        return None
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    s = str(val).strip()
    if s.lower() in ("nan", "none", "nat", ""):
        return None
    return s

def _safe_int(val, default=0):
    try:
        if val is None:
            return default
        if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
            return default
        return int(float(val))
    except:
        return default

def _safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return default
        return f
    except:
        return default
