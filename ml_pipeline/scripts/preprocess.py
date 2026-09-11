"""Compatibility entry point for AI4Shipwrecks preparation.

The real dataset-cleaning implementation is maintained in
prepare_ai4shipwrecks.py. This wrapper prevents the old placeholder script
from silently reporting success without processing any data.
"""

from pathlib import Path
import subprocess
import sys


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
PREPARATION_SCRIPT = SCRIPT_DIRECTORY / "prepare_ai4shipwrecks.py"


def main() -> None:
    if not PREPARATION_SCRIPT.is_file():
        raise FileNotFoundError(
            f"Preparation script not found: {PREPARATION_SCRIPT}"
        )

    command = [
        sys.executable,
        str(PREPARATION_SCRIPT),
        *sys.argv[1:],
    ]

    completed = subprocess.run(command, check=False)

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
