"""
SkillBridge - Flask REST API + dashboard.

    python app/app.py          then open http://127.0.0.1:5000

All analytics run inside PostgreSQL (fn_gap_analysis, fn_readiness,
fn_build_roadmap, fn_extract_skills ...). Flask only passes parameters and
returns JSON.

Security is enforced BY THE DATABASE: after login, every request runs inside a
transaction that does
    SELECT set_config('skillbridge.user_id', <id>, true);   -- identity for row-level security
    SET LOCAL ROLE skillbridge_learner | skillbridge_admin;  -- privileges from 07_security.sql
so a learner's queries can only see that learner's rows, whatever the Python code asks for.
Passwords are hashed with Werkzeug (scrypt/pbkdf2); sessions are signed Flask cookies.
"""

from __future__ import annotations

import os
import secrets
import sys
from contextlib import contextmanager
from decimal import Decimal
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_database as bd  # noqa: E402  (also fixes the Windows libpq PATH)
import load_staging as ls  # noqa: E402

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

DB_URL = ls.get_database_url()


def _secret_key() -> str:
    """FLASK_SECRET_KEY from .env, else a random key stored in .flask_secret (git-ignored)."""
    if os.environ.get("FLASK_SECRET_KEY"):
        return os.environ["FLASK_SECRET_KEY"]
    path = ROOT / ".flask_secret"
    if not path.exists():
        path.write_text(secrets.token_hex(32), encoding="utf-8")
    return path.read_text(encoding="utf-8").strip()


app = Flask(__name__)
app.config.update(SECRET_KEY=_secret_key(), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

# Demo accounts (password set on first start if the build left a placeholder)
DEMO_ACCOUNTS = {
    "demo@skillbridge.local": "demo1234",
    "learner2@skillbridge.local": "learner1234",
    "admin@skillbridge.local": "admin1234",
}


# ---------------------------------------------------------------------------
# database access - always as the logged-in user's database role
# ---------------------------------------------------------------------------
def _clean(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, list):
        return [_clean(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


@contextmanager
def db(as_user: bool = True):
    """A connection whose transaction runs with the current user's DB role + RLS identity."""
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        if as_user and "user_id" in session:
            conn.execute("SELECT set_config('skillbridge.user_id', %s, true)", (str(session["user_id"]),))
            conn.execute("SET LOCAL ROLE skillbridge_admin" if session.get("role") == "admin"
                         else "SET LOCAL ROLE skillbridge_learner")
        yield conn


def query(sql: str, params=(), one: bool = False, commit: bool = False, as_user: bool = True):
    with db(as_user) as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if cur.description else []
        if commit:
            conn.commit()
    rows = [_clean(dict(r)) for r in rows]
    return (rows[0] if rows else None) if one else rows


def uid() -> int:
    return session["user_id"]


def err(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


@app.errorhandler(psycopg.Error)
def db_error(exc):
    msg = str(exc).splitlines()[0]
    code = 403 if isinstance(exc, psycopg.errors.InsufficientPrivilege) else 400
    return err(msg, code)


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return err("Please log in.", 401)
        return fn(*a, **kw)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return err("Please log in.", 401)
        if session.get("role") != "admin":
            return err("Administrator access required.", 403)
        return fn(*a, **kw)
    return wrapper


def ensure_demo_passwords() -> None:
    """Give the seeded demo accounts real hashed passwords (only if still a placeholder)."""
    with psycopg.connect(DB_URL) as conn:
        for email, pw in DEMO_ACCOUNTS.items():
            conn.execute("""UPDATE core.users SET password_hash = %s
                            WHERE email = %s AND password_hash NOT LIKE 'scrypt:%%'
                              AND password_hash NOT LIKE 'pbkdf2:%%'""",
                         (generate_password_hash(pw), email))
        conn.commit()


# ---------------------------------------------------------------------------
# pages + authentication
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("index.html")


@app.get("/login")
def login_page():
    return render_template("login.html")


@app.post("/api/login")
def login():
    body = request.get_json(force=True)
    email = (body.get("email") or "").strip().lower()
    row = query("SELECT user_id, full_name, role, password_hash FROM core.users WHERE lower(email) = %s",
                (email,), one=True, as_user=False)
    if not row or not row["password_hash"].startswith(("scrypt:", "pbkdf2:")) \
            or not check_password_hash(row["password_hash"], body.get("password") or ""):
        return err("Wrong email or password.", 401)
    session.clear()
    session.update(user_id=row["user_id"], role=row["role"], name=row["full_name"])
    return jsonify({"user_id": row["user_id"], "role": row["role"], "full_name": row["full_name"]})


@app.post("/api/register")
def register():
    body = request.get_json(force=True)
    name = (body.get("full_name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    pw = body.get("password") or ""
    hours = body.get("weekly_hours") or 8
    if len(name) < 2:
        return err("Please enter your name.")
    if "@" not in email:
        return err("Please enter a valid email.")
    if len(pw) < 8:
        return err("Password must be at least 8 characters.")
    try:
        row = query("""INSERT INTO core.users (full_name, email, password_hash, role, weekly_hours)
                       VALUES (%s, %s, %s, 'learner', %s) RETURNING user_id""",
                    (name, email, generate_password_hash(pw), hours), one=True, commit=True, as_user=False)
    except psycopg.errors.UniqueViolation:
        return err("An account with this email already exists.", 409)
    session.clear()
    session.update(user_id=row["user_id"], role="learner", name=name)
    return jsonify({"user_id": row["user_id"], "role": "learner", "full_name": name}), 201


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/session")
@login_required
def current_session():
    return jsonify({"user_id": uid(), "role": session.get("role"), "full_name": session.get("name"),
                    "is_demo": query("SELECT email = %s AS d FROM core.users WHERE user_id = %s",
                                     (bd.DEMO_EMAIL, uid()), one=True)["d"]})


# ---------------------------------------------------------------------------
# reference data
# ---------------------------------------------------------------------------
@app.get("/api/overview")
@login_required
def overview():
    return jsonify(query("""
        SELECT (SELECT COUNT(*) FROM core.careers WHERE has_ratings)                     AS rated_careers,
               (SELECT COUNT(*) FROM core.careers)                                       AS careers,
               (SELECT COUNT(*) FROM core.skills)                                        AS skills,
               (SELECT COUNT(*) FROM core.career_skill_evidence)                         AS evidence,
               (SELECT COUNT(*) FROM core.skill_similarity WHERE method = 'transfer_v0') AS transfer_edges,
               (SELECT COUNT(*) FROM core.skill_prerequisites)                           AS prerequisites,
               (SELECT COUNT(*) FROM core.data_sources)                                  AS sources,
               (SELECT param_value FROM core.model_parameters
                 WHERE param_name = 'transfer_lambda')                                   AS lambda
    """, one=True))


@app.get("/api/careers")
@login_required
def careers():
    return jsonify(query("""SELECT career_id, title, domain, origin_code, evidence_rows
                            FROM core.v_target_careers ORDER BY domain, title"""))


@app.get("/api/careers/search")
@login_required
def careers_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    return jsonify(query("""SELECT career_id, title, domain FROM core.careers
                            WHERE has_ratings AND title ILIKE %s
                            ORDER BY (lower(title) LIKE lower(%s)) DESC, length(title) LIMIT 12""",
                         (f"%{q}%", f"{q}%")))


@app.get("/api/skills/search")
@login_required
def skills_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    taxonomies = ("onet_skill", "onet_knowledge", "onet_technology")
    if request.args.get("all") == "1":
        taxonomies += ("esco",)
    return jsonify(query("""
        SELECT skill_id, name, taxonomy, skill_type, is_hot_technology
        FROM core.skills
        WHERE taxonomy = ANY(%s) AND name ILIKE %s
        ORDER BY (lower(name) = lower(%s)) DESC, (lower(name) LIKE lower(%s)) DESC,
                 (taxonomy = 'esco'), taxonomy <> 'onet_technology' DESC, length(name)
        LIMIT 12""", (list(taxonomies), f"%{q}%", q, f"{q}%")))


# ---------------------------------------------------------------------------
# learner profile (row-level security limits every query to the user's own rows)
# ---------------------------------------------------------------------------
@app.get("/api/me")
@login_required
def me():
    user = query("SELECT user_id, full_name, email, role, weekly_hours FROM core.users WHERE user_id = %s",
                 (uid(),), one=True)
    user["skills"] = query("""
        SELECT us.skill_id, k.name, k.taxonomy, k.skill_type, us.proficiency, us.updated_at::text
        FROM core.user_skills us JOIN core.skills k USING (skill_id)
        WHERE us.user_id = %s                      -- explicit filter; RLS enforces it for learners anyway
        ORDER BY k.skill_type, k.name""", (uid(),))
    user["is_demo"] = user["email"] == bd.DEMO_EMAIL
    return jsonify(user)


@app.put("/api/me")
@login_required
def update_me():
    hours = (request.get_json(force=True) or {}).get("weekly_hours")
    query("UPDATE core.users SET weekly_hours = %s WHERE user_id = %s", (hours, uid()), commit=True)
    return me()


@app.put("/api/me/skills")
@login_required
def upsert_skill():
    body = request.get_json(force=True)
    sid, p = body.get("skill_id"), body.get("proficiency")
    if sid is None or p is None:
        return err("skill_id and proficiency are required")
    query("""INSERT INTO core.user_skills (user_id, skill_id, proficiency, updated_at)
             VALUES (%s, %s, %s, now())
             ON CONFLICT (user_id, skill_id)
             DO UPDATE SET proficiency = EXCLUDED.proficiency, updated_at = now()""",
          (uid(), sid, round(float(p), 2)), commit=True)
    return jsonify({"ok": True})


@app.delete("/api/me/skills/<int:skill_id>")
@login_required
def delete_skill(skill_id: int):
    query("DELETE FROM core.user_skills WHERE user_id = %s AND skill_id = %s", (uid(), skill_id), commit=True)
    return jsonify({"ok": True})


@app.post("/api/me/reset")
@login_required
def reset_demo():
    row = query("SELECT email FROM core.users WHERE user_id = %s", (uid(),), one=True)
    if row["email"] != bd.DEMO_EMAIL:
        return err("Only the demo account can be reset.", 403)
    with psycopg.connect(DB_URL) as conn:
        bd.seed_demo_learner(conn)
    ensure_demo_passwords()
    return me()


@app.get("/api/me/history")
@login_required
def history():
    return jsonify(query("""SELECT h.skill_id, k.name, h.old_proficiency, h.new_proficiency, h.changed_at::text
                            FROM core.user_skill_history h JOIN core.skills k USING (skill_id)
                            WHERE h.user_id = %s ORDER BY h.changed_at DESC LIMIT 30""", (uid(),)))


# ---------------------------------------------------------------------------
# Contribution 2: gap analysis with transfer credit
# ---------------------------------------------------------------------------
@app.get("/api/gap/<int:career_id>")
@login_required
def gap(career_id: int):
    career = query("SELECT career_id, title, domain, description, origin_code FROM core.careers "
                   "WHERE career_id = %s", (career_id,), one=True)
    if not career:
        return err("career not found", 404)
    with_t = query("SELECT * FROM core.fn_gap_analysis(%s, %s, true) ORDER BY gap DESC", (uid(), career_id))
    base = {r["skill_id"]: r["gap"] for r in
            query("SELECT skill_id, gap FROM core.fn_gap_analysis(%s, %s, false)", (uid(), career_id))}
    for r in with_t:
        r["gap_baseline"] = base.get(r["skill_id"], r["gap"])
    readiness = query("SELECT core.fn_readiness(%s,%s,false) AS baseline, "
                      "core.fn_readiness(%s,%s,true) AS transfer", (uid(), career_id, uid(), career_id), one=True)
    by_type: dict[str, int] = {}
    for r in with_t:
        by_type[r["skill_type"]] = by_type.get(r["skill_type"], 0) + 1
    return jsonify({
        "career": career, "readiness": readiness, "gaps": with_t,
        "summary": {"requirements": len(with_t), "by_type": by_type,
                    "transfer_used": sum(1 for r in with_t if r["transfer_used"]),
                    "met": sum(1 for r in with_t if r["gap"] < 0.05),
                    "sources": sorted({s for r in with_t for s in (r["sources"] or [])})},
    })


@app.get("/api/explain/<int:career_id>/<int:skill_id>")
@login_required
def explain(career_id: int, skill_id: int):
    row = query("SELECT * FROM core.fn_gap_analysis(%s,%s,true) WHERE skill_id = %s",
                (uid(), career_id, skill_id), one=True)
    if not row:
        return err("skill is not a requirement of this career", 404)
    base = query("SELECT gap FROM core.fn_gap_analysis(%s,%s,false) WHERE skill_id = %s",
                 (uid(), career_id, skill_id), one=True)
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
        ORDER BY credit DESC LIMIT 5""", (uid(), skill_id))
    prereqs = query("""SELECT k.skill_id, k.name,
                              ROUND(core.fn_skill_effective(%s, k.skill_id, true), 2) AS your_level
                       FROM core.skill_prerequisites p JOIN core.skills k ON k.skill_id = p.prereq_skill_id
                       WHERE p.skill_id = %s ORDER BY k.name""", (uid(), skill_id))
    lam = query("SELECT core.param('transfer_lambda') AS l", one=True)["l"]
    return jsonify({"skill": skill, "gap": row, "gap_baseline": base["gap"] if base else None,
                    "evidence": evidence, "transfer_candidates": candidates,
                    "prerequisites": prereqs, "lambda": lam})


@app.post("/api/snapshot/<int:career_id>")
@login_required
def snapshot(career_id: int):
    use_transfer = bool((request.get_json(silent=True) or {}).get("use_transfer", True))
    return jsonify(query("SELECT core.fn_save_gap_snapshot(%s::bigint, %s::bigint, %s::boolean) AS id",
                         (uid(), career_id, use_transfer), one=True, commit=True))


@app.get("/api/snapshots/<int:career_id>")
@login_required
def snapshots(career_id: int):
    return jsonify(query("""SELECT snapshot_id, use_transfer, readiness, created_at::text
                            FROM core.gap_snapshots WHERE user_id = %s AND career_id = %s
                            ORDER BY created_at""", (uid(), career_id)))


# ---------------------------------------------------------------------------
# Contribution 3: roadmap
# ---------------------------------------------------------------------------
@app.post("/api/roadmap/<int:career_id>")
@login_required
def roadmap(career_id: int):
    body = request.get_json(silent=True) or {}
    hours = float(body.get("weekly_hours") or 8)
    use_transfer = bool(body.get("use_transfer", True))
    with db() as conn:
        rid = conn.execute("SELECT core.fn_build_roadmap(%s::bigint, %s::bigint, %s::numeric, %s::boolean) AS id",
                           (uid(), career_id, hours, use_transfer)).fetchone()["id"]
        conn.commit()
    meta = query("""SELECT r.roadmap_id, r.weekly_hours, r.total_hours, r.total_weeks, r.created_at::text,
                           core.fn_roadmap_violations(r.roadmap_id) AS violations, s.readiness
                    FROM core.roadmaps r LEFT JOIN core.gap_snapshots s USING (snapshot_id)
                    WHERE r.roadmap_id = %s""", (rid,), one=True)
    items = query("""
        SELECT ri.item_no, ri.skill_id, k.name AS skill, k.skill_type, ri.layer,
               ri.week_start, ri.week_end, ri.hours,
               lr.title AS resource, lr.url AS resource_url, lr.provider AS resource_provider,
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
        WHERE ri.roadmap_id = %s ORDER BY ri.item_no""", (uid(), career_id, use_transfer, rid))
    return jsonify({"roadmap": meta, "items": items})


# ---------------------------------------------------------------------------
# comparison + ranking
# ---------------------------------------------------------------------------
@app.get("/api/compare")
@login_required
def compare():
    out = []
    for key in ("a", "b"):
        cid = request.args.get(key, type=int)
        if cid is None:
            continue
        c = query("SELECT career_id, title, domain FROM core.careers WHERE career_id = %s", (cid,), one=True)
        if not c:
            continue
        c.update(query("SELECT core.fn_readiness(%s,%s,false) AS baseline, "
                       "core.fn_readiness(%s,%s,true) AS transfer", (uid(), cid, uid(), cid), one=True))
        c["top_gaps"] = query("SELECT skill, skill_type, gap FROM core.fn_gap_analysis(%s,%s,true) "
                              "ORDER BY gap DESC LIMIT 6", (uid(), cid))
        out.append(c)
    return jsonify(out)


@app.get("/api/rank")
@login_required
def rank():
    return jsonify(query("""SELECT career_id, title, domain,
                                   core.fn_readiness(%s, career_id, false) AS baseline,
                                   core.fn_readiness(%s, career_id, true)  AS transfer
                            FROM core.careers WHERE is_target
                            ORDER BY transfer DESC NULLS LAST""", (uid(), uid())))


# ---------------------------------------------------------------------------
# ADMIN: job-description extraction + review (Contribution 1, job-postings source)
# ---------------------------------------------------------------------------
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
@admin_required
def extract():
    body = request.get_json(force=True)
    text = (body.get("text") or "").strip()
    if len(text) < 10:
        return err("Paste a job description of at least a sentence.")
    if len(text) > 20000:
        return err("Job description is too long (max 20,000 characters).")
    with db() as conn:
        batch = conn.execute("SELECT core.fn_submit_job_posting(%s::bigint, %s, %s) AS b",
                             (body.get("career_id"), text, bool(body.get("fuzzy", True)))).fetchone()["b"]
        tokens = conn.execute("SELECT core.fn_tokenize(%s) AS t", (text,)).fetchone()["t"]
        conn.commit()
    return jsonify({"batch_id": batch, "tokens": tokens,
                    "candidates": candidates_for("ec.batch_id = %s", (batch,))})


@app.post("/api/candidates/<int:candidate_id>/review")
@admin_required
def review(candidate_id: int):
    approve = bool((request.get_json(silent=True) or {}).get("approve", True))
    row = query("SELECT core.fn_review_candidate(%s::bigint, %s::bigint, %s) AS status",
                (candidate_id, uid(), approve), one=True, commit=True)
    if not row or row["status"] is None:
        return err("candidate not found", 404)
    return jsonify({"candidate": candidates_for("ec.candidate_id = %s", (candidate_id,))[0]})


@app.get("/api/candidates")
@admin_required
def candidates():
    where, params = "ec.status = %s", [request.args.get("status", "pending")]
    if request.args.get("career_id", type=int):
        where += " AND ec.career_id = %s"
        params.append(request.args.get("career_id", type=int))
    return jsonify(candidates_for(where, tuple(params))[:200])


@app.get("/api/postings/<int:career_id>")
@login_required
def postings(career_id: int):
    rows = query("""
        SELECT k.name AS skill, k.skill_type, r.importance, r.n_sources, r.sources, r.disagreement
        FROM core.v_career_skill_requirement r JOIN core.skills k USING (skill_id)
        WHERE r.career_id = %s AND 'Job postings' = ANY (r.sources)
        ORDER BY r.disagreement DESC, k.name""", (career_id,))
    stats = {"postings": 0, "approved": 0, "rejected": 0, "pending": 0}
    if session.get("role") == "admin":
        stats = query("""SELECT COUNT(DISTINCT batch_id) AS postings,
                                COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                                COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
                                COUNT(*) FILTER (WHERE status = 'pending')  AS pending
                         FROM core.extraction_candidates WHERE career_id = %s""", (career_id,), one=True)
    return jsonify({"stats": stats, "evidence": rows})


# ---------------------------------------------------------------------------
# ADMIN: prerequisite graph, parameters, users
# ---------------------------------------------------------------------------
@app.get("/api/admin/prerequisites")
@admin_required
def admin_prereqs():
    return jsonify(query("""
        SELECT p.prereq_skill_id, pk.name AS prerequisite, pk.skill_type AS prerequisite_type,
               p.skill_id, k.name AS skill, k.skill_type, p.note, u.full_name AS created_by,
               p.created_at::date::text AS created
        FROM core.skill_prerequisites p
        JOIN core.skills k  ON k.skill_id  = p.skill_id
        JOIN core.skills pk ON pk.skill_id = p.prereq_skill_id
        LEFT JOIN core.users u ON u.user_id = p.created_by
        ORDER BY pk.name, k.name"""))


@app.post("/api/admin/prerequisites")
@admin_required
def admin_add_prereq():
    body = request.get_json(force=True)
    try:
        query("""INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id, created_by, note)
                 VALUES (%s, %s, %s, %s)""",
              (body.get("skill_id"), body.get("prereq_skill_id"), uid(), body.get("note") or None), commit=True)
    except psycopg.errors.UniqueViolation:
        return err("This prerequisite already exists.", 409)
    except psycopg.errors.CheckViolation as exc:          # self-dependency or cycle - from the trigger
        return err(str(exc).splitlines()[0], 422)
    return jsonify({"ok": True}), 201


@app.delete("/api/admin/prerequisites")
@admin_required
def admin_delete_prereq():
    query("DELETE FROM core.skill_prerequisites WHERE skill_id = %s AND prereq_skill_id = %s",
          (request.args.get("skill_id", type=int), request.args.get("prereq_skill_id", type=int)), commit=True)
    return jsonify({"ok": True})


EDITABLE_PARAMS = ("transfer_lambda", "gap_min_importance", "gap_min_importance_tech",
                   "gap_include_esco_optional", "roadmap_max_skills", "prereq_mastery",
                   "hours_skill", "hours_knowledge", "hours_technology", "nlp_min_similarity")


@app.get("/api/admin/parameters")
@admin_required
def admin_params():
    return jsonify(query("SELECT param_name, param_value, description FROM core.model_parameters "
                         "WHERE param_name = ANY(%s) ORDER BY param_name", (list(EDITABLE_PARAMS),)))


@app.put("/api/admin/parameters")
@admin_required
def admin_set_param():
    body = request.get_json(force=True)
    name, value = body.get("param_name"), body.get("param_value")
    if name not in EDITABLE_PARAMS:
        return err("This parameter cannot be changed from the dashboard.", 403)
    query("UPDATE core.model_parameters SET param_value = %s WHERE param_name = %s", (value, name), commit=True)
    return jsonify({"ok": True})


@app.get("/api/admin/users")
@admin_required
def admin_users():
    return jsonify(query("""SELECT u.user_id, u.full_name, u.email, u.role, u.weekly_hours,
                                   u.created_at::date::text AS created,
                                   (SELECT COUNT(*) FROM core.user_skills s WHERE s.user_id = u.user_id) AS skills
                            FROM core.users u ORDER BY u.user_id"""))


ensure_demo_passwords()

if __name__ == "__main__":
    print("\n  SkillBridge dashboard ->  http://127.0.0.1:5000")
    print("  Demo logins:  demo@skillbridge.local / demo1234   (learner)")
    print("                admin@skillbridge.local / admin1234 (administrator)\n")
    app.run(debug=False, port=5000)
