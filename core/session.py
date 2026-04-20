"""Load root-level session.py as core.session."""
import importlib.util
import sys
from pathlib import Path

_p = Path(__file__).resolve().parent.parent / "session.py"
_IMPL = "_shoefit_session_impl"
_spec = importlib.util.spec_from_file_location(_IMPL, _p)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
# exec 전에 등록해야 @dataclass 등이 cls.__module__ 조회 시 실패하지 않음
sys.modules[_IMPL] = _mod
_spec.loader.exec_module(_mod)
sys.modules[__name__] = _mod
