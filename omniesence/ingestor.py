"""
omniesence.ingestor
MultimodalIngestorInt and OMNIESENCE_Monolith classes extracted from the notebook.
"""
from __future__ import annotations
import hashlib
from typing import Dict, Any, Tuple
import numpy as np
from .ffi import NativeFFIBridge

class MultimodalIngestorInt:
    """
    Deterministically convert payload bytes into a uint64 vector, scaled by modality.
    """

    SCALING_MAP = {
        'audio': 7,
        'image': 31,
        'video': 127,
        'code': 8191,
        'linguistic': 3
    }

    def ingest_modality(self, data_type: str, raw_payload: bytes) -> np.ndarray:
        if not isinstance(raw_payload, (bytes, bytearray)):
            raise TypeError("raw_payload must be bytes")
        h = hashlib.sha512(raw_payload).digest() + hashlib.sha256(raw_payload).digest()
        base_vec = np.frombuffer(h[:96], dtype=np.uint64).copy()
        scale = self.SCALING_MAP.get(data_type, 3)
        result = ((base_vec % 50) + 1) * int(scale)
        return result.astype(np.uint64)

class OMNIESENCE_Monolith:
    """
    High-level monolith: process_pattern (ingest + stasis) and verify_coherence using NativeFFIBridge.
    """

    def __init__(self, ffi_bridge: NativeFFIBridge, target: int = 1_000_000_000, o_val: float = 0.536):
        self.ffi = ffi_bridge
        self.target = int(target)
        self.O_VAL = float(o_val)

    def process_pattern(self, data: bytes | str, modality: str = 'linguistic') -> Dict[str, Any]:
        payload = data.encode('utf-8') if isinstance(data, str) else data
        ing = MultimodalIngestorInt()
        vec = ing.ingest_modality(modality, payload)

        # 20-tier Stasis Pulse (replicates the notebook's resonance calc)
        tiers = np.arange(20, 1, -2)
        resonance = float(np.sum([np.sin(np.mean(vec) * (t / 20.0)) * self.O_VAL for t in tiers]))
        stasis = (abs((resonance * self.target) % self.target)) / float(self.target)
        return {"stasis": float(stasis), "vector": vec}

    def verify_coherence(self, vec: np.ndarray) -> bool:
        if not isinstance(vec, np.ndarray):
            raise TypeError("vec must be a numpy.ndarray")
        length = int(vec.size)
        # Construct i_vec and b_vec as in the notebook
        i_val = 1000
        i_vec = np.full(length, i_val, dtype=np.uint64)
        mean_vec = int(max(1, int(np.mean(vec))))
        b_val = max(1, self.target // (i_val * mean_vec))
        b_vec = np.full(length, b_val, dtype=np.uint64)
        tolerance = self.target // 5
        return self.ffi.check_integer_coherence(i_vec, vec.astype(np.uint64), b_vec, target=self.target, tolerance=tolerance)
