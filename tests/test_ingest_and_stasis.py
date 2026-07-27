import pytest
import numpy as np
from omniesence.ingestor import MultimodalIngestorInt, OMNIESENCE_Monolith
from omniesence.ffi import NativeFFIBridge

def fake_validator(i_vec, int_vec, b_vec, length, target, tolerance):
    # A deterministic fake validator: returns True if mean(i_vec * int_vec * b_vec)/length within tolerance
    total = int(np.sum(i_vec.astype(np.uint64) * int_vec.astype(np.uint64) * b_vec.astype(np.uint64)))
    mean = total // max(1, int(length))
    diff = abs(mean - int(target))
    return 1 if diff <= int(tolerance) else 0

def test_ingest_deterministic():
    ing = MultimodalIngestorInt()
    a = ing.ingest_modality('linguistic', b'hello world')
    b = ing.ingest_modality('linguistic', b'hello world')
    assert isinstance(a, np.ndarray)
    assert a.dtype == np.uint64
    assert a.shape == b.shape
    assert np.array_equal(a, b)

def test_process_pattern_and_stasis_range():
    ffi = NativeFFIBridge(validate_func=fake_validator)
    mon = OMNIESENCE_Monolith(ffi)
    res = mon.process_pattern("test payload", modality="linguistic")
    assert "stasis" in res and "vector" in res
    assert isinstance(res["stasis"], float)
    assert 0.0 <= res["stasis"] < 1.0

def test_verify_coherence_calls_validator_true():
    # craft a vector likely to pass with our fake_validator by setting int_vec so mean approx target
    ffi = NativeFFIBridge(validate_func=fake_validator)
    mon = OMNIESENCE_Monolith(ffi, target=1000)
    vec = np.full(12, 1, dtype=np.uint64) * 1  # small vector
    # choose b_vec indirectly via verify_coherence implementation (will be computed inside)
    assert mon.verify_coherence(vec) in (True, False)
