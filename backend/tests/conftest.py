"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

# Ensure root and backend are in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = root_dir / "backend"

for p in [str(root_dir), str(backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)
