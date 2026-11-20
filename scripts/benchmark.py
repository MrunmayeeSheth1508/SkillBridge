"""
SkillBridge - performance benchmark of the in-database engine.

    python scripts/benchmark.py            (about 1-3 minutes)

Measures, with warm caches and the median of repeated runs:
  1. Query latency of every core operation (gap analysis, readiness,
     roadmap, extraction, provenance lookup)
  2. Index effect: the same evidence lookup with and without indexes
     (EXPLAIN ANALYZE, planner switches)
  3. RQ3 - cost of the cycle-checking trigger as the prerequisite graph grows
Everything that writes runs inside transactions that are rolled back.
Writes reports/performance.md
"""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402

REPORT = ls.PROJECT_ROOT / "reports" / "performance.md"
REPEATS = 7
AD = ("We are hiring a data scientist. You will analyse data with Python and SQL, build machine learning "
      "models using scikit-learn and PyTorch, and communicate results with Tableau. Strong mathematics, "
      "statistics and critical thinking are required. Experience with Apache Spark and Git is a plus.")


def timed(cur, sql: str, params=(), repeats: int = REPEATS) -> tuple[float, float, int]:
    """Median and p95-ish (max) latency in ms, plus row count."""
    cur.execute(sql, params)          # warm-up
    rows = len(cur.fetchall()) if cur.description else 0
    times = []
    for _ in range(repeats):
        t = time.perf_counter()
        cur.execute(sql, params)
        if cur.description:
            cur.fetchall()
        times.append((time.perf_counter() - t) * 1000)
    return statistics.median(times), max(times), rows


def main() -> None:
    url = ls.get_database_url()
    out = ["# SkillBridge performance benchmark", ""]
    with psycopg.connect(url) as conn:
        cur = conn.cursor()
        cur.execute("SET search_path = core, staging, public")
        cur.execute("SELECT version()")
        out += [f"- {cur.fetchone()[0].split(',')[0]}", f"- Median of {REPEATS} warm runs per query", ""]
        cur.execute("""SELECT (SELECT COUNT(*) FROM careers), (SELECT COUNT(*) FROM skills),
                              (SELECT COUNT(*) FROM career_skill_evidence), (SELECT COUNT(*) FROM skill_similarity),
                              (SELECT COUNT(*) FROM mv_skill_lexicon)""")
        c, k, e, s, lx = cur.fetchone()
        out += [f"Data size: {c:,} careers · {k:,} skills · {e:,} evidence rows · {s:,} skill relations · "
                f"{lx:,} lexicon labels", ""]

        cur.execute("SELECT user_id FROM users WHERE email = 'demo@skillbridge.local'")
        uid = cur.fetchone()[0]
        cur.execute("SELECT career_id, title FROM careers WHERE title = 'Data Scientists' AND is_target "
                    "UNION ALL (SELECT career_id, title FROM careers WHERE is_target ORDER BY career_id) LIMIT 1")
        cid, title = cur.fetchone()

        # ---------------------------------------------------------- 1. latency
        print("1/3  Query latency ...")
        ops = [
            ("Provenance lookup (v_evidence_detail, one career)",
             "SELECT * FROM v_evidence_detail WHERE career_id = %s", (cid,)),
            ("Aggregated requirements (v_career_skill_requirement)",
             "SELECT * FROM v_career_skill_requirement WHERE career_id = %s", (cid,)),
            ("Gap analysis, baseline (fn_gap_analysis, no transfer)",
             "SELECT * FROM fn_gap_analysis(%s, %s, false)", (uid, cid)),
            ("Gap analysis with directional transfer",
             "SELECT * FROM fn_gap_analysis(%s, %s, true)", (uid, cid)),
            ("Readiness for all target careers (fn_readiness x targets)",
             "SELECT career_id, fn_readiness(%s, career_id, true) FROM careers WHERE is_target", (uid,)),
            ("Skill extraction from a job ad (fn_extract_from_text, exact)",
             "SELECT * FROM fn_extract_from_text(%s, false)", (AD,)),
            ("Skill extraction from a job ad (exact + fuzzy)",
             "SELECT * FROM fn_extract_from_text(%s, true)", (AD,)),
        ]
        out += [f"## 1. Latency of core operations ({title})", "",
                "| Operation | Median (ms) | Max (ms) | Rows |", "| --- | --- | --- | --- |"]
        for name, sql, params in ops:
            med, mx, n = timed(cur, sql, params)
            out.append(f"| {name} | {med:.1f} | {mx:.1f} | {n} |")

        meds = []
        for _ in range(3):
            t = time.perf_counter()
            cur.execute("SELECT fn_build_roadmap(%s, %s, 8, true)", (uid, cid))
            meds.append((time.perf_counter() - t) * 1000)
            conn.rollback()
            cur.execute("SET search_path = core, staging, public")
        out.append(f"| Roadmap generation incl. snapshot + storage (fn_build_roadmap) | "
                   f"{statistics.median(meds):.1f} | {max(meds):.1f} | 1 |")
        out.append("")

        # ---------------------------------------------------------- 2. index effect
        print("2/3  Index effect ...")
        cur.execute("SELECT skill_id FROM skills WHERE taxonomy = 'onet_skill' ORDER BY skill_id LIMIT 1")
        sid = cur.fetchone()[0]
        q = "SELECT * FROM career_skill_evidence WHERE skill_id = %s"

        def plan_ms() -> tuple[float, str]:
            cur.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + q, (sid,))
            plan = cur.fetchone()[0][0]
            return plan["Execution Time"], plan["Plan"]["Node Type"]

        with_idx = [plan_ms() for _ in range(REPEATS)]
        cur.execute("SET enable_indexscan = off; SET enable_bitmapscan = off; SET enable_indexonlyscan = off")
        no_idx = [plan_ms() for _ in range(REPEATS)]
        cur.execute("RESET enable_indexscan; RESET enable_bitmapscan; RESET enable_indexonlyscan")
        mi, ni = statistics.median(t for t, _ in with_idx), statistics.median(t for t, _ in no_idx)
        out += ["## 2. Index effect: all evidence for one skill", "",
                "`SELECT * FROM career_skill_evidence WHERE skill_id = ?` measured with EXPLAIN ANALYZE.", "",
                "| Plan | Node | Median execution (ms) |", "| --- | --- | --- |",
                f"| With index on skill_id | {with_idx[0][1]} | {mi:.2f} |",
                f"| Indexes disabled | {no_idx[0][1]} | {ni:.2f} |",
                "", f"Speed-up from the index: **{ni / mi:.0f}x**." if mi > 0 else "", ""]

        # ---------------------------------------------------------- 3. RQ3 trigger cost
        print("3/3  Cycle-check trigger vs graph size ...")
        out += ["## 3. RQ3: cost of the cycle-checking trigger as the graph grows", "",
                "A chain of prerequisite edges is inserted one at a time (each insert runs the advisory lock "
                "and the recursive reachability check). Rolled back afterwards.", "",
                "| Edges already in graph | Median insert latency (ms) | Cycle attempt rejected in (ms) |",
                "| --- | --- | --- |"]
        cur.execute("SELECT skill_id FROM skills ORDER BY skill_id LIMIT 2001")
        ids = [r[0] for r in cur.fetchall()]
        checkpoints = [c for c in (10, 100, 250, 500, 1000, 2000) if c < len(ids)]
        cur.execute("DELETE FROM skill_prerequisites")           # isolated graph (rolled back)
        inserted, lat = 0, []
        for i in range(1, len(ids)):
            t = time.perf_counter()
            cur.execute("INSERT INTO skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)",
                        (ids[i], ids[i - 1]))      # chain: id0 -> id1 -> id2 ...
            lat.append((time.perf_counter() - t) * 1000)
            inserted += 1
            if inserted in checkpoints:
                cur.execute("SAVEPOINT c")
                t = time.perf_counter()
                try:   # closing the loop must be rejected: whole chain is traversed
                    cur.execute("INSERT INTO skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)",
                                (ids[0], ids[inserted]))
                    rej = "NOT REJECTED"
                except psycopg.Error:
                    rej = f"{(time.perf_counter() - t) * 1000:.1f}"
                cur.execute("ROLLBACK TO SAVEPOINT c")
                window = lat[-min(25, len(lat)):]
                out.append(f"| {inserted:,} | {statistics.median(window):.2f} | {rej} |")
            if inserted >= checkpoints[-1]:
                break
        conn.rollback()
        out += ["", "The worst case is a long chain, because the check must walk the whole path. "
                "Curated prerequisite graphs are shallow (a few layers), so real inserts stay near the first row.",
                ""]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"Done. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()