import pickle as pk
from pathlib import Path
from typing import Any

def save_pk(x: Any, path: Path):
    with open(path, 'wb') as f:
        pk.dump(x, f)

def load_pk(path: str | Path):
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x