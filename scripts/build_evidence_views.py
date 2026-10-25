"""Display captured CLI records for browser screenshots, without inventing output.

These pages are explicitly labeled transcript viewers, not terminal screenshots.
Full original logs and execution metadata remain the source of truth.
"""

import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence"
VIEWS = EVIDENCE / "views"
VIEWS.mkdir(exist_ok=True)


def record(name, start=None, stop=None):
    metadata = json.loads((EVIDENCE / "logs" / f"{name}.json").read_text())
    content = (EVIDENCE / "logs" / f"{name}.txt").read_text(encoding="utf-8")
    if start:
        content = content[content.index(start):]
    if stop:
        content = content[:content.index(stop)]
    command = subprocess.list2cmdline(metadata["command"])
    excerpt = "excerpt" if start or stop else "complete output"
    return f'''<section><div class="command">{html.escape(command)}</div>
<div class="meta">{html.escape(metadata['started_at'])} | exit {metadata['exit_code']} | {excerpt} |
<a href="../logs/{name}.txt">original log</a></div><pre>{html.escape(content.strip())}</pre></section>'''


def page(number, title, records, note=""):
    body = "".join(record(*item) if isinstance(item, tuple) else record(item) for item in records)
    document = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Milestone {number} - {title}</title>
<style>body{{font:15px system-ui,sans-serif;color:#152338;background:#f6f8fc;margin:24px 32px}}
h1{{font-size:25px;margin:4px 0 6px}}header{{border-left:5px solid #6d28d9;padding-left:16px;margin-bottom:18px}}
p{{margin:5px 0;color:#43516a}}section{{background:#fff;border:1px solid #ccd4e1;border-radius:8px;margin:12px 0;overflow:hidden}}
.command{{font:14px Consolas,monospace;color:#fff;background:#1e3a8a;padding:10px 14px;overflow-wrap:anywhere}}
.meta{{padding:6px 14px;background:#eef2ff;font-size:12px;color:#43516a}}a{{color:#1d4ed8}}
pre{{font:13px/1.4 Consolas,monospace;margin:12px 14px;white-space:pre-wrap;overflow-wrap:anywhere}}
.note{{font-size:13px}}.eyebrow{{font-size:12px;letter-spacing:1px;color:#6d28d9;font-weight:700}}</style>
<header><div class="eyebrow">SDI 4213 / WEEK 9 / RECORDED CLI EVIDENCE</div><h1>Milestone {number} - {title}</h1>
<p>Read-only transcript viewer. Output comes from actual local command executions.</p></header>{body}<p class="note">{html.escape(note)}</p></html>'''
    (VIEWS / f"milestone-{number:02d}.html").write_text(document, encoding="utf-8")


page(1, "Baseline application and tests", ["baseline-tests"],
     "The unchanged baseline image passes both tests; service startup and browser screenshots are preserved separately.")
page(2, ".env protected from Git", ["env-ignored", "env-untracked", "branch-status"],
     "Exit 1 from git ls-files is expected here: Git has no tracked .env. Its contents were never displayed.")
page(4, "Baseline Docker Scout CVE scan", [("baseline-cves", "## Overview", "## Packages and Vulnerabilities")],
     "This excerpt preserves Scout's severity summary. The full log reports 19 vulnerable packages and 97 findings.")
page(5, "Docker Scout recommendations / SBOM evidence", [("baseline-recommendations", " Target", "Change base image")],
     "Observation: Scout identifies python:3.13-slim as up to date, while the base still has reported vulnerabilities.")
page(7, "Non-root container verification", ["hardened-uid", "baseline-uid"],
     "The hardened image returns 10001; the preserved baseline returns 0. Only the hardened image satisfies the policy.")
print(f"Created five transcript views in {VIEWS}")
