"""
omniesence.monolith
Terminal/visualization helpers (FinalExactingMonolith).
"""
from __future__ import annotations
import numpy as np
from .ingestor import MultimodalIngestorInt
from typing import Sequence

class FinalExactingMonolith:
    """
    Terminal matrix modulation logic extracted from the notebook.
    """

    def __init__(self, engine, terminal_pattern: str = "±=≡=-+"):
        self.engine = engine
        self.terminal_pattern = terminal_pattern
        self.O_VAL = getattr(engine, "O_VAL", 0.536)

    def execute_terminal_ingest(self, app_id: str) -> np.ndarray:
        raw_uptake = MultimodalIngestorInt().ingest_modality('linguistic', app_id.encode('utf-8'))
        dim = 20
        matrix = np.zeros((dim, dim), dtype=float)
        for i in range(dim):
            for j in range(dim):
                # guard against indexing beyond raw_uptake
                val = float(raw_uptake[j % raw_uptake.size])
                matrix[i, j] = (val * self.O_VAL * ((20 - i) / 20.0)) % 1.0

        # Terminal Modulation Logic
        modulated = np.power(matrix, 2) % 1.0
        modulated = (modulated * 1.536 + 0.464) % 1.0
        # normalize to 0..1
        rng = modulated.max() - modulated.min()
        if rng == 0:
            return modulated
        return (modulated - modulated.min()) / rng
