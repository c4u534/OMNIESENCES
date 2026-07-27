"""
omniesence.kernel
Helpers to write & compile the native C kernel used by the substrate.
"""
from __future__ import annotations
import os
import time
import subprocess
from typing import Optional

C_SOURCE = r"""
#include <stdint.h>
#include <stdlib.h>
int validate_integer_zeroth_law(const uint64_t* i_vec, const uint64_t* int_vec, const uint64_t* b_vec, size_t length, uint64_t target, uint64_t tolerance) {
    // Note: This implementation uses 64-bit accumulators and can overflow for certain inputs.
    uint64_t total_product = 0;
    for (size_t k = 0; k < length; k++) {
        total_product += (i_vec[k] * int_vec[k] * b_vec[k]);
    }
    uint64_t mean_product = total_product / length;
    uint64_t diff = (mean_product > target) ? (mean_product - target) : (target - mean_product);
    return (diff <= tolerance) ? 1 : 0;
}
"""

def compile_kernel(base_dir: str, out_name_prefix: str = "libqme_core") -> str:
    """
    Write the C source to base_dir/lib and compile a shared object using gcc.
    Returns the path to the compiled .so file.
    Raises subprocess.CalledProcessError if compilation fails.
    """
    lib_dir = os.path.join(base_dir, "lib")
    os.makedirs(lib_dir, exist_ok=True)
    timestamp = int(time.time())
    so_path = os.path.join(lib_dir, f"{out_name_prefix}_{timestamp}.so")
    c_path = so_path.replace(".so", ".c")
    with open(c_path, "w", encoding="utf-8") as f:
        f.write(C_SOURCE)
    # Compile with gcc. Caller must ensure a POSIX toolchain is available.
    subprocess.run(["gcc", "-O3", "-shared", "-fPIC", c_path, "-o", so_path], check=True)
    return so_path
