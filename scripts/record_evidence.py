"""Record real command output and provenance; never pass credentials as arguments."""

import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def main():
    if len(sys.argv) < 3 or not re.fullmatch(r"[a-z0-9-]+", sys.argv[1]):
        raise SystemExit("Usage: python scripts/record_evidence.py record-name command [args ...]")
    sys.stdout.reconfigure(encoding="utf-8")
    name, command = sys.argv[1], sys.argv[2:]
    directory = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {"command": command, "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    environment = {**os.environ, "NO_COLOR": "1", "TERM": "dumb", "DOCKER_CLI_HINTS": "false"}
    with (directory / f"{name}.txt").open("w", encoding="utf-8") as output:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace", env=environment)
        for line in process.stdout:
            output.write(line)
            output.flush()
            print(line, end="", flush=True)
        metadata["exit_code"] = process.wait()
    metadata["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (directory / f"{name}.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(metadata["exit_code"])


if __name__ == "__main__":
    main()
