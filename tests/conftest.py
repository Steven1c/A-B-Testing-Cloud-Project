import sys
from pathlib import Path

# Agar `from src.analysis...` bisa diimpor saat pytest dijalankan dari root repo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
