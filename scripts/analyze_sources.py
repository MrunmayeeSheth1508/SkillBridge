"""
SkillBridge - RQ1 analysis: how much do O*NET and ESCO agree, and does
keeping both change what learners are told?

    python scripts/analyze_sources.py

Uses comparable evidence tiers (core.v_evidence_tier) instead of raw
importance differences, because the sources use different scales.
Reported for the target careers:
  1. Coverage   - skills required by O*NET only, ESCO only, or both
  2. Agreement  - tier contingency table + Cohen's kappa on shared skills
  3. Impact     - requirement set and demo-learner readiness with O*NET alone
                  vs evidence-aware aggregation (O*NET + ESCO)
  4. Examples   - strongest disagreements
Writes reports/source_agreement.md
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402

REPORT = ls.PROJECT_ROOT / "reports" / "source_agreement.md"
TIER = {1: "peripheral", 2: "supporting", 3: "core"}


def cohen_kappa(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


COVERAGE_SQL = """
    WITH t AS (
      SELECT e.career_id, e.skill_id,
             bool_or(e.source = 'O*NET') AS onet, bool_or(e.source = 'ESCO') AS esco
      FROM careers c
      JOIN v_evidence_tier e ON e.career_id = c.career_id
      JOIN skills k ON k.skill_id = e.skill_id AND k.skill_type <> 'work_activity'
      WHERE c.is_target AND e.source IN ('O*NET', 'ESCO')
      GROUP BY e.career_id, e.skill_id)
    SELECT COUNT(*) FILTER (WHERE onet AND NOT esco), COUNT(*) FILTER (WHERE esco AND NOT onet),
           COUNT(*) FILTER (WHERE onet AND esco) FROM t"""

PAIRS_SQL = """
    SELECT o.tier, s.tier
    FROM v_evidence_tier o
    JOIN v_evidence_tier s ON s.career_id = o.career_id AND s.skill_id = o.skill_id AND s.source = 'ESCO'
    JOIN careers c ON c.career_id = o.career_id AND c.is_target
    JOIN skills k ON k.skill_id = o.skill_id AND k.skill_type <> 'work_activity'
    WHERE o.source = 'O*NET'"""

IMPACT_SQL = """
    WITH g AS (
      SELECT c.career_id, c.title, x.*
      FROM careers c CROSS JOIN LATERAL fn_gap_analysis(%s, c.career_id, true) x
      WHERE c.is_target),
    onet AS (
      SELECT g.career_id, g.skill_id, e.importance AS i_onet, g.effective_proficiency AS p
      FROM g JOIN career_skill_evidence e ON e.career_id = g.career_id AND e.skill_id = g.skill_id
      JOIN data_sources d ON d.source_id = e.source_id AND d.source_name = 'O*NET')
    SELECT g.title,
           COUNT(*)                                             AS req_aggregated,
           COUNT(onet.skill_id)                                 AS req_with_onet,
           COUNT(*) FILTER (WHERE g.sources = ARRAY['ESCO'])    AS added_by_esco_only,
           ROUND(1 - SUM(onet.i_onet * (1 - onet.p)) / NULLIF(SUM(onet.i_onet), 0), 3) AS readiness_onet_only,
           ROUND(1 - SUM(g.gap) / NULLIF(SUM(g.importance), 0), 3)                     AS readiness_aggregated
    FROM g LEFT JOIN onet ON onet.career_id = g.career_id AND onet.skill_id = g.skill_id
    GROUP BY g.title ORDER BY g.title"""


def md_table(header: list[str], rows: list) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join("" if v is None else str(v) for v in r) + " |" for r in rows]
    return out + [""]


def main() -> None:
    with psycopg.connect(ls.get_database_url()) as conn:
        cur = conn.cursor()
        cur.execute("SET search_path = core, staging, public")
        cur.execute("SELECT COUNT(*) FROM career_source_codes WHERE match_type LIKE 'crosswalk%'")
        if cur.fetchone()[0] == 0:
            sys.exit("No crosswalk loaded - put the ESCO-O*NET crosswalk in data/raw and rebuild.")
        out = ["# RQ1 - Evidence-aware requirements: O*NET vs ESCO", "",
               "Target careers only. Work activities excluded. ESCO evidence reaches O*NET careers through "
               "the official crosswalk (default: exact + close matches; section 4 compares with broad/narrow).", "",
               "Tiers make the sources comparable: **core** = O*NET importance >= 3.5/5, ESCO *essential*, "
               "or an O*NET In-Demand tool; **supporting** = O*NET 2.5-3.5, ESCO *optional*, other tools; "
               "**peripheral** = O*NET < 2.5.", ""]

        # ------------------------------------------------ 1. coverage
        cur.execute("""
            WITH t AS (
              SELECT c.career_id, c.title, c.domain, e.skill_id,
                     bool_or(e.source = 'O*NET') AS onet, bool_or(e.source = 'ESCO') AS esco
              FROM careers c
              JOIN v_evidence_tier e ON e.career_id = c.career_id
              JOIN skills k ON k.skill_id = e.skill_id AND k.skill_type <> 'work_activity'
              WHERE c.is_target AND e.source IN ('O*NET', 'ESCO')
              GROUP BY c.career_id, c.title, c.domain, e.skill_id)
            SELECT domain, title,
                   COUNT(*) FILTER (WHERE onet AND NOT esco) AS onet_only,
                   COUNT(*) FILTER (WHERE esco AND NOT onet) AS esco_only,
                   COUNT(*) FILTER (WHERE onet AND esco)     AS both
            FROM t GROUP BY domain, title ORDER BY domain, title""")
        cov = cur.fetchall()
        tot = [sum(r[i] for r in cov) for i in (2, 3, 4)]
        all_skills = sum(tot)
        out += ["## 1. Coverage: who requires what", ""]
        out += md_table(["Domain", "Career", "O*NET only", "ESCO only", "Both"], cov)
        out += [f"Across {len(cov)} target careers: **{tot[0]:,}** career-skill requirements come from O*NET only, "
                f"**{tot[1]:,}** from ESCO only and **{tot[2]:,}** from both "
                f"({100 * tot[2] / max(all_skills, 1):.1f}% overlap). Each source alone would miss the other's "
                "requirements; most of the non-overlap is vocabulary (O*NET's 35 broad skills and named tools vs "
                "ESCO's fine-grained skills).", ""]

        # ------------------------------------------------ 2. agreement on shared skills
        cur.execute("""
            SELECT o.tier, s.tier, k.skill_type
            FROM v_evidence_tier o
            JOIN v_evidence_tier s ON s.career_id = o.career_id AND s.skill_id = o.skill_id AND s.source = 'ESCO'
            JOIN careers c ON c.career_id = o.career_id AND c.is_target
            JOIN skills k ON k.skill_id = o.skill_id AND k.skill_type <> 'work_activity'
            WHERE o.source = 'O*NET'""")
        shared = cur.fetchall()
        pairs = [(a, b) for a, b, _ in shared]
        out += ["## 2. Agreement on skills both sources require", ""]
        if pairs:
            ct = Counter(pairs)
            rows = [[f"O*NET {TIER[a]}"] + [ct.get((a, b), 0) for b in (1, 2, 3)] for a in (3, 2, 1)]
            out += md_table(["", "ESCO peripheral", "ESCO supporting (optional)", "ESCO core (essential)"], rows)
            agree = sum(1 for a, b in pairs if a == b) / len(pairs)
            out += [f"- Shared career-skill pairs: **{len(pairs):,}**",
                    f"- Same tier: **{100 * agree:.1f}%**",
                    f"- Cohen's kappa (O*NET tier vs ESCO tier): **{cohen_kappa(pairs):.3f}**"]
            by_type = Counter(t for _, _, t in shared)
            for t in sorted(by_type):
                tp = [(a, b) for a, b, tt in shared if tt == t]
                out.append(f"- {t}: {len(tp):,} pairs, same tier {100 * sum(a == b for a, b in tp) / len(tp):.1f}%, "
                           f"kappa {cohen_kappa(tp):.3f}")
            out += ["", "Kappa near 0 means the two taxonomies' judgements of *how* important a shared skill is "
                    "are close to independent - a merged list would hide this.", ""]
        else:
            out += ["_No shared career-skill pairs._", ""]

        # ------------------------------------------------ 3. impact on recommendations
        cur.execute("SELECT user_id FROM users WHERE email = 'demo@skillbridge.local'")
        uid = cur.fetchone()[0]
        cur.execute(IMPACT_SQL, (uid,))

        imp = cur.fetchall()
        out += ["## 3. Impact on what the learner is told (demo learner, transfer credit on)", ""]
        out += md_table(["Career", "Requirements (aggregated)", "...with O*NET evidence",
                         "Added by ESCO only (essential)", "Readiness: O*NET only", "Readiness: O*NET + ESCO"], imp)
        if imp:
            added = sum(r[3] for r in imp) / max(sum(r[1] for r in imp), 1)
            diffs = [abs(float(r[5]) - float(r[4])) for r in imp if r[4] is not None and r[5] is not None]
            out += [f"ESCO adds **{100 * added:.1f}%** of the requirements shown to the learner. "
                    f"Readiness changes by **{100 * sum(diffs) / max(len(diffs), 1):.1f} points** on average "
                    f"(max {100 * max(diffs, default=0):.1f}) when ESCO evidence is kept alongside O*NET.", ""]

        # ------------------------------------------------ 5. sensitivity: exact + close links only
        def summary() -> tuple:
            cur.execute(COVERAGE_SQL)
            o, e_, both = cur.fetchone()
            cur.execute(PAIRS_SQL)
            k = cohen_kappa(cur.fetchall())
            cur.execute(IMPACT_SQL, (uid,))
            rows = cur.fetchall()
            added = sum(r[3] for r in rows) / max(sum(r[1] for r in rows), 1)
            d = [abs(float(r[5]) - float(r[4])) for r in rows if r[4] is not None and r[5] is not None]
            return (both / max(o + e_ + both, 1), k, added, sum(d) / max(len(d), 1))

        def with_setting(v: int) -> tuple:
            cur.execute("UPDATE model_parameters SET param_value = %s WHERE param_name = 'crosswalk_use_broad_narrow'", (v,))
            cur.execute("SELECT * FROM fn_apply_crosswalk()")
            return summary()

        full = with_setting(1)
        strict = with_setting(0)
        conn.rollback()                     # leave the database exactly as it was
        cur.execute("SET search_path = core, staging, public")
        out += ["## 4. Sensitivity: which crosswalk links to trust", "",
                "Broad and narrow links import requirements of *related* occupations. Re-running with "
                "exact + close links only (computed in a rolled-back transaction):", ""]
        out += md_table(["Crosswalk links used", "Overlap (both sources)", "Cohen's kappa",
                         "Requirements added by ESCO", "Mean readiness change"],
                        [("exact + close + broad + narrow", f"{100 * full[0]:.1f}%", f"{full[1]:.3f}",
                          f"{100 * full[2]:.1f}%", f"{100 * full[3]:.1f} pts"),
                         ("exact + close only", f"{100 * strict[0]:.1f}%", f"{strict[1]:.3f}",
                          f"{100 * strict[2]:.1f}%", f"{100 * strict[3]:.1f} pts")])
        out += ["Readiness is also pessimistic for a structural reason: the learner's skills are O*NET skills "
                "and transfer edges do not cross into ESCO's vocabulary, so ESCO-only requirements count as "
                "fully missing. Cross-taxonomy alignment (embeddings) addresses this.", ""]

        # ------------------------------------------------ 4. strongest disagreements
        cur.execute("""SELECT career, skill, onet_type, onet_tier, esco_type, esco_tier
                       FROM v_tier_disagreement WHERE is_target
                       ORDER BY tier_gap DESC, career, skill LIMIT 25""")
        out += ["## 5. Strongest disagreements (tier gap 2 first)", ""]
        out += md_table(["Career", "Skill", "O*NET evidence", "O*NET tier", "ESCO evidence", "ESCO tier"],
                        [(c, s, ot, TIER[a], et, TIER[b]) for c, s, ot, a, et, b in cur.fetchall()])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"Done. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
