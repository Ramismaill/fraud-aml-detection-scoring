"""Central configuration for the M1 pilot.

Import from every notebook (notebooks run from C:/m1/repo/notebooks):
    import sys; sys.path.insert(0, "..")
    from src.config import PATHS, SEED, DUCKDB_FILE, duckdb_connect, Timer
"""
from pathlib import Path
import os
import time

import duckdb
import psutil

SEED = 42  # used for every random_state in the project

PATHS = {
    "raw":      Path("D:/m1/raw"),       # original Kaggle downloads, never edited
    "lake":     Path("D:/m1/lake"),      # clean Parquet archive (HDD)
    "work":     Path("C:/m1/work"),      # working Parquet + DuckDB file (fast SSD)
    "duck_tmp": Path("C:/m1/duck_tmp"),  # DuckDB spill directory
    "repo":     Path("C:/m1/repo"),      # git repo, code only
}
for _p in PATHS.values():
    _p.mkdir(parents=True, exist_ok=True)

DUCKDB_FILE = PATHS["work"] / "m1.duckdb"


def duckdb_connect(db_file=DUCKDB_FILE, memory_limit="9GB", threads=8):
    """Open the project DuckDB file with the agreed memory/thread/spill settings."""
    con = duckdb.connect(str(db_file))
    con.execute(f"SET memory_limit = '{memory_limit}'")
    con.execute(f"SET threads = {threads}")
    con.execute(f"SET temp_directory = '{PATHS['duck_tmp'].as_posix()}'")
    con.execute("SET max_temp_directory_size = '20GB'")
    return con


class Timer:
    """Context manager that prints wall time and RAM of this process.

    Usage:
        with Timer("load BAF"):
            df = pd.read_parquet(...)
    Peak RSS is Windows-only (peak_wset); on other OS it prints 0.
    """
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.t0 = time.perf_counter()
        self.proc = psutil.Process(os.getpid())
        return self

    def __exit__(self, *exc):
        dt = time.perf_counter() - self.t0
        mi = self.proc.memory_info()
        rss = mi.rss / 1e9
        peak = getattr(mi, "peak_wset", 0) / 1e9
        print(f"[{self.label}] wall = {dt:,.1f} s | RSS now = {rss:.2f} GB | peak RSS = {peak:.2f} GB")