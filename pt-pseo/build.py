"""Thin wrapper to run the shared non-pharm vertical builder."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from vertical_build_common import build_vertical


if __name__ == "__main__":
    build_vertical(ROOT)
