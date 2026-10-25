"""Exercise the actual workflow shell steps against safe and unsafe fixtures.

Requires PyYAML, Git Bash (on Windows), and the before/after Docker images.
Fixtures contain only a dummy value and stay under ignored tmp/.
"""

import os
from pathlib import Path
import subprocess
import uuid

import yaml


ROOT = Path(__file__).resolve().parents[1]
workflow = yaml.safe_load((ROOT / ".github/workflows/security.yml").read_text())
steps = workflow["jobs"]["security-policy"]["steps"]
secret_check = next(step["run"] for step in steps if step["name"] == "Reject a tracked .env file")
uid_check = next(step["run"] for step in steps if step["name"] == "Require a non-root runtime user")
bash = r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "bash"
fixture = ROOT / "tmp" / f"policy-{uuid.uuid4().hex}"
fixture.mkdir(parents=True)
subprocess.run(["git", "init", "-q", str(fixture)], check=True)


def expect(label, script, passes, cwd=ROOT):
    result = subprocess.run([bash, "-c", script], cwd=cwd, capture_output=True, text=True)
    print(f"\n{label}\n{result.stdout}{result.stderr}Exit code: {result.returncode}", flush=True)
    assert (result.returncode == 0) == passes, f"Unexpected policy outcome: {label}"
    print("Expected outcome verified.", flush=True)


expect("Untracked .env: policy accepts", secret_check, True, fixture)
(fixture / ".env").write_text("POSTGRES_PASSWORD=dummy-policy-test-only\n")
subprocess.run(["git", "add", ".env"], cwd=fixture, check=True)
expect("Tracked dummy .env: policy rejects", secret_check, False, fixture)
expect("Baseline root image: policy rejects", uid_check.replace("helpdesk:security", "helpdesk:week9-before"), False)
expect("Hardened image: policy accepts", uid_check, True)
print("\nAll four policy scenarios passed; no fixture was committed or pushed.")
