"""
SkillBridge - RQ2: does directional transfer credit make readiness more realistic?

    python scripts/rq2_transfer_eval.py                 # 20% held-out occupations, seed 42
    python scripts/rq2_transfer_eval.py --test-share 0.3 --seed 7

Ground truth: O*NET "Related Occupations" (put the file in data/raw; the file
name must contain "related"). Columns are detected from their contents.

Protocol (offline, no users needed)
  1. A random share of rated O*NET occupations is held out as pseudo-learners.
     Each learner's proficiency in a skill/knowledge element = its O*NET level (LV / 7).
  2. Transfer edges are re-fitted WITHOUT the held-out occupations (no leakage).
  3. For every learner, readiness is computed for every other rated occupation,
     using O*NET skills + knowledge only (no priors, no ESCO), with
        none        : P_eff = P_own
        directional : P_eff = max(P_own, lambda * max_a P(a) * T(a -> s))   lambda in 0.4..1.0
        symmetric   : same, with T replaced by (T(a->s) + T(s->a)) / 2      (H2b ablation)
  4. Occupations are ranked by readiness; O*NET's related occupations should rank high.
     Metrics: MRR, nDCG@10, Recall@10, Recall@20 (binary relevance),
     with a 95% bootstrap CI for the difference to "none".
Everything runs in a transaction that is rolled back.  Writes reports/rq2_transfer.md
"""

from __future__ import annotations

import argparse
import io
import math
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import pandas as pd  # noqa: E402
import psycopg  # noqa: E402

REPORT = ls.PROJECT_ROOT / "reports" / "rq2_transfer.md"
SOC = re.compile(r"^\d{2}-\d{4}\.\d{2}$")


# ------------------------------------------------------------------ ground truth
def load_related(raw_dir: Path) -> pd.DataFrame:
    files = [p for p in raw_dir.rglob("*") if p.is_file() and "related" in p.name.lower()
             and p.suffix.lower() in (".txt", ".csv", ".tsv", ".xlsx", ".xls")]
    if not files:
        sys.exit("O*NET Related Occupations file not found in data/raw (name must contain 'related').\n"
                 "Download it from https://www.onetcenter.org/database.html")
    path = files[0]
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path, dtype=str)
    else:
        raw = path.read_bytes()
        df = pd.read_csv(io.BytesIO(raw), dtype=str, sep=None, engine="python", encoding="utf-8-sig")
    soc_cols = [c for c in df.columns if df[c].dropna().astype(str).str.strip().str.match(SOC).mean() > 0.9]
    if len(soc_cols) < 2:
        sys.exit(f"Could not find two O*NET-SOC code columns in {path.name}: {list(df.columns)}")
    tier_col = next((c for c in df.columns if df[c].dropna().astype(str).str.contains(
        "Primary|Supplemental", case=False).mean() > 0.8), None)
    out = pd.DataFrame({"code": df[soc_cols[0]].str.strip(), "related": df[soc_cols[1]].str.strip()})
    out["tier"] = df[tier_col].str.strip() if tier_col else "all"
    print(f"Ground truth: {path.name} - {len(out):,} pairs; columns {soc_cols[0]!r} -> {soc_cols[1]!r}"
          + (f", tier {tier_col!r}" if tier_col else ""))
    return out[out["code"] != out["related"]]


# ------------------------------------------------------------------ metrics
def metrics(ranked: list[int], relevant: set[int]) -> dict:
    rr = next((1 / (i + 1) for i, c in enumerate(ranked) if c in relevant), 0.0)
    dcg = sum(1 / math.log2(i + 2) for i, c in enumerate(ranked[:10]) if c in relevant)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(10, len(relevant))))
    return {"MRR": rr, "nDCG@10": dcg / idcg if idcg else 0.0,
            "Recall@10": len(set(ranked[:10]) & relevant) / len(relevant),
            "Recall@20": len(set(ranked[:20]) & relevant) / len(relevant)}


def bootstrap_diff(a: list[float], b: list[float], n: int = 2000, seed: int = 1) -> tuple[float, float]:
    rng = random.Random(seed)
    d = [x - y for x, y in zip(a, b)]
    means = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


# ------------------------------------------------------------------ SQL (set-based readiness)
SETUP = """
CREATE TEMP TABLE rq_learners ON COMMIT DROP AS
  SELECT career_id AS o FROM core.careers WHERE career_id = ANY(%(test)s);
CREATE TEMP TABLE rq_prof_full ON COMMIT DROP AS     -- full profile = O*NET level of the occupation
  SELECT e.career_id AS o, e.skill_id AS s, COALESCE(e.level_norm, 0) AS p,
         row_number() OVER (PARTITION BY e.career_id ORDER BY e.level_norm DESC NULLS LAST,
                                                          e.importance DESC, e.skill_id) AS rn
  FROM core.career_skill_evidence e JOIN core.skills k USING (skill_id)
  WHERE e.career_id = ANY(%(test)s) AND e.requirement_type = 'scored'
    AND k.taxonomy IN ('onet_skill', 'onet_knowledge');
CREATE TEMP TABLE rq_req ON COMMIT DROP AS           -- requirements of every candidate occupation
  SELECT e.career_id AS c, e.skill_id AS s, e.importance AS i
  FROM core.career_skill_evidence e JOIN core.skills k USING (skill_id)
  JOIN core.careers c ON c.career_id = e.career_id AND c.has_ratings
  WHERE e.requirement_type = 'scored' AND k.taxonomy IN ('onet_skill', 'onet_knowledge')
    AND e.importance >= core.param('gap_min_importance');
CREATE TEMP TABLE rq_dir ON COMMIT DROP AS
  SELECT from_skill_id AS a, to_skill_id AS b, weight AS w
  FROM core.skill_similarity WHERE method = 'transfer_v0';
CREATE TEMP TABLE rq_sym ON COMMIT DROP AS           -- symmetric ablation: mean of both directions
  SELECT x.a, x.b, (COALESCE(f.w, 0) + COALESCE(r.w, 0)) / 2 AS w
  FROM (SELECT a, b FROM rq_dir UNION SELECT b, a FROM rq_dir) x
  LEFT JOIN rq_dir f ON f.a = x.a AND f.b = x.b
  LEFT JOIN rq_dir r ON r.a = x.b AND r.b = x.a;
CREATE INDEX ON rq_req (s); ANALYZE rq_req;
"""

READINESS = """
WITH skills AS (SELECT DISTINCT s FROM rq_req),
grid AS (SELECT l.o, k.s FROM rq_learners l CROSS JOIN skills k),
tr AS (
  SELECT p.o, e.b AS s, MAX(p.p * e.w) AS t
  FROM rq_prof p JOIN {edges} e ON e.a = p.s
  GROUP BY p.o, e.b),
eff AS (
  SELECT g.o, g.s, GREATEST(COALESCE(p.p, 0), %(lam)s * COALESCE(tr.t, 0)) AS pe
  FROM grid g LEFT JOIN rq_prof p ON p.o = g.o AND p.s = g.s
  LEFT JOIN tr ON tr.o = g.o AND tr.s = g.s)
SELECT e.o, r.c, 1 - SUM(r.i * (1 - e.pe)) / SUM(r.i) AS readiness
FROM rq_req r JOIN eff e ON e.s = r.s
WHERE r.c <> e.o
GROUP BY e.o, r.c
"""


def evaluate(cur, test, truth, truth_primary, k: int) -> tuple[list[str], dict]:
    """Rank every candidate for every learner under each method; return report lines + key numbers."""
    cur.execute("DROP TABLE IF EXISTS rq_prof")
    cur.execute("CREATE TEMP TABLE rq_prof ON COMMIT DROP AS SELECT o, s, p FROM rq_prof_full "
                "WHERE %(k)s = 0 OR rn <= %(k)s", {"k": k})
    cur.execute("CREATE INDEX ON rq_prof (o, s)")
    cur.execute("ANALYZE rq_prof")

    variants = [("none (exact skills only)", "rq_dir", 0.0)]
    variants += [(f"directional, lambda={lam}", "rq_dir", lam) for lam in (0.4, 0.6, 0.8, 1.0)]
    variants += [("symmetric, lambda=0.8 (H2b)", "rq_sym", 0.8)]
    per_variant, per_primary, all_scores = {}, {}, {}
    for name, edges, lam in variants:
        print(f"    {name} ...")
        cur.execute(READINESS.format(edges=edges), {"lam": lam})
        scores: dict[int, list[tuple[float, int]]] = defaultdict(list)
        by_pair: dict[int, dict[int, float]] = defaultdict(dict)
        for o, c, r in cur.fetchall():
            scores[o].append((float(r), c))
            by_pair[o][c] = float(r)
        all_scores[name] = by_pair
        m_all: dict[str, list[float]] = defaultdict(list)
        m_pri: dict[str, list[float]] = defaultdict(list)
        for o in test:
            ranked = [c for _, c in sorted(scores[o], key=lambda x: (-x[0], x[1]))]
            for key, v in metrics(ranked, truth[o]).items():
                m_all[key].append(v)
            if truth_primary[o]:
                for key, v in metrics(ranked, truth_primary[o]).items():
                    m_pri[key].append(v)
        per_variant[name], per_primary[name] = m_all, m_pri

    keys = ["MRR", "nDCG@10", "Recall@10", "Recall@20"]
    mean = lambda xs: sum(xs) / len(xs)  # noqa: E731
    base = per_variant[variants[0][0]]
    label = "full O*NET profile (all 68 skills + knowledge)" if k == 0 else f"partial profile: learner's {k} strongest skills only"
    out = [f"## Profile: {label}", "", "### Ranking of related occupations", "",
           "| Method | " + " | ".join(keys) + " |", "| --- |" + " --- |" * len(keys)]
    for name, *_ in variants:
        out.append(f"| {name} | " + " | ".join(f"{mean(per_variant[name][x]):.4f}" for x in keys) + " |")
    out += ["", "Difference to *none* (95% bootstrap CI over learners; * = CI excludes 0):", "",
            "| Method | Delta MRR [CI] | Delta nDCG@10 [CI] |", "| --- | --- | --- |"]
    for name, *_ in variants[1:]:
        cells = []
        for x in ("MRR", "nDCG@10"):
            lo, hi = bootstrap_diff(per_variant[name][x], base[x])
            d = mean(per_variant[name][x]) - mean(base[x])
            cells.append(f"{d:+.4f} [{lo:+.4f}, {hi:+.4f}]" + (" *" if lo > 0 or hi < 0 else ""))
        out.append(f"| {name} | " + " | ".join(cells) + " |")

    if any(per_primary[variants[0][0]].values()):
        out += ["", "Primary related occupations only:", "",
                "| Method | " + " | ".join(keys) + " |", "| --- |" + " --- |" * len(keys)]
        for name, *_ in variants:
            if per_primary[name].get("MRR"):
                out.append(f"| {name} | " + " | ".join(f"{mean(per_primary[name][x]):.4f}" for x in keys) + " |")

    # credit targeting
    base_scores = all_scores[variants[0][0]]
    out += ["", "### Credit targeting: do related occupations receive more of the transfer credit?", "",
            "| Method | Lift related (pts) | Lift unrelated (pts) | Raw difference [CI] "
            "| Gap closed, related - unrelated (pts) [CI] |", "| --- | --- | --- | --- | --- |"]
    for name, *_ in variants[1:]:
        rel_l, unr_l, diffs, ndiffs = [], [], [], []
        for o in test:
            rel_c = [c for c in truth[o] if c in base_scores[o]]
            unr_c = [c for c in base_scores[o] if c not in truth[o]]
            if not rel_c or not unr_c:
                continue

            def closed(c):
                b_, t_ = base_scores[o][c], all_scores[name][o][c]
                return (t_ - b_) / (1 - b_) if b_ < 1 else 0.0

            r_ = mean([all_scores[name][o][c] - base_scores[o][c] for c in rel_c])
            u_ = mean([all_scores[name][o][c] - base_scores[o][c] for c in unr_c])
            rel_l.append(r_); unr_l.append(u_); diffs.append(r_ - u_)
            ndiffs.append(mean([closed(c) for c in rel_c]) - mean([closed(c) for c in unr_c]))
        lo, hi = bootstrap_diff(diffs, [0.0] * len(diffs))
        nlo, nhi = bootstrap_diff(ndiffs, [0.0] * len(ndiffs))
        out.append(f"| {name} | {100 * mean(rel_l):.2f} | {100 * mean(unr_l):.2f} | "
                   f"{100 * mean(diffs):+.2f} [{100 * lo:+.2f}, {100 * hi:+.2f}]" + (" *" if lo > 0 or hi < 0 else "")
                   + f" | {100 * mean(ndiffs):+.2f} [{100 * nlo:+.2f}, {100 * nhi:+.2f}]"
                   + (" *" if nlo > 0 or nhi < 0 else "") + " |")
    out.append("")

    d8, sym = per_variant["directional, lambda=0.8"], per_variant["symmetric, lambda=0.8 (H2b)"]
    lo, hi = bootstrap_diff(d8["MRR"], sym["MRR"])
    blo, bhi = bootstrap_diff(d8["MRR"], base["MRR"])
    key_numbers = {"k": k, "mrr_none": mean(base["MRR"]), "mrr_dir": mean(d8["MRR"]), "mrr_sym": mean(sym["MRR"]),
                   "dir_vs_none": (mean(d8["MRR"]) - mean(base["MRR"]), blo, bhi),
                   "dir_vs_sym": (mean(d8["MRR"]) - mean(sym["MRR"]), lo, hi)}
    return out, key_numbers


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-share", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--raw", default=str(ls.PROJECT_ROOT / "data" / "raw"))
    ap.add_argument("--profiles", default="0,10",
                    help="profile sizes: 0 = full O*NET profile, k = only the learner's k strongest skills")
    args = ap.parse_args()
    profiles = [int(x) for x in args.profiles.split(",")]
    t0 = time.time()
    rel = load_related(Path(args.raw))

    with psycopg.connect(ls.get_database_url()) as conn:
        cur = conn.cursor()
        cur.execute("""SELECT career_id, origin_code FROM core.careers c
                       JOIN core.data_sources d ON d.source_id = c.origin_source_id AND d.source_name = 'O*NET'
                       WHERE c.has_ratings ORDER BY origin_code""")
        code_to_id = {code: cid for cid, code in cur.fetchall()}
        truth: dict[int, set[int]] = defaultdict(set)
        truth_primary: dict[int, set[int]] = defaultdict(set)
        for code, related, tier in rel.itertuples(index=False, name=None):
            if code in code_to_id and related in code_to_id:
                truth[code_to_id[code]].add(code_to_id[related])
                if "primary" in str(tier).lower() or tier == "all":
                    truth_primary[code_to_id[code]].add(code_to_id[related])
        eligible = sorted(o for o in truth if truth[o])
        rng = random.Random(args.seed)
        test = sorted(rng.sample(eligible, max(1, int(len(eligible) * args.test_share))))
        print(f"{len(code_to_id)} rated occupations, {len(eligible)} with related occupations; "
              f"{len(test)} held out as pseudo-learners")

        print("Re-fitting transfer edges without the held-out occupations ...")
        cur.execute("SELECT core.fn_build_transfer_edges(%s)", (test,))
        n_edges = cur.fetchone()[0]
        for stmt in (x.strip() for x in SETUP.split(";")):
            if stmt:
                cur.execute(stmt, {"test": test} if "%(test)s" in stmt else None)

        sections, summary = [], []
        for k in profiles:
            print(f"  profile size {'full' if k == 0 else k}:")
            lines, nums = evaluate(cur, test, truth, truth_primary, k)
            sections += lines
            summary.append(nums)
        conn.rollback()                                   # restore the original edges

    out = ["# RQ2 - Does directional transfer credit make readiness more realistic?", "",
           f"- Ground truth: O*NET Related Occupations; {len(test)} held-out occupations as pseudo-learners "
           f"(seed {args.seed}, {int(args.test_share * 100)}% of {len(eligible)}); "
           f"candidates: all {len(code_to_id)} rated occupations",
           f"- Transfer edges re-fitted without the held-out occupations: {n_edges:,} edges",
           "- Readiness uses O*NET skills + knowledge only (no priors, no ESCO); learner proficiency = O*NET level",
           "- Full profiles leave little for transfer to infer; partial profiles (a learner lists only their "
           "strongest skills) are the realistic case transfer credit is designed for.",
           f"- Runtime {time.time() - t0:.0f} s", "",
           "## Summary (lambda = 0.8)", "",
           "| Profile | MRR none | MRR directional | MRR symmetric | Directional - none [CI] | Directional - symmetric [CI] |",
           "| --- | --- | --- | --- | --- | --- |"]
    for n in summary:
        dn, sy = n["dir_vs_none"], n["dir_vs_sym"]
        star = lambda lo, hi: " *" if lo > 0 or hi < 0 else ""  # noqa: E731
        out.append(f"| {'full' if n['k'] == 0 else 'top ' + str(n['k'])} | {n['mrr_none']:.4f} | {n['mrr_dir']:.4f} | "
                   f"{n['mrr_sym']:.4f} | {dn[0]:+.4f} [{dn[1]:+.4f}, {dn[2]:+.4f}]{star(dn[1], dn[2])} | "
                   f"{sy[0]:+.4f} [{sy[1]:+.4f}, {sy[2]:+.4f}]{star(sy[1], sy[2])} |")
    out += ["", "\\* = 95% bootstrap CI excludes 0.", ""] + sections
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"\nDone in {time.time() - t0:.0f} s. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
