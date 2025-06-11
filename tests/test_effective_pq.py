import os
import sys
import types
import pytest

sys.modules.setdefault("flask", types.ModuleType("flask"))
class DummyFlask:
    def __init__(self, *a, **k):
        self.config = {}

    def route(self, *a, **k):
        def decorator(f):
            return f
        return decorator

sys.modules["flask"].Flask = DummyFlask
sys.modules["flask"].render_template = lambda *a, **k: None
sys.modules["flask"].request = None
sys.modules["flask"].jsonify = lambda *a, **k: None

sys.modules.setdefault("flask_socketio", types.ModuleType("flask_socketio"))
class DummySocketIO:
    def __init__(self, *a, **k):
        pass

    def on(self, *a, **k):
        def decorator(f):
            return f
        return decorator

    def start_background_task(self, *a, **k):
        return None

    def emit(self, *a, **k):
        pass

    def run(self, *a, **k):
        pass

sys.modules["flask_socketio"].SocketIO = DummySocketIO

sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules["numpy"].pi = 3.141592653589793

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import calculate_effective_pq


def test_calculate_effective_pq_zero_p():
    """La función no debería lanzar excepción cuando p es cero."""
    result = calculate_effective_pq(
        sigma3=0,
        H0=1,
        D0=1,
        DH0=0,
        DV0=0,
        PP0=0,
        displacement=0,
        force=0,
        volume=0,
        pressure=0,
    )
    assert result["qp"] == 0.0

