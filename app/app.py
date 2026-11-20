"""
SkillBridge - Flask REST API + dashboard.

    python app/app.py          then open http://127.0.0.1:5000

All analytics run inside PostgreSQL (fn_gap_analysis, fn_readiness,
fn_build_roadmap ...). Flask only passes parameters and returns JSON.
The demo runs as the seeded demo learner; login/roles come in Phase 9.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_database as bd  # noqa: E402  (also fixes the Windows libpq PATH)
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

app = Flask(__name__)
DB_URL = ls.get_database_url()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _clean(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, list):
        return [_clean(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


def query(sql: str, params=(), one: bool = False, commit: bool = False):
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if cur.description else []
        if commit:
            conn.commit()
    rows = [_clean(dict(r)) for r in rows]
    return (rows[0] if rows else None) if one else rows


def demo_user_id() -> int:
    row = query("SELECT user_id FROM core.users WHERE email = %s", (bd.DEMO_EMAIL,), one=True)
    if row is None:
        with psycopg.connect(DB_URL) as conn:
            bd.seed_demo_learner(conn)
        row = query("SELECT user_id FROM core.users WHERE email = %s", (bd.DEMO_EMAIL,), one=True)
    return row["user_id"]


def err(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


@app.errorhandler(psycopg.Error)
def db_error(exc):
    return err(str(exc).splitlines()[0], 400)


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# reference data
# ---------------------------------------------------------------------------
@app.get("/api/overview")
def overview():
    stats = query("""
        SELECT (SELECT COUNT(*) FROM core.careers WHERE has_ratings)          AS rated_careers,
               (SELECT COUNT(*) FROM core.careers)                            AS careers,
               (SELECT COUNT(*) FROM core.skills)                             AS skills,
               (SELECT COUNT(*) FROM core.career_skill_evidence)              AS evidence,
               (SELECT COUNT(*) FROM core.skill_similarity
                 WHERE method = 'transfer_v0')                                AS transfer_edges,
               (SELECT COUNT(*) FROM core.skill_prerequisites)                AS prerequisites,
               (SELECT COUNT(*) FROM core.data_sources)                       AS sources,
               (SELECT param_value FROM core.model_parameters
                 WHERE param_name = 'transfer_lambda')                        AS lambda
    """, one=True)
    return jsonify(stats)


@app.get("/api/careers")
def careers():
    rows = query("""SELECT career_id, title, domain, origin_code, evidence_rows
                    FROM core.v_target_careers ORDER BY domain, title""")
    return jsonify(rows)


@app.get("/api/careers/search")
def careers_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    rows = query("""SELECT career_id, title, domain FROM core.careers
                    WHERE has_ratings AND title ILIKE %s
                    ORDER BY (lower(title) LIKE lower(%s)) DESC, length(title) LIMIT 12""",
                 (f"%{q}%", f"{q}%"))
    return jsonify(rows)


@app.get("/api/skills/search")
def skills_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    rows = query("""
        SELECT skill_id, name, taxonomy, skill_type, is_hot_technology
        FROM core.skills
        WHERE taxonomy IN ('onet_skill', 'onet_knowledge', 'onet_technology')
          AND name ILIKE %s
        ORDER BY (lower(name) = lower(%s)) DESC, (lower(name) LIKE lower(%s)) DESC,
                 taxonomy <> 'onet_technology' DESC, length(name)
        LIMIT 12""", (f"%{q}%", q, f"{q}%"))
    return jsonify(rows)


# ---------------------------------------------------------------------------
# learner profile
# ---------------------------------------------------------------------------
@app.get("/api/me")
def me():
    uid = demo_user_id()
    user = query("SELECT user_id, full_name, email, role, weekly_hours FROM core.users WHERE user_id = %s",
                 (uid,), one=True)
    user["skills"] = query("""
        SELECT us.skill_id, k.name, k.taxonomy, k.skill_type, us.proficiency, us.updated_at::text
        FROM core.user_skills us JOIN core.skills k USING (skill_id)
        WHERE us.user_id = %s
        ORDER BY k.skill_type, k.name""", (uid,))
    return jsonify(user)


@app.put("/api/me")
def update_me():
    body = request.get_json(force=True)
    hours = body.get("weekly_hours")
    query("UPDATE core.users SET weekly_hours = %s WHERE user_id = %s", (hours, demo_user_id()), commit=True)
    return me()


@app.put("/api/me/skills")
def upsert_skill():
    body = request.get_json(force=True)
    sid, p = body.get("skill_id"), body.get("proficiency")
    if sid is None or p is None:
        return err("skill_id and proficiency are required")
    query("""INSERT INTO core.user_skills (user_id, skill_id, proficiency, updated_at)
             VALUES (%s, %s, %s, now())
             ON CONFLICT (user_id, skill_id)
             DO UPDATE SET proficiency = EXCLUDED.proficiency, updated_at = now()""",
          (demo_user_id(), sid, round(float(p), 2)), commit=True)
    return jsonify({"ok": True})


@app.delete("/api/me/skills/<int:skill_id>")
def delete_skill(skill_id: int):
    query("DELETE FROM core.user_skills WHERE user_id = %s AND skill_id = %s",
          (demo_user_id(), skill_id), commit=True)
    return jsonify({"ok": True})


@app.post("/api/me/reset")
def reset_demo():
    with psycopg.connect(DB_URL) as conn:
        bd.seed_demo_learner(conn)
    return me()


@app.get("/api/me/history")
def history():
    rows = query("""SELECT skill_id, k.name, old_proficiency, new_proficiency, changed_at::text
                    FROM core.user_skill_history h JOIN core.skills k USING (skill_id)
                    WHERE user_id = %s ORDER BY changed_at DESC LIMIT 30""", (demo_user_id(),))
    return jsonify(rows)


# ---------------------------------------------------------------------------
# Contribution 2: gap analysis with transfer credit
# ---------------------------------------------------------------------------
@app.get("/api/gap/<int:career_id>")
def gap(career_id: int):
    uid = demo_user_id()
    career = query("SELECT career_id, title, domain, description, origin_code FROM core.careers "
                   "WHERE career_id = %s", (career_id,), one=True)
    if not career:
        return err("career not found", 404)
    with_t = query("SELECT * FROM core.fn_gap_analysis(%s, %s, true) ORDER BY gap DESC", (uid, career_id))
    base = {r["skill_id"]: r["gap"] for r in
            query("SELECT skill_id, gap FROM core.fn_gap_analysis(%s, %s, false)", (uid, career_id))}
    for r in with_t:
        r["gap_baseline"] = base.get(r["skill_id"], r["gap"])
    readiness = query("SELECT core.fn_readiness(%s,%s,false) AS baseline, "
                      "core.fn_readiness(%s,%s,true) AS transfer", (uid, career_id, uid, career_id), one=True)
    by_type: dict[str, int] = {}
    for r in with_t:
        by_type[r["skill_type"]] = by_type.get(r["skill_type"], 0) + 1
    return jsonify({
        "career": career,
        "readiness": readiness,
        "gaps": with_t,
        "summary": {
            "requirements": len(with_t),
            "by_type": by_type,
            "transfer_used": sum(1 for r in with_t if r["transfer_used"]),
            "met": sum(1 for r in with_t if r["gap"] < 0.05),
            "sources": sorted({s for r in with_t for s in (r["sources"] or [])}),
        },
    })


@app.get("/api/explain/<int:career_id>/<int:skill_id>")
def explain(career_id: int, skill_id: int):
    uid = demo_user_id()
    row = query("SELECT * FROM core.fn_gap_analysis(%s,%s,true) WHERE skill_id = %s",
                (uid, career_id, skill_id), one=True)
    if not row:
        return err("skill is not a requirement of this career", 404)
    base = query("SELECT gap FROM core.fn_gap_analysis(%s,%s,false) WHERE skill_id = %s",
                 (uid, career_id, skill_id), one=True)
    evidence = query("""SELECT source, requirement_type, importance_raw, level_raw, importance,
                               level_norm, confidence, source_record
                        FROM core.v_evidence_detail WHERE career_id = %s AND skill_id = %s
                        ORDER BY source""", (career_id, skill_id))
    skill = query("SELECT skill_id, name, description, taxonomy, skill_type, is_hot_technology "
                  "FROM core.skills WHERE skill_id = %s", (skill_id,), one=True)
    candidates = query("""
        SELECT k.name, us.proficiency, s.weight,
               ROUND(us.proficiency * s.weight * core.param('transfer_lambda'), 4) AS credit
        FROM core.skill_similarity s
        JOIN core.user_skills us ON us.skill_id = s.from_skill_id AND us.user_id = %s
        JOIN core.skills k ON k.skill_id = s.from_skill_id
        WHERE s.to_skill_id = %s AND s.method IN ('transfer_v0', 'exact_label')
        ORDER BY credit DESC LIMIT 5""", (uid, skill_id))
    prereqs = query("""SELECT k.skill_id, k.name,
                              ROUND(core.fn_skill_effective(%s, k.skill_id, true), 2) AS your_level
                       FROM core.skill_prerequisites p JOIN core.skills k ON k.skill_id = p.prereq_skill_id
                       WHERE p.skill_id = %s ORDER BY k.name""", (uid, skill_id))
    lam = query("SELECT core.param('transfer_lambda') AS l", one=True)["l"]
    return jsonify({"skill": skill, "gap": row, "gap_baseline": base["gap"] if base else None,
                    "evidence": evidence, "transfer_candidates": candidates,
                    "prerequisites": prereqs, "lambda": lam})


@app.post("/api/snapshot/<int:career_id>")
def snapshot(career_id: int):
    use_transfer = bool((request.get_json(silent=True) or {}).get("use_transfer", True))
    row = query("SELECT core.fn_save_gap_snapshot(%s::bigint, %s::bigint, %s::boolean) AS id",
                (demo_user_id(), career_id, use_transfer), one=True, commit=True)
    return jsonify(row)


@app.get("/api/snapshots/<int:career_id>")
def snapshots(career_id: int):
    rows = query("""SELECT snapshot_id, use_transfer, readiness, created_at::text
                    FROM core.gap_snapshots WHERE user_id = %s AND career_id = %s
                    ORDER BY created_at""", (demo_user_id(), career_id))
    return jsonify(rows)


# ---------------------------------------------------------------------------
# Contribution 3: roadmap
# ---------------------------------------------------------------------------
@app.post("/api/roadmap/<int:career_id>")
def roadmap(career_id: int):
    body = request.get_json(silent=True) or {}
    uid = demo_user_id()
    hours = float(body.get("weekly_hours") or 8)
    use_transfer = bool(body.get("use_transfer", True))
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        rid = conn.execute("SELECT core.fn_build_roadmap(%s::bigint, %s::bigint, %s::numeric, %s::boolean) AS id",
                           (uid, career_id, hours, use_transfer)).fetchone()["id"]
        conn.commit()
    meta = query("""SELECT r.roadmap_id, r.weekly_hours, r.total_hours, r.total_weeks, r.created_at::text,
                           core.fn_roadmap_violations(r.roadmap_id) AS violations,
                           s.readiness
                    FROM core.roadmaps r LEFT JOIN core.gap_snapshots s USING (snapshot_id)
                    WHERE r.roadmap_id = %s""", (rid,), one=True)
    items = query("""
        SELECT ri.item_no, ri.skill_id, k.name AS skill, k.skill_type, ri.layer,
               ri.week_start, ri.week_end, ri.hours,
               lr.title AS resource, lr.url AS resource_url,
               (SELECT array_agg(pk.name ORDER BY pk.name)
                FROM core.skill_prerequisites p
                JOIN core.roadmap_items pi ON pi.roadmap_id = ri.roadmap_id AND pi.skill_id = p.prereq_skill_id
                JOIN core.skills pk ON pk.skill_id = p.prereq_skill_id
                WHERE p.skill_id = ri.skill_id) AS after,
               g.gap
        FROM core.roadmap_items ri
        JOIN core.skills k ON k.skill_id = ri.skill_id
        LEFT JOIN core.learning_resources lr ON lr.resource_id = ri.resource_id
        LEFT JOIN core.fn_gap_analysis(%s, %s, %s) g ON g.skill_id = ri.skill_id
        WHERE ri.roadmap_id = %s ORDER BY ri.item_no""", (uid, career_id, use_transfer, rid))
    return jsonify({"roadmap": meta, "items": items})


# ---------------------------------------------------------------------------
# NLP: job-description skill extraction + admin review
# ---------------------------------------------------------------------------
def admin_user_id() -> int:
    row = query("SELECT user_id FROM core.users WHERE role = 'admin' ORDER BY user_id LIMIT 1", one=True)
    return row["user_id"]


def candidates_for(where: str, params) -> list[dict]:
    return query(f"""
        SELECT ec.candidate_id, ec.batch_id, ec.span_start, ec.span_end, ec.span_text, ec.method,
               ec.match_score AS score, ec.status, ec.source_text,
               k.skill_id, k.name AS skill, k.skill_type, k.taxonomy, c.title AS career
        FROM core.extraction_candidates ec
        LEFT JOIN core.skills k ON k.skill_id = ec.matched_skill_id
        LEFT JOIN core.careers c ON c.career_id = ec.career_id
        WHERE {where}
        ORDER BY ec.batch_id DESC, ec.span_start""", params)


@app.post("/api/extract")
def extract():
    body = request.get_json(force=True)
    text = (body.get("text") or "").strip()
    career_id = body.get("career_id")
    if len(text) < 10:
        return err("Paste a job description of at least a sentence.")
    if len(text) > 20000:
        return err("Job description is too long (max 20,000 characters).")
    fuzzy = bool(body.get("fuzzy", True))
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        batch = conn.execute("SELECT core.fn_submit_job_posting(%s::bigint, %s, %s) AS b",
                             (career_id, text, fuzzy)).fetchone()["b"]
        tokens = conn.execute("SELECT core.fn_tokenize(%s) AS t", (text,)).fetchone()["t"]
        conn.commit()
    return jsonify({"batch_id": batch, "tokens": tokens,
                    "candidates": candidates_for("ec.batch_id = %s", (batch,))})


@app.post("/api/candidates/<int:candidate_id>/review")
def review(candidate_id: int):
    approve = bool((request.get_json(silent=True) or {}).get("approve", True))
    row = query("SELECT core.fn_review_candidate(%s::bigint, %s::bigint, %s) AS status",
                (candidate_id, admin_user_id(), approve), one=True, commit=True)
    if not row or row["status"] is None:
        return err("candidate not found", 404)
    cand = candidates_for("ec.candidate_id = %s", (candidate_id,))[0]
    return jsonify({"candidate": cand})


@app.get("/api/candidates")
def candidates():
    status = request.args.get("status", "pending")
    career_id = request.args.get("career_id", type=int)
    where, params = "ec.status = %s", [status]
    if career_id:
        where += " AND ec.career_id = %s"
        params.append(career_id)
    return jsonify(candidates_for(where, tuple(params))[:200])


@app.get("/api/postings/<int:career_id>")
def postings(career_id: int):
    """Job-posting evidence for a career + how it compares with the other sources."""
    rows = query("""
        SELECT k.name AS skill, k.skill_type, r.importance, r.n_sources, r.sources, r.disagreement
        FROM core.v_career_skill_requirement r JOIN core.skills k USING (skill_id)
        WHERE r.career_id = %s AND 'Job postings' = ANY (r.sources)
        ORDER BY r.disagreement DESC, k.name""", (career_id,))
    stats = query("""SELECT COUNT(DISTINCT batch_id) AS postings,
                            COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                            COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
                            COUNT(*) FILTER (WHERE status = 'pending')  AS pending
                     FROM core.extraction_candidates WHERE career_id = %s""", (career_id,), one=True)
    return jsonify({"stats": stats, "evidence": rows})


# ---------------------------------------------------------------------------
# career comparison
# ---------------------------------------------------------------------------
@app.get("/api/compare")
def compare():
    uid = demo_user_id()
    out = []
    for key in ("a", "b"):
        cid = request.args.get(key, type=int)
        if cid is None:
            continue
        c = query("SELECT career_id, title, domain FROM core.careers WHERE career_id = %s", (cid,), one=True)
        if not c:
            continue
        c.update(query("SELECT core.fn_readiness(%s,%s,false) AS baseline, "
                       "core.fn_readiness(%s,%s,true) AS transfer", (uid, cid, uid, cid), one=True))
        c["top_gaps"] = query("SELECT skill, skill_type, gap FROM core.fn_gap_analysis(%s,%s,true) "
                              "ORDER BY gap DESC LIMIT 6", (uid, cid))
        out.append(c)
    return jsonify(out)


@app.get("/api/rank")
def rank():
    """Readiness for every target career - 'where am I closest?'"""
    uid = demo_user_id()
    rows = query("""SELECT career_id, title, domain,
                           core.fn_readiness(%s, career_id, false) AS baseline,
                           core.fn_readiness(%s, career_id, true)  AS transfer
                    FROM core.careers WHERE is_target
                    ORDER BY transfer DESC NULLS LAST""", (uid, uid))
    return jsonify(rows)


if __name__ == "__main__":
    print("\n  SkillBridge dashboard ->  http://127.0.0.1:5000\n")
    app.run(debug=False, port=5000)