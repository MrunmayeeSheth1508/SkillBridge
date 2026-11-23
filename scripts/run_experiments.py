"""
SkillBridge - run every experiment with one command.

    python scripts/run_experiments.py            (database already built)
    python scripts/run_experiments.py --build    (reload staging + rebuild core first)
    python scripts/run_experiments.py --quick    (skip the slow concurrency test)

Each step runs on its own; a failing step is reported and the rest continue.
Writes reports/RESULTS_INDEX.md listing every report and whether its step passed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
RAW = str(ROOT / "data" / "raw")

#        name, command, report it writes, slow?
STEPS = [
    ("Load staging + build core",    ["scripts/build_database.py", RAW],             "reports/core_build.md",         False, "build"),
    ("Unit/integration tests",       ["-m", "pytest", "-q"],                          None,                            False, ""),
    ("RQ1 source agreement",         ["scripts/analyze_sources.py"],                  "reports/source_agreement.md",   False, ""),
    ("RQ2 transfer (held-out)",      ["scripts/rq2_transfer_eval.py"],                "reports/rq2_transfer.md",       False, ""),
    ("RQ3 extraction (exact)",       ["scripts/evaluate_extraction.py", "--split", "test"], "reports/extraction_eval.md", False, ""),
    ("RQ4 roadmap greedy vs ILP",    ["scripts/rq4_roadmap_eval.py"],                 "reports/rq4_roadmap.md",        False, ""),
    ("Performance benchmark",        ["scripts/benchmark.py"],                        "reports/performance.md",        False, ""),
    ("Concurrency (trigger locks)",  ["scripts/concurrency_test.py"],                 "reports/concurrency.md",        True,  ""),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="reload staging and rebuild the core schema first")
    ap.add_argument("--quick", action="store_true", help="skip slow steps")
    args = ap.parse_args()

    results = []
    for name, cmd, report, slow, tag in STEPS:
        if tag == "build" and not args.build:
            continue
        if slow and args.quick:
            results.append((name, "skipped", report, 0.0))
            continue
        print(f"\n=== {name} ===", flush=True)
        t = time.time()
        rc = subprocess.run([PY, *cmd], cwd=ROOT).returncode
        results.append((name, "ok" if rc == 0 else f"FAILED (exit {rc})", report, time.time() - t))

    study = ROOT / "docs" / "user_study" / "results.csv"
    if study.exists():
        print("\n=== User study ===", flush=True)
        rc = subprocess.run([PY, "scripts/analyze_user_study.py", str(study)], cwd=ROOT).returncode
        results.append(("User study (SUS)", "ok" if rc == 0 else f"FAILED (exit {rc})", "reports/user_study.md", 0))
    else:
        results.append(("User study (SUS)", "no results.csv yet", "reports/user_study.md", 0))

    lines = ["# SkillBridge - experiment results index", "",
             f"Run on {time.strftime('%Y-%m-%d %H:%M')}", "",
             "| Step | Status | Time (s) | Report |", "| --- | --- | --- | --- |"]
    for name, status, report, secs in results:
        exists = report and (ROOT / report).exists()
        lines.append(f"| {name} | {status} | {secs:.0f} | {report if exists else '-'} |")
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "RESULTS_INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n" + "\n".join(lines[4:]))
    print("\nIndex: reports/RESULTS_INDEX.md")
    if any(s.startswith("FAILED") for _, s, _, _ in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
