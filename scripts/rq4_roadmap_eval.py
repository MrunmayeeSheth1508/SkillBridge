"""
SkillBridge - RQ4: how close is the in-database greedy resource selection to the optimum?

    python -m pip install pulp highspy          (once)
    python scripts/rq4_roadmap_eval.py

Resource selection is weighted SET COVER: choose learning resources so that every
needed skill is covered and total hours are minimal. It is NP-hard; SkillBridge
uses the greedy rule inside PostgreSQL (core.fn_assign_resources): repeatedly take the
resource with the lowest hours per newly covered skill. Guarantee: cost <= H(k) * optimum,
where H(k) = 1 + 1/2 + ... + 1/k and k = the most skills one resource covers.

This script compares greedy with the exact optimum (integer linear program) on
  A. curated instances - your learning_resources.csv, for every target career and demo learner
  B. synthetic instances - random set-cover problems of growing size (always available)
and checks that the SQL implementation picks exactly what the reference greedy picks.
Writes reports/rq4_roadmap.md
"""

from __future__ import annotations

import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402

try:
    import pulp
except ImportError:
    sys.exit("This experiment needs PuLP:  python -m pip install pulp highspy")

REPORT = ls.PROJECT_ROOT / "reports" / "rq4_roadmap.md"


def solver():
    available = pulp.listSolvers(onlyAvailable=True)
    if "HiGHS" in available:
        return pulp.HiGHS(msg=False, timeLimit=60)
    if "PULP_CBC_CMD" in available:
        return pulp.PULP_CBC_CMD(msg=False, timeLimit=60)
    sys.exit(f"No ILP solver available (found {available}). Run: python -m pip install highspy")


# ------------------------------------------------------------------ algorithms
def greedy(needed: set, resources: dict) -> tuple[list, float]:
    """resources: id -> (hours, set_of_skills). Same rule and tie-breaks as core.fn_assign_resources."""
    uncovered, chosen, cost = set(needed), [], 0.0
    while uncovered:
        best = None
        for rid, (hours, skills) in resources.items():
            new = len(skills & uncovered)
            if new:
                key = (hours / new, -new, rid)
                if best is None or key < best[0]:
                    best = (key, rid)
        if best is None:
            break
        rid = best[1]
        chosen.append(rid)
        cost += resources[rid][0]
        uncovered -= resources[rid][1]
    return chosen, cost


def optimal(needed: set, resources: dict, slv) -> tuple[list, float, str]:
    coverable = {s for s in needed if any(s in sk for _, sk in resources.values())}
    prob = pulp.LpProblem("set_cover", pulp.LpMinimize)
    x = {rid: binary_var(prob, f"x_{i}") for i, rid in enumerate(resources)}
    prob += pulp.lpSum(h * x[rid] for rid, (h, _) in resources.items())
    for s in coverable:
        prob += pulp.lpSum(x[rid] for rid, (_, sk) in resources.items() if s in sk) >= 1
    status = prob.solve(slv)                     # PuLP returns the status code
    chosen = [rid for rid in resources if (x[rid].value() or 0) > 0.5]
    return chosen, sum(resources[r][0] for r in chosen), str(status)


def binary_var(prob, name: str):
    """PuLP >= 4 creates variables through the problem; older PuLP through LpVariable."""
    if hasattr(prob, "add_variable"):
        return prob.add_variable(name, cat="Binary")
    return pulp.LpVariable(name, cat="Binary")


def harmonic(k: int) -> float:
    return sum(1 / i for i in range(1, k + 1))


def summarise(rows: list[tuple[float, float]]) -> tuple[float, float, int]:
    ratios = [g / o for g, o in rows if o > 0]
    return (statistics.mean(ratios) if ratios else float("nan"),
            max(ratios) if ratios else float("nan"),
            sum(1 for r in ratios if r < 1 + 1e-9))


# ------------------------------------------------------------------ main
def main() -> None:
    slv = solver()
    out = ["# RQ4 - Greedy resource selection vs the exact optimum (weighted set cover)", "",
           f"- Solver for the optimum: {type(slv).__name__} (integer linear program)",
           "- Greedy rule = core.fn_assign_resources: lowest hours per newly covered skill", ""]
    t0 = time.time()

    # ---------------------------------------------------------- A. curated instances
    with psycopg.connect(ls.get_database_url()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM core.learning_resources")
        n_res = cur.fetchone()[0]
        out += ["## A. Curated instances (data/curated/learning_resources.csv)", ""]
        if n_res == 0:
            out += ["_No curated resources loaded yet - fill `data/curated/learning_resources.csv` "
                    "(see docs/learning_resources_guide.md), rebuild, and re-run._", ""]
        else:
            cur.execute("""SELECT r.resource_id, r.effort_hours, array_agg(rs.skill_id)
                           FROM core.learning_resources r JOIN core.resource_skills rs USING (resource_id)
                           GROUP BY r.resource_id, r.effort_hours""")
            all_res = {rid: (float(h), set(sk)) for rid, h, sk in cur.fetchall()}
            cur.execute("SELECT user_id, full_name FROM core.users WHERE role = 'learner' ORDER BY user_id")
            learners = cur.fetchall()
            cur.execute("SELECT career_id, title FROM core.careers WHERE is_target ORDER BY title")
            careers = cur.fetchall()
            rows, table, sql_match, sql_checked = [], [], 0, 0
            for uid, uname in learners:
                for cid, title in careers:
                    cur.execute("""SELECT skill_id FROM core.fn_gap_analysis(%s, %s, true)
                                   WHERE gap >= core.param('roadmap_min_gap')""", (uid, cid))
                    needed = {r[0] for r in cur.fetchall()}
                    res = {rid: v for rid, v in all_res.items() if v[1] & needed}
                    coverable = {s for s in needed if any(s in v[1] for v in res.values())}
                    if not coverable:
                        continue
                    g_set, g_cost = greedy(coverable, res)
                    o_set, o_cost, status = optimal(coverable, res, slv)
                    rows.append((g_cost, o_cost))
                    table.append((uname, title, len(coverable), len(res), len(g_set), f"{g_cost:.1f}",
                                  len(o_set), f"{o_cost:.1f}", f"{g_cost / o_cost:.3f}" if o_cost else "-"))

                    # consistency: the SQL greedy on a real roadmap picks what the reference greedy picks
                    cur.execute("SELECT core.fn_build_roadmap(%s, %s, 8, true)", (uid, cid))
                    rid_map = cur.fetchone()[0]
                    cur.execute("SELECT skill_id, resource_id FROM core.roadmap_items WHERE roadmap_id = %s", (rid_map,))
                    items = cur.fetchall()
                    item_skills = {s for s, _ in items}
                    sql_set = {r for _, r in items if r is not None}
                    ref_res = {k: v for k, v in all_res.items() if v[1] & item_skills}
                    ref_cov = {s for s in item_skills if any(s in v[1] for v in ref_res.values())}
                    ref_set, _ = greedy(ref_cov, ref_res)
                    sql_checked += 1
                    sql_match += int(set(ref_set) == sql_set)
            conn.rollback()                                   # roadmaps built for the check are discarded
            if rows:
                mean_r, max_r, n_opt = summarise(rows)
                out += [f"{len(rows)} learner x career instances, {n_res} curated resources.", "",
                        "| Learner | Career | Skills to cover | Candidate resources | Greedy picks | Greedy hours "
                        "| Optimal picks | Optimal hours | Ratio |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
                out += ["| " + " | ".join(str(v) for v in t) + " |" for t in table[:60]]
                out += ["", f"- Mean greedy/optimal hours ratio: **{mean_r:.3f}**, worst: **{max_r:.3f}**; "
                        f"greedy optimal in {n_opt}/{len(rows)} instances",
                        f"- SQL implementation matches the reference greedy on {sql_match}/{sql_checked} roadmaps", ""]
            else:
                out += ["_Curated resources do not cover any current gap of the learners - add resources for "
                        "the target careers' skills._", ""]

    # ---------------------------------------------------------- B. synthetic instances
    out += ["## B. Synthetic set-cover instances", "",
            "Random instances: n skills, 3n resources, each covering 1-5 skills, hours ~ lognormal and "
            "growing with the number of skills covered; every skill is coverable. 30 instances per size, seed 7.", "",
            "| Skills (n) | Resources | Mean ratio | Worst ratio | Greedy optimal | Bound H(5) | Greedy ms | ILP ms |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    rng = random.Random(7)
    for n in (10, 20, 40, 80, 160):
        rows, gt, ot = [], [], []
        for _ in range(30):
            skills = list(range(n))
            res = {}
            for r in range(3 * n):
                k = rng.randint(1, 5)
                cov = set(rng.sample(skills, min(k, n)))
                res[r] = (round(rng.lognormvariate(2.3, 0.5) * (0.6 + 0.4 * len(cov)), 1), cov)
            for s in skills:                                   # guarantee coverability
                if not any(s in c for _, c in res.values()):
                    res[len(res)] = (round(rng.lognormvariate(2.3, 0.5), 1), {s})
            t = time.perf_counter(); _, g = greedy(set(skills), res); gt.append((time.perf_counter() - t) * 1000)
            t = time.perf_counter(); _, o, _ = optimal(set(skills), res, slv); ot.append((time.perf_counter() - t) * 1000)
            rows.append((g, o))
        mean_r, max_r, n_opt = summarise(rows)
        out.append(f"| {n} | {3 * n} | {mean_r:.3f} | {max_r:.3f} | {n_opt}/30 | {harmonic(5):.2f} | "
                   f"{statistics.median(gt):.2f} | {statistics.median(ot):.1f} |")
    out += ["", "## Reading the result", "",
            "- The ratio is greedy hours / optimal hours (1.000 = optimal). The theoretical worst case is H(5) = 2.28 "
            "when a resource covers at most 5 skills; observed ratios are far below it.",
            "- Greedy runs in milliseconds inside the database for every roadmap request; the exact ILP needs an "
            "external solver and grows quickly with instance size, which is why the greedy rule is used online.", "",
            f"Runtime {time.time() - t0:.0f} s"]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"Done. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
