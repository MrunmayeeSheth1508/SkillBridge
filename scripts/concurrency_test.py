"""
SkillBridge - RQ3 concurrency experiment: can two simultaneous transactions
create a prerequisite cycle together?

    python scripts/concurrency_test.py            # 40 trials per cell (~1-2 minutes)
    python scripts/concurrency_test.py --trials 100

Each trial starts two (or three) transactions at the same moment. Each inserts
one edge and waits before committing, so their cycle checks overlap in time.
Individually every edge is valid; together they close a loop.

  Scenario "direct"     : T1 adds a->b, T2 adds b->a
  Scenario "transitive" : a->b already committed; T1 adds b->c, T2 adds c->a

Three strategies are compared:
  1. trigger + advisory lock, READ COMMITTED   (SkillBridge's design)
  2. trigger WITHOUT the lock, READ COMMITTED  (= an application-level check)
  3. trigger WITHOUT the lock, SERIALIZABLE     (PostgreSQL's SSI)

Strategy 2 is created temporarily by redefining the trigger function; the
original is ALWAYS restored afterwards (try/finally).
Writes reports/concurrency.md
"""

from __future__ import annotations

import argparse
import re
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402

REPORT = ls.PROJECT_ROOT / "reports" / "concurrency.md"
HOLD = 0.15          # seconds each transaction waits before COMMIT (widens the race window)


def make_skills(url: str, n: int) -> list[int]:
    with psycopg.connect(url) as c:
        c.execute("DELETE FROM core.skills WHERE external_id LIKE 'race://%'")
        rows = c.execute("""INSERT INTO core.skills (name, taxonomy, skill_type, external_id)
                            SELECT 'race test ' || g, 'esco', 'skill', 'race://' || g
                            FROM generate_series(1, %s) g RETURNING skill_id""", (n,)).fetchall()
        c.commit()
    return [r[0] for r in rows]


def drop_skills(url: str) -> None:
    with psycopg.connect(url) as c:
        c.execute("DELETE FROM core.skills WHERE external_id LIKE 'race://%'")   # cascades to edges
        c.commit()


def worker(url, isolation, edge, barrier, results, key):
    """Insert one edge (skill, prereq) in its own transaction; record the outcome."""
    skill, prereq = edge
    try:
        with psycopg.connect(url) as conn:
            if isolation == "serializable":
                conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE
            barrier.wait()
            try:
                conn.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)",
                             (skill, prereq))
                time.sleep(HOLD)
                conn.commit()
                results[key] = "committed"
            except psycopg.errors.SerializationFailure:
                conn.rollback()
                results[key] = "serialization_failure"
            except psycopg.errors.CheckViolation:
                conn.rollback()
                results[key] = "rejected_cycle"
    except Exception as exc:                                    # pragma: no cover
        results[key] = f"error: {exc}"


def has_cycle(url: str, ids: list[int]) -> bool:
    """True if the committed edges among `ids` contain a cycle."""
    with psycopg.connect(url) as c:
        edges = c.execute("SELECT prereq_skill_id, skill_id FROM core.skill_prerequisites "
                          "WHERE skill_id = ANY(%s) AND prereq_skill_id = ANY(%s)", (ids, ids)).fetchall()
    graph: dict[int, list[int]] = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
    state: dict[int, int] = {}

    def dfs(v: int) -> bool:
        state[v] = 1
        for w in graph.get(v, []):
            if state.get(w) == 1 or (state.get(w) is None and dfs(w)):
                return True
        state[v] = 2
        return False

    return any(state.get(v) is None and dfs(v) for v in list(graph))


def run_cell(url: str, isolation: str, scenario: str, trials: int, skills: list[int]) -> dict:
    stats = {"trials": trials, "cycles": 0, "committed": 0, "rejected_cycle": 0,
             "serialization_failure": 0, "errors": 0}
    for t in range(trials):
        a, b, c = skills[3 * t: 3 * t + 3]
        with psycopg.connect(url) as conn:                       # clean slate for this triple
            conn.execute("DELETE FROM core.skill_prerequisites WHERE skill_id = ANY(%s) OR prereq_skill_id = ANY(%s)",
                         ([a, b, c], [a, b, c]))
            if scenario == "transitive":
                conn.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)", (b, a))
            conn.commit()
        edges = [(b, a), (a, b)] if scenario == "direct" else [(c, b), (a, c)]
        barrier = threading.Barrier(len(edges))
        results: dict[int, str] = {}
        threads = [threading.Thread(target=worker, args=(url, isolation, e, barrier, results, i))
                   for i, e in enumerate(edges)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        for r in results.values():
            if r in stats:
                stats[r] += 1
            else:
                stats["errors"] += 1
        if has_cycle(url, [a, b, c]):
            stats["cycles"] += 1
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=40)
    args = ap.parse_args()
    url = ls.get_database_url()

    with psycopg.connect(url) as c:
        original = c.execute("SELECT pg_get_functiondef('core.trg_prerequisite_no_cycle()'::regprocedure)").fetchone()[0]
        version = c.execute("SELECT version()").fetchone()[0].split(",")[0]
    unlocked = re.sub(r"^\s*PERFORM pg_advisory_xact_lock\(.*?\);\s*$", "", original, flags=re.M)
    if unlocked == original:
        sys.exit("The trigger function has no advisory lock (a previous run may have been interrupted).\n"
                 "Run  python scripts/build_database.py data/raw  first, then re-run this test.")

    cells = []
    skills = make_skills(url, 3 * args.trials)
    try:
        for label, fn_def, iso in (
            ("Trigger + advisory lock (SkillBridge)", original, "read_committed"),
            ("Trigger without lock (= application-level check)", unlocked, "read_committed"),
            ("Trigger without lock, SERIALIZABLE isolation", unlocked, "serializable"),
        ):
            with psycopg.connect(url) as c:
                c.execute(fn_def)
                c.commit()
            for scenario in ("direct", "transitive"):
                print(f"  {label:<52} {scenario:<10} ...", end=" ", flush=True)
                t0 = time.time()
                s = run_cell(url, iso, scenario, args.trials, skills)
                s.update(strategy=label, scenario=scenario, seconds=time.time() - t0)
                cells.append(s)
                print(f"cycles accepted: {s['cycles']}/{s['trials']}")
    finally:
        try:                                                     # ALWAYS restore the real trigger
            with psycopg.connect(url) as c:
                c.execute(original)
                c.commit()
            drop_skills(url)
        except psycopg.Error as exc:
            print("\n!!! Could not restore the cycle-check trigger:", exc)
            print("!!! Run  python scripts/build_database.py data/raw  before using the database again.")
            raise

    out = ["# RQ3 - Concurrency: can simultaneous transactions create a prerequisite cycle?", "",
           f"- {version}; {args.trials} trials per cell; each transaction holds {HOLD * 1000:.0f} ms before COMMIT",
           "- *direct*: T1 adds a->b while T2 adds b->a. *transitive*: a->b exists; T1 adds b->c while T2 adds c->a.",
           "- Every edge is valid on its own; only the combination is a cycle.", "",
           "| Strategy | Scenario | Trials | **Cycles accepted** | Rejected by trigger | Serialization failures | Committed txns |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in cells:
        out.append(f"| {s['strategy']} | {s['scenario']} | {s['trials']} | **{s['cycles']}** | "
                   f"{s['rejected_cycle']} | {s['serialization_failure']} | {s['committed']} |")
    out += ["", "## Reading the result", "",
            "- **Without the lock**, both cycle checks run before either transaction commits, so neither sees "
            "the other's edge: both pass and the committed graph contains a cycle. This is what an "
            "application-level check (validate in Python, then insert) would do.",
            "- **With the advisory lock**, the second transaction waits until the first commits; its check then "
            "sees the new edge and rejects the insert. No cycle is ever committed.",
            "- **SERIALIZABLE** also prevents the cycle, but by aborting a transaction with a serialization failure "
            "that the application must catch and retry; the advisory lock gives a clear, deterministic "
            "\"would create a cycle\" error instead and works at the default isolation level.", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"\nDone. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
