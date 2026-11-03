import subprocess
import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent / "back"

if __name__ == "__main__":
    try:
        exit_code = subprocess.call([sys.executable, "app.py"], cwd=BACK_DIR)
    except KeyboardInterrupt:
        # Ctrl+C also reaches the server process; avoid a launcher traceback.
        exit_code = 130
    sys.exit(exit_code)
