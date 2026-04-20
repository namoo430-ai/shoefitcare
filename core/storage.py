"""Load root-level storage.py as core.storage."""
import importlib.util
import sys
from pathlib import Path

_p = Path(__file__).resolve().parent.parent / "storage.py"
_IMPL = "_shoefit_storage_impl"
_spec = importlib.util.spec_from_file_location(_IMPL, _p)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules[_IMPL] = _mod
_spec.loader.exec_module(_mod)
sys.modules[__name__] = _mod
