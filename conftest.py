"""
conftest.py – Root pytest configuration.

Adds the project root to sys.path so that packages like `core`, `data`,
`api`, and `config` are importable without installing the project.
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path.
sys.path.insert(0, str(Path(__file__).parent))
