import numpy as np
from omniesence.ffi import NativeFFIBridge

def test_ffi_with_python_callable():
    def always_true(i_vec, int_vec, b_vec, length, target, tolerance):
        assert isinstance(i_vec, np.ndarray)
        assert isinstance(int_vec, np.ndarray)
        assert isinstance(b_vec, np.ndarray)
        return 1

    bridge = NativeFFIBridge(validate_func=always_true)
    i_vec = np.full(12, 1000, dtype=np.uint64)
    int_vec = np.full(12, 250000, dtype=np.uint64)
    b_vec = np.full(12, 4, dtype=np.uint64)
    assert bridge.check_integer_coherence(i_vec, int_vec, b_vec, target=1_000_000_000, tolerance=200_000_000) is True
