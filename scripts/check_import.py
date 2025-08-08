import sys, importlib, traceback
print("sys.path:", sys.path)
try:
    m = importlib.import_module("backend.main")
    print("OK: backend.main imported; has app:", hasattr(m, "app"))
except Exception:
    traceback.print_exc()
    raise