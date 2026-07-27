"""
scripts/cleanup.py
Remove generated compiled artifacts and exported scripts created by the notebook.
"""
from __future__ import annotations
import os
import glob

def cleanup_generated(base_dir: str = "./sovereign_substrate") -> int:
    """
    Remove generated files (.so, .c) in base_dir/lib and nodal_deploy.py in cwd.
    Returns the number of files removed.
    """
    removed = 0
    patterns = [
        os.path.join(base_dir, "lib", "libqme_core_*.so"),
        os.path.join(base_dir, "lib", "libqme_core_*.c"),
        "nodal_deploy.py",
        "nodal_deploy.pyc"
    ]
    for pat in patterns:
        for p in glob.glob(pat):
            try:
                os.remove(p)
                removed += 1
            except OSError:
                pass
    return removed

if __name__ == "__main__":
    n = cleanup_generated()
    print(f"[CLEANUP] Removed {n} generated files.")
