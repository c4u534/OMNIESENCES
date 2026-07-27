"""
omniesence.ffi
A thin, test-friendly FFI wrapper around the native validate_integer_zeroth_law function.
Allows injection of a Python callable for testing so unit tests do not need a compiled .so.
"""
from __future__ import annotations
from typing import Callable, Optional
import ctypes
import numpy as np

ValidateCallable = Callable[[np.ndarray, np.ndarray, np.ndarray, int, int, int], int]

class NativeFFIBridge:
    """
    Wrapper to call the native validator.

    Usage:
      - In production: NativeFFIBridge(lib_path="/path/to/libqme_core_*.so")
      - In tests: NativeFFIBridge(validate_func=fake_callable)
    """

    def __init__(self, lib_path: Optional[str] = None, validate_func: Optional[ValidateCallable] = None):
        self._use_ctypes = False
        if validate_func is not None:
            # Use the injected python callable for testing.
            self._validate = validate_func
            self._use_ctypes = False
            return

        if lib_path is None:
            raise ValueError("Either lib_path or validate_func must be provided")

        # Load the shared lib and configure ctypes signature
        self.lib = ctypes.CDLL(lib_path)
        # define argtypes/restype consistent with the C signature
        self.lib.validate_integer_zeroth_law.argtypes = [
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint64
        ]
        self.lib.validate_integer_zeroth_law.restype = ctypes.c_int
        self._validate = self.lib.validate_integer_zeroth_law
        self._use_ctypes = True

    def check_integer_coherence(self, i_vec: np.ndarray, int_vec: np.ndarray, b_vec: np.ndarray, target: int, tolerance: int) -> bool:
        """
        Call the underlying validator. Accepts numpy arrays of dtype uint64.
        When using the real .so, this method converts arrays to ctypes pointers.
        When using an injected python callable, the callable will be invoked directly.
        """
        if not (isinstance(i_vec, np.ndarray) and isinstance(int_vec, np.ndarray) and isinstance(b_vec, np.ndarray)):
            raise TypeError("i_vec, int_vec, and b_vec must be numpy arrays")

        if self._use_ctypes:
            # Convert to ctypes pointers and call the C function
            i_ptr = i_vec.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
            int_ptr = int_vec.astype(np.uint64).ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
            b_ptr = b_vec.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
            length = int(int_vec.size)
            res = self._validate(i_ptr, int_ptr, b_ptr, length, ctypes.c_uint64(target), ctypes.c_uint64(tolerance))
            return bool(res)
        else:
            # Call Python callable with numpy arrays and python ints
            res = self._validate(i_vec, int_vec, b_vec, int(int_vec.size), int(target), int(tolerance))
            return bool(res)
