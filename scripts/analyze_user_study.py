"""
SkillBridge - analyse the user study.

    python scripts/analyze_user_study.py docs/user_study/results.csv

Input: one row per participant (template: docs/user_study/results_template.csv).
SUS scoring (Brooke 1996): odd items contribute (answer - 1), even items (5 - answer);
the sum x 2.5 gives 0-100. Adjective grades follow Bangor, Kortum & Miller (2009).
Writes reports/user_study.md
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "user_study.md"
TASKS = ["t1", "t2", "t3", "t4", "t5", "t6"]
TASK_NAMES = {"t1": "Add skills to profile", "t2": "Choose a career, read readiness",
              "t3": "Explain the top gap", "t4": "Find a transfer credit",
              "t5": "Build an 8-week roadmap", "t6": "Compare two careers"}
T_CRIT = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26,
          10: 2.23, 12: 2.18, 15: 2.13, 20: 2.09, 30: 2.04}


def t_crit(df: int) -> float:
    return T_CRIT[max(k for k in T_CRIT if k <= df)] if df >= 1 else float("nan")


def sus_score(row: dict) -> float:
    total = 0
    for i in range(1, 11):
        v = int(row[f"sus{i}"])
        if not 1 <= v <= 5:
            raise ValueError(f"sus{i}={v} outside 1-5")
        total += (v - 1) if i % 2 else (5 - v)
    return total * 2.5


def grade(score: float) -> str:
    for limit, label in [(85.6, "Excellent (A)"), (72.6, "Good (B-C)"), (52.0, "OK (D)"), (38.0, "Poor (E)")]:
        if score >= limit:
            return label
    return "Awful (F)"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/analyze_user_study.py docs/user_study/results.csv")
    with open(sys.argv[1], newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("participant") and not r["participant"].startswith("EXAMPLE")]
    if not rows:
        sys.exit("No participant rows (rows starting with EXAMPLE are ignored).")

    scores, errors = [], []
    for r in rows:
        try:
            scores.append((r["participant"], sus_score(r)))
        except (ValueError, KeyError) as e:
            errors.append(f"{r['participant']}: {e}")
    vals = [s for _, s in scores]
    n = len(vals)
    mean = statistics.mean(vals) if vals else float("nan")
    sd = statistics.stdev(vals) if n > 1 else 0.0
    half = t_crit(n - 1) * sd / math.sqrt(n) if n > 1 else float("nan")

    out = ["# User study results", "", f"- Participants: **{len(rows)}**",
           f"- SUS: **{mean:.1f}** ± {sd:.1f} (SD), 95% CI [{mean - half:.1f}, {mean + half:.1f}] - "
           f"**{grade(mean)}**; the industry average is about 68", ""]
    if errors:
        out += ["Rows with invalid SUS answers (excluded): " + "; ".join(errors), ""]

    out += ["## Task performance", "", "| Task | Success | Partial | Fail | Success rate | Median time (s) |",
            "| --- | --- | --- | --- | --- | --- |"]
    for t in TASKS:
        oc = [r.get(f"{t}_outcome", "").strip().lower() for r in rows]
        secs = [float(r[f"{t}_seconds"]) for r in rows if r.get(f"{t}_seconds", "").strip()]
        k = sum(o in ("success", "partial", "fail") for o in oc)
        s, p, fl = oc.count("success"), oc.count("partial"), oc.count("fail")
        out.append(f"| {t.upper()} {TASK_NAMES[t]} | {s} | {p} | {fl} | "
                   f"{(s / k * 100 if k else 0):.0f}% | {statistics.median(secs) if secs else float('nan'):.0f} |")

    for col, label in [("roadmap_order", "The roadmap's order made sense"),
                       ("trust_evidence", "I trust the gaps because I can see the sources")]:
        v = [int(r[col]) for r in rows if r.get(col, "").strip().isdigit()]
        if v:
            out += ["", f"- {label}: mean **{statistics.mean(v):.2f}** / 5 (n = {len(v)})"]

    out += ["", "## SUS per participant", "", "| Participant | SUS |", "| --- | --- |"]
    out += [f"| {p} | {s:.1f} |" for p, s in scores]
    for col, title in [("comment_useful", "Most useful"), ("comment_confusing", "Confusing or missing")]:
        c = [r[col].strip() for r in rows if r.get(col, "").strip()]
        if c:
            out += ["", f"## {title}", ""] + [f"- {x}" for x in c]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"SUS {mean:.1f} ({grade(mean)}), n={n}. Report: reports/user_study.md")


if __name__ == "__main__":
    main()
