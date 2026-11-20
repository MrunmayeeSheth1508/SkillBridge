"""
SkillBridge - build the whole database in one command.

    python scripts/build_database.py data/raw

Steps
  1. Load every raw file into the `staging` schema (scripts/load_staging.py)
  2. sql/02_core_schema.sql  - create the core relational model (15 tables)
  3. sql/03_transform.sql    - clean staging data and fill the core tables
  4. sql/04_views.sql        - query views (evidence, aggregated requirements)
  5. Self-tests (constraints, cycle trigger, history trigger) - rolled back
  6. Write reports/staging_validation.md and reports/core_build.md

Re-running rebuilds everything from the raw files.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # also fixes the Windows libpq PATH before importing psycopg

import psycopg  # noqa: E402

import csv  # noqa: E402

ROOT = ls.PROJECT_ROOT
SQL_FILES = ["02_core_schema.sql", "03_transform.sql", "04_views.sql", "05_analytics.sql",
             "06_nlp.sql", "07_security.sql"]
CORE_REPORT = ROOT / "reports" / "core_build.md"
CURATED_DIR = ROOT / "data" / "curated"

# Demo learner: a mechanical engineer moving towards data careers.
# (taxonomy, name or ILIKE pattern, proficiency)
DEMO_EMAIL = "demo@skillbridge.local"
DEMO_SKILLS = [
    ("onet_knowledge", "Mathematics", 0.80),
    ("onet_knowledge", "Physics", 0.80),
    ("onet_knowledge", "Engineering and Technology", 0.85),
    ("onet_knowledge", "Design", 0.60),
    ("onet_skill", "Mathematics", 0.75),
    ("onet_skill", "Critical Thinking", 0.80),
    ("onet_skill", "Complex Problem Solving", 0.75),
    ("onet_skill", "Science", 0.60),
    ("onet_skill", "Reading Comprehension", 0.80),
    ("onet_skill", "Judgment and Decision Making", 0.60),
    ("onet_skill", "Operations Analysis", 0.50),
    ("onet_technology", "Microsoft Excel", 0.70),
    ("onet_technology", "%MATLAB%", 0.60),
    ("onet_technology", "%AutoCAD%", 0.70),
    ("onet_technology", "%SolidWorks%", 0.60),
]


def find_skill(cur, taxonomy: str, name: str) -> int | None:
    """Exact (case-insensitive) name match first, then ILIKE pattern, shortest name wins."""
    cur.execute("SELECT skill_id FROM core.skills WHERE taxonomy = %s AND lower(name) = lower(%s) LIMIT 1",
                (taxonomy, name.strip("%")))
    row = cur.fetchone()
    if row:
        return row[0]
    pattern = name if "%" in name else f"%{name}%"
    cur.execute("SELECT skill_id FROM core.skills WHERE taxonomy = %s AND name ILIKE %s "
                "ORDER BY length(name) LIMIT 1", (taxonomy, pattern))
    row = cur.fetchone()
    return row[0] if row else None


def load_curated_prerequisites(conn) -> list[str]:
    """Load data/curated/prerequisites.csv through the cycle-checking trigger."""
    notes: list[str] = []
    path = CURATED_DIR / "prerequisites.csv"
    if not path.exists():
        return [f"{path.relative_to(ROOT)} not found - no prerequisites loaded"]
    cur = conn.cursor()
    loaded = 0
    with path.open(encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            pre = find_skill(cur, row["prerequisite_taxonomy"], row["prerequisite"])
            skl = find_skill(cur, row["skill_taxonomy"], row["skill"])
            if pre is None or skl is None:
                missing = row["prerequisite"] if pre is None else row["skill"]
                notes.append(f"prerequisites.csv line {i}: skill not found -> {missing}")
                continue
            cur.execute("SAVEPOINT p")
            try:
                cur.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id, note) "
                            "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                            (skl, pre, row.get("note") or None))
                loaded += cur.rowcount
                cur.execute("RELEASE SAVEPOINT p")
            except psycopg.Error as exc:
                cur.execute("ROLLBACK TO SAVEPOINT p")
                notes.append(f"prerequisites.csv line {i} rejected: {str(exc).splitlines()[0]}")
    conn.commit()
    notes.insert(0, f"{loaded} prerequisite edges loaded")
    return notes


def seed_demo_learner(conn) -> list[str]:
    cur = conn.cursor()
    cur.execute("""INSERT INTO core.users (full_name, email, password_hash, role, weekly_hours)
                   VALUES ('Demo Learner', %s, 'demo-account-no-login', 'learner', 8)
                   ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name
                   RETURNING user_id""", (DEMO_EMAIL,))
    uid = cur.fetchone()[0]
    cur.execute("DELETE FROM core.user_skills WHERE user_id = %s", (uid,))
    notes = []
    for taxonomy, name, p in DEMO_SKILLS:
        sid = find_skill(cur, taxonomy, name)
        if sid is None:
            notes.append(f"demo skill not found: {name}")
            continue
        cur.execute("INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s,%s,%s) "
                    "ON CONFLICT (user_id, skill_id) DO UPDATE SET proficiency = EXCLUDED.proficiency",
                    (uid, sid, p))
    cur.execute("INSERT INTO core.users (full_name, email, password_hash, role) "
                "VALUES ('Administrator', 'admin@skillbridge.local', 'set-via-app', 'admin') "
                "ON CONFLICT (email) DO NOTHING")
    # A second learner, so row-level security has someone else's data to hide
    cur.execute("INSERT INTO core.users (full_name, email, password_hash, role, weekly_hours) "
                "VALUES ('Second Learner', 'learner2@skillbridge.local', 'demo-account-no-login', 'learner', 5) "
                "ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name RETURNING user_id")
    uid2 = cur.fetchone()[0]
    for taxonomy, name, p in [("onet_skill", "Programming", 0.7), ("onet_technology", "Python", 0.8)]:
        sid = find_skill(cur, taxonomy, name)
        if sid is not None:
            cur.execute("INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s,%s,%s) "
                        "ON CONFLICT (user_id, skill_id) DO NOTHING", (uid2, sid, p))
    conn.commit()
    return [f"demo learner user_id={uid}"] + notes

SUMMARY_QUERIES: list[tuple[str, str]] = [
    ("Rows per core table", """
        SELECT relname AS table_name, n_live_tup AS rows
        FROM pg_stat_user_tables WHERE schemaname = 'core' ORDER BY relname"""),
    ("Careers by source", """
        SELECT ds.source_name, COUNT(*) AS careers,
               COUNT(*) FILTER (WHERE c.has_ratings) AS with_onet_ratings,
               COUNT(*) FILTER (WHERE c.is_target)   AS targets
        FROM core.careers c JOIN core.data_sources ds ON ds.source_id = c.origin_source_id
        GROUP BY 1 ORDER BY 1"""),
    ("Skills by taxonomy", """
        SELECT taxonomy, skill_type, COUNT(*) AS skills
        FROM core.skills GROUP BY 1, 2 ORDER BY 1, 2"""),
    ("Evidence by source and type", """
        SELECT ds.source_name, e.requirement_type, COUNT(*) AS rows,
               ROUND(AVG(e.importance), 3) AS avg_importance,
               ROUND(AVG(e.confidence), 3) AS avg_confidence
        FROM core.career_skill_evidence e JOIN core.data_sources ds USING (source_id)
        GROUP BY 1, 2 ORDER BY 1, 2"""),
    ("Skill relationships seeded", """
        SELECT method, COUNT(*) AS edges FROM core.skill_similarity GROUP BY 1 ORDER BY 1"""),
    ("Target careers (4 domains)", """
        SELECT domain, title, origin_code, evidence_rows, scored, technologies
        FROM core.v_target_careers ORDER BY domain, title"""),
    ("Starter-list codes that did not become targets", """
        SELECT c.origin_code, c.title, c.has_ratings
        FROM core.careers c WHERE c.domain IS NOT NULL AND NOT c.is_target"""),
    ("Excluded during transform", """
        SELECT 'ESCO relations to non-skill concepts' AS what, COUNT(*) AS rows
        FROM staging.esco_occupation_skill_relations r
        WHERE NOT EXISTS (SELECT 1 FROM core.skills k
                          WHERE k.taxonomy = 'esco' AND k.external_id = r.skill_uri)
        UNION ALL
        SELECT 'O*NET ratings not relevant at minimum importance',
               COUNT(*) FROM (
                 SELECT onet_soc_code, element_id
                 FROM staging.onet_ratings
                 GROUP BY 1, 2
                 HAVING bool_or(not_relevant = 'Y')
                    AND MAX(data_value::numeric) FILTER (WHERE scale_id = 'IM') <= 1) x"""),
    ("Demo: top 20 requirements for Data Scientists", """
        SELECT skill, taxonomy, source, importance, level_norm, requirement_type, confidence
        FROM core.v_evidence_detail
        WHERE career = 'Data Scientists' AND taxonomy IN ('onet_skill', 'onet_technology')
        ORDER BY importance DESC, level_norm DESC NULLS LAST LIMIT 20"""),
]


def self_tests(conn: psycopg.Connection) -> list[tuple[str, bool, str]]:
    """Exercise the integrity rules inside a transaction that is rolled back."""
    results: list[tuple[str, bool, str]] = []
    cur = conn.cursor()

    def expect_error(name: str, sql: str, params=()) -> None:
        cur.execute("SAVEPOINT t")
        try:
            cur.execute(sql, params)
            results.append((name, False, "statement was accepted"))
        except psycopg.Error as exc:
            results.append((name, True, str(exc).splitlines()[0]))
        cur.execute("ROLLBACK TO SAVEPOINT t")

    cur.execute("SELECT skill_id FROM core.skills WHERE taxonomy = 'onet_skill' ORDER BY skill_id LIMIT 3")
    ids = [r[0] for r in cur.fetchall()]
    if len(ids) < 3:
        return [("self-tests", False, "fewer than 3 O*NET skills loaded")]
    a, b, c = ids

    cur.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s,%s),(%s,%s)",
                (b, a, c, b))  # a -> b -> c
    results.append(("Valid chain a->b->c accepted", True, "ok"))
    expect_error("Self-dependency rejected",
                 "INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s,%s)", (a, a))
    expect_error("Direct cycle b->a rejected",
                 "INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s,%s)", (a, b))
    expect_error("Transitive cycle c->a rejected",
                 "INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s,%s)", (a, c))
    cur.execute("INSERT INTO core.users (full_name, email, password_hash) VALUES ('T','t2@x.org','h') "
                "RETURNING user_id")
    uid = cur.fetchone()[0]
    expect_error("Proficiency 1.5 rejected",
                 "INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s, %s, 1.5)",
                 (uid, a))
    expect_error("Duplicate evidence from the same source rejected",
                 "INSERT INTO core.career_skill_evidence (career_id, skill_id, source_id, importance, "
                 "requirement_type, confidence, source_record) "
                 "SELECT career_id, skill_id, source_id, 0.5, 'scored', 1, 'dup' "
                 "FROM core.career_skill_evidence LIMIT 1")
    cur.execute("INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s,%s,0.2)", (uid, a))
    cur.execute("UPDATE core.user_skills SET proficiency = 0.6 WHERE user_id=%s AND skill_id=%s", (uid, a))
    cur.execute("SELECT COUNT(*) FROM core.user_skill_history WHERE user_id=%s", (uid,))
    n = cur.fetchone()[0]
    results.append(("Proficiency history recorded (insert + update)", n == 2, f"{n} history rows"))

    conn.rollback()
    return results


def analytics_tests(conn) -> list[tuple[str, bool, str]]:
    """Check the Contribution 2 and 3 functions on the demo learner (rolled back)."""
    out: list[tuple[str, bool, str]] = []
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM core.users WHERE email = %s", (DEMO_EMAIL,))
    uid = cur.fetchone()[0]
    cur.execute("SELECT career_id, title FROM core.careers WHERE is_target ORDER BY career_id LIMIT 1")
    row = cur.fetchone()
    if not row:
        return [("Analytics tests", False, "no target careers")]
    cid, title = row

    cur.execute("SELECT COUNT(*) FROM core.skill_similarity WHERE method = 'transfer_v0'")
    n_edges = cur.fetchone()[0]
    cur.execute("""SELECT COUNT(*) FROM core.skill_similarity a
                   JOIN core.skill_similarity b ON b.from_skill_id = a.to_skill_id
                    AND b.to_skill_id = a.from_skill_id AND b.method = a.method
                   WHERE a.method = 'transfer_v0' AND a.weight <> b.weight""")
    n_asym = cur.fetchone()[0]
    out.append(("Directional transfer edges built", n_edges > 0,
                f"{n_edges} edges; {n_asym} have a different weight in the reverse direction"))

    cur.execute("SELECT core.fn_readiness(%s,%s,false), core.fn_readiness(%s,%s,true)", (uid, cid, uid, cid))
    base, transfer = cur.fetchone()
    out.append(("Transfer credit never lowers readiness", (transfer or 0) >= (base or 0),
                f"{title}: baseline {base}, transfer-aware {transfer}"))

    cur.execute("""SELECT COUNT(*) FROM core.fn_gap_analysis(%s,%s,true)
                   WHERE gap < 0 OR gap > importance OR effective_proficiency < own_proficiency""", (uid, cid))
    bad = cur.fetchone()[0]
    out.append(("Gap values consistent (0 <= gap <= importance)", bad == 0, f"{bad} inconsistent rows"))

    cur.execute("SELECT core.fn_build_roadmap(%s,%s,8,true)", (uid, cid))
    rid = cur.fetchone()[0]
    cur.execute("SELECT core.fn_roadmap_violations(%s), total_hours, total_weeks, "
                "(SELECT COUNT(*) FROM core.roadmap_items WHERE roadmap_id = %s) "
                "FROM core.roadmaps WHERE roadmap_id = %s", (rid, rid, rid))
    viol, hours, weeks, items = cur.fetchone()
    out.append(("Roadmap respects prerequisites", viol == 0,
                f"{items} items, {hours} h, {weeks} weeks at 8 h/week, {viol} violations"))
    conn.rollback()
    return out


SAMPLE_AD = ("We need a data scientist with Python, SQL and scikit-learn. "
             "Strong mathematics and critical thinking. Experience with Tableau is a plus.")


def nlp_tests(conn) -> list[tuple[str, bool, str]]:
    """Extraction finds skills; approving a candidate creates Job-postings evidence (rolled back)."""
    out: list[tuple[str, bool, str]] = []
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM core.mv_skill_lexicon")
    lex = cur.fetchone()[0]
    cur.execute("SELECT string_agg(skill, ', ' ORDER BY start_tok) FROM core.fn_extract_from_text(%s)", (SAMPLE_AD,))
    found = cur.fetchone()[0] or ""
    out.append(("Skill extraction finds skills in a job ad", "Python" in found,
                f"lexicon {lex:,} labels; found: {found[:70]}"))
    cur.execute("SELECT career_id FROM core.careers WHERE is_target ORDER BY career_id LIMIT 1")
    cid = cur.fetchone()[0]
    cur.execute("SELECT user_id FROM core.users WHERE role = 'admin' LIMIT 1")
    admin = cur.fetchone()[0]
    cur.execute("SELECT core.fn_submit_job_posting(%s, %s)", (cid, SAMPLE_AD))
    batch = cur.fetchone()[0]
    cur.execute("SELECT candidate_id FROM core.extraction_candidates WHERE batch_id = %s "
                "ORDER BY candidate_id LIMIT 1", (batch,))
    cand = cur.fetchone()[0]
    cur.execute("SELECT core.fn_review_candidate(%s, %s, true)", (cand, admin))
    cur.execute("""SELECT COUNT(*) FROM core.career_skill_evidence e
                   JOIN core.data_sources d USING (source_id)
                   WHERE e.career_id = %s AND d.source_name = 'Job postings'""", (cid,))
    n = cur.fetchone()[0]
    out.append(("Approved extraction becomes Job-postings evidence (trigger)", n == 1, f"{n} evidence row(s)"))
    conn.rollback()
    return out


def security_tests(conn) -> list[tuple[str, bool, str]]:
    """Row-level security and privileges, exercised as the learner role (rolled back)."""
    out: list[tuple[str, bool, str]] = []
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM core.users WHERE email = %s", (DEMO_EMAIL,))
    uid = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM core.user_skills")
    all_users = cur.fetchone()[0]
    cur.execute("SELECT set_config('skillbridge.user_id', %s, true)", (str(uid),))
    cur.execute("SET LOCAL ROLE skillbridge_learner")
    cur.execute("SELECT COUNT(DISTINCT user_id), MIN(user_id) FROM core.user_skills")
    seen, who = cur.fetchone()
    out.append(("RLS: learner sees only own skills", seen == 1 and who == uid,
                f"table holds {all_users} learners' skills; learner role sees {seen}"))

    def denied(name: str, sql: str) -> None:
        cur.execute("SAVEPOINT s")
        try:
            cur.execute(sql)
            out.append((name, False, "allowed"))
        except psycopg.Error as exc:
            out.append((name, True, str(exc).splitlines()[0]))
        cur.execute("ROLLBACK TO SAVEPOINT s")

    denied("Learner cannot read password hashes", "SELECT password_hash FROM core.users")
    denied("Learner cannot change evidence", "DELETE FROM core.career_skill_evidence")
    conn.rollback()
    return out


def table_md(cur, sql: str) -> list[str]:
    cur.execute(sql)
    cols = [d.name for d in cur.description]
    rows = cur.fetchall()
    if not rows:
        return ["_No rows._", ""]
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows[:60]:
        out.append("| " + " | ".join("" if v is None else str(v).replace("|", "/")[:70] for v in r) + " |")
    return out + [""]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/build_database.py <raw_data_dir>")
    raw_dir = Path(sys.argv[1])
    url = ls.get_database_url()
    t0 = time.time()

    print("Step 1/5  Reading and loading raw files into staging ...")
    files, notes = ls.collect_sources(raw_dir)
    with psycopg.connect(url) as conn:
        conn.execute(ls.SCHEMA_SQL.read_text(encoding="utf-8"))
        conn.commit()
        warnings = ls.load_all(conn, files)
        staging_report = ["# SkillBridge staging validation report", ""]
        if notes or warnings:
            staging_report += ["## Loader notes", ""] + [f"- {n}" for n in notes + warnings] + [""]
        staging_report += ls.run_checks(conn)
        ls.REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ls.REPORT_PATH.write_text("\n".join(staging_report), encoding="utf-8")

        for name in SQL_FILES:
            print(f"          Running sql/{name} ...")
            conn.execute((ROOT / "sql" / name).read_text(encoding="utf-8"))
            conn.commit()

        print("          Loading curated prerequisites, lexicon blocklist and demo learner ...")
        build_notes = load_curated_prerequisites(conn) + seed_demo_learner(conn)
        from tune_lexicon import load_blocklist
        build_notes.append(f"{load_blocklist(conn)} lexicon labels blocked (learned on SkillSpan train)")

        print("          Self-tests and report ...")
        tests = self_tests(conn)
        tests += analytics_tests(conn)
        tests += nlp_tests(conn)
        tests += security_tests(conn)
        conn.execute("ANALYZE")
        cur = conn.cursor()
        report = ["# SkillBridge core database build report", "",
                  f"Build time: {time.time() - t0:.0f} s", "", "## Integrity self-tests", "",
                  "| Test | Passed | Detail |", "| --- | --- | --- |"]
        report += [f"| {n} | {'yes' if ok else '**NO**'} | {d.replace('|', '/')[:90]} |" for n, ok, d in tests]
        report += ["", "## Build notes", ""] + [f"- {n}" for n in build_notes] + [""]
        for title, sql in SUMMARY_QUERIES:
            report += [f"## {title}", ""] + table_md(cur, sql)

    CORE_REPORT.write_text("\n".join(report), encoding="utf-8")
    print()
    for n, ok, d in tests:
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
    print(f"\nDone in {time.time() - t0:.0f} s. Reports:")
    print(f"  {ls.REPORT_PATH.relative_to(ROOT)}")
    print(f"  {CORE_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()