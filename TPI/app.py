import subprocess
import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent / "back"

if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "app.py"], cwd=BACK_DIR))
