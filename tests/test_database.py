"""Database-level tests: schema integrity, the three contributions, NLP and security."""

import psycopg
import pytest


# ---------------------------------------------------------------- data loaded
def test_core_tables_are_populated(cur):
    for table in ("careers", "skills", "career_skill_evidence", "skill_aliases", "data_sources"):
        cur.execute(f"SELECT COUNT(*) FROM core.{table}")
        assert cur.fetchone()[0] > 0, f"core.{table} is empty"


def test_no_orphan_evidence(cur):
    cur.execute("""SELECT COUNT(*) FROM core.career_skill_evidence e
                   LEFT JOIN core.careers c USING (career_id)
                   LEFT JOIN core.skills  k USING (skill_id)
                   WHERE c.career_id IS NULL OR k.skill_id IS NULL""")
    assert cur.fetchone()[0] == 0


def test_normalised_values_in_range(cur):
    cur.execute("""SELECT COUNT(*) FROM core.career_skill_evidence
                   WHERE importance NOT BETWEEN 0 AND 1
                      OR (level_norm IS NOT NULL AND level_norm NOT BETWEEN 0 AND 1)
                      OR confidence NOT BETWEEN 0 AND 1""")
    assert cur.fetchone()[0] == 0


def test_esco_duplicates_removed(cur):
    cur.execute("""SELECT COUNT(*) FROM (SELECT external_id FROM core.skills WHERE taxonomy = 'esco'
                   GROUP BY external_id HAVING COUNT(*) > 1) d""")
    assert cur.fetchone()[0] == 0


# ---------------------------------------------------------------- constraints
def test_proficiency_check_constraint(cur, demo_user, three_skills):
    with pytest.raises(psycopg.errors.CheckViolation):
        cur.execute("INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s, %s, 1.5)",
                    (demo_user, three_skills[0]))


def test_duplicate_evidence_same_source_rejected(cur):
    with pytest.raises(psycopg.errors.UniqueViolation):
        cur.execute("""INSERT INTO core.career_skill_evidence
                       (career_id, skill_id, source_id, importance, requirement_type, confidence, source_record)
                       SELECT career_id, skill_id, source_id, 0.5, 'scored', 1, 'dup'
                       FROM core.career_skill_evidence LIMIT 1""")


# ---------------------------------------------------------------- Contribution 1
def test_aggregated_importance_is_weighted_mean(cur):
    cur.execute("""SELECT r.importance,
                          ROUND(SUM(d.default_weight * e.confidence * e.importance)
                                / SUM(d.default_weight * e.confidence), 4)
                   FROM core.v_career_skill_requirement r
                   JOIN core.career_skill_evidence e USING (career_id, skill_id)
                   JOIN core.data_sources d ON d.source_id = e.source_id
                   GROUP BY r.career_id, r.skill_id, r.importance LIMIT 200""")
    for view_value, manual in cur.fetchall():
        assert view_value == manual


def test_every_evidence_row_has_provenance(cur):
    cur.execute("SELECT COUNT(*) FROM core.career_skill_evidence WHERE coalesce(source_record, '') = ''")
    assert cur.fetchone()[0] == 0


# ---------------------------------------------------------------- Contribution 2
def test_transfer_edges_are_directional(cur):
    cur.execute("""SELECT COUNT(*) FROM core.skill_similarity a
                   JOIN core.skill_similarity b ON b.from_skill_id = a.to_skill_id
                    AND b.to_skill_id = a.from_skill_id AND b.method = a.method
                   WHERE a.method = 'transfer_v0' AND a.weight <> b.weight""")
    assert cur.fetchone()[0] > 0, "expected at least some asymmetric transfer pairs"


def test_transfer_never_lowers_readiness(cur, demo_user):
    cur.execute("""SELECT COUNT(*) FROM core.careers c WHERE c.is_target
                   AND core.fn_readiness(%s, c.career_id, true) < core.fn_readiness(%s, c.career_id, false)""",
                (demo_user, demo_user))
    assert cur.fetchone()[0] == 0


def test_gap_formula(cur, demo_user, target_career):
    cur.execute("""SELECT importance, effective_proficiency, gap, own_proficiency, transfer_credit
                   FROM core.fn_gap_analysis(%s, %s, true)""", (demo_user, target_career))
    rows = cur.fetchall()
    assert rows
    for imp, p_eff, gap, own, credit in rows:
        assert p_eff == max(own, credit)
        assert abs(gap - imp * (1 - p_eff)) < 0.0002
        assert 0 <= gap <= imp


# ---------------------------------------------------------------- Contribution 3
def test_self_dependency_rejected(cur, three_skills):
    a, _, _ = three_skills
    with pytest.raises(psycopg.errors.CheckViolation):
        cur.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)", (a, a))


def test_direct_and_transitive_cycles_rejected(cur, three_skills):
    a, b, c = three_skills
    cur.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s,%s), (%s,%s)",
                (b, a, c, b))                                   # a -> b -> c
    for skill, prereq in ((a, b), (a, c)):                      # b -> a, c -> a
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg.errors.CheckViolation, match="cycle"):
            cur.execute("INSERT INTO core.skill_prerequisites (skill_id, prereq_skill_id) VALUES (%s, %s)",
                        (skill, prereq))
        cur.execute("ROLLBACK TO SAVEPOINT s")


def test_roadmap_valid_and_within_budget(cur, demo_user, target_career):
    cur.execute("SELECT core.fn_build_roadmap(%s, %s, 8, true)", (demo_user, target_career))
    rid = cur.fetchone()[0]
    cur.execute("SELECT core.fn_roadmap_violations(%s)", (rid,))
    assert cur.fetchone()[0] == 0
    # no week is planned for more hours than the budget allows (a step may span weeks)
    cur.execute("""SELECT total_hours, total_weeks FROM core.roadmaps WHERE roadmap_id = %s""", (rid,))
    hours, weeks = cur.fetchone()
    assert weeks == 0 or hours <= weeks * 8


def test_roadmap_rejects_bad_budget(cur, demo_user, target_career):
    with pytest.raises(psycopg.errors.CheckViolation):
        cur.execute("SELECT core.fn_build_roadmap(%s, %s, 500, true)", (demo_user, target_career))


# ---------------------------------------------------------------- tracking
def test_history_trigger(cur, demo_user, three_skills):
    s = three_skills[0]
    cur.execute("DELETE FROM core.user_skills WHERE user_id = %s AND skill_id = %s", (demo_user, s))
    cur.execute("SELECT COUNT(*) FROM core.user_skill_history WHERE user_id = %s AND skill_id = %s", (demo_user, s))
    before = cur.fetchone()[0]
    cur.execute("INSERT INTO core.user_skills (user_id, skill_id, proficiency) VALUES (%s, %s, 0.2)", (demo_user, s))
    cur.execute("UPDATE core.user_skills SET proficiency = 0.7 WHERE user_id = %s AND skill_id = %s", (demo_user, s))
    cur.execute("SELECT COUNT(*) FROM core.user_skill_history WHERE user_id = %s AND skill_id = %s", (demo_user, s))
    assert cur.fetchone()[0] == before + 2


# ---------------------------------------------------------------- NLP
AD = "We need Python, SQL and scikit-learn. Strong mathematics and critical thinking. Excel is a plus."


def test_extraction_finds_known_skills(cur):
    cur.execute("SELECT skill FROM core.fn_extract_from_text(%s)", (AD,))
    found = {r[0] for r in cur.fetchall()}
    assert "Python" in found


def test_extraction_case_sensitive_tools(cur):
    cur.execute("SELECT COUNT(*) FROM core.fn_extract_from_text('You will excel in this role.') WHERE skill ILIKE '%excel%'")
    assert cur.fetchone()[0] == 0, "the verb 'excel' must not match Microsoft Excel"


def test_extraction_spans_do_not_overlap(cur):
    cur.execute("SELECT start_tok, end_tok FROM core.fn_extract_from_text(%s) ORDER BY 1", (AD,))
    spans = cur.fetchall()
    for (s1, e1), (s2, _) in zip(spans, spans[1:]):
        assert e1 < s2


def test_approval_creates_job_posting_evidence(cur, target_career):
    cur.execute("SELECT user_id FROM core.users WHERE role = 'admin' LIMIT 1")
    admin = cur.fetchone()[0]
    cur.execute("SELECT core.fn_submit_job_posting(%s, %s)", (target_career, AD))
    batch = cur.fetchone()[0]
    cur.execute("SELECT candidate_id, matched_skill_id FROM core.extraction_candidates "
                "WHERE batch_id = %s ORDER BY candidate_id LIMIT 1", (batch,))
    cand, skill = cur.fetchone()
    cur.execute("SELECT core.fn_review_candidate(%s, %s, true)", (cand, admin))
    cur.execute("""SELECT COUNT(*) FROM core.career_skill_evidence e JOIN core.data_sources d USING (source_id)
                   WHERE e.career_id = %s AND e.skill_id = %s AND d.source_name = 'Job postings'""",
                (target_career, skill))
    assert cur.fetchone()[0] == 1


# ---------------------------------------------------------------- security
def test_rls_learner_sees_only_own_rows(cur, demo_user):
    cur.execute("SELECT set_config('skillbridge.user_id', %s, true)", (str(demo_user),))
    cur.execute("SET LOCAL ROLE skillbridge_learner")
    cur.execute("SELECT DISTINCT user_id FROM core.user_skills")
    assert [r[0] for r in cur.fetchall()] == [demo_user]


def test_learner_cannot_read_password_hash(cur):
    cur.execute("SET LOCAL ROLE skillbridge_learner")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        cur.execute("SELECT password_hash FROM core.users")


def test_learner_cannot_modify_evidence(cur):
    cur.execute("SET LOCAL ROLE skillbridge_learner")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        cur.execute("DELETE FROM core.career_skill_evidence")


# ---------------------------------------------------------------- crosswalk (Contribution 1)
def test_crosswalk_evidence_is_traceable(cur):
    cur.execute("SELECT COUNT(*) FROM core.career_source_codes WHERE match_type LIKE 'crosswalk%'")
    if cur.fetchone()[0] == 0:
        pytest.skip("crosswalk file not loaded")
    cur.execute("""SELECT COUNT(*) FROM core.career_skill_evidence e
                   JOIN core.careers c USING (career_id) JOIN core.data_sources d USING (source_id)
                   WHERE d.source_name = 'ESCO' AND c.origin_code ~ '^\\d{2}-\\d{4}'
                     AND e.source_record NOT LIKE '%via crosswalk%'""")
    assert cur.fetchone()[0] == 0, "ESCO evidence on O*NET careers must name the crosswalk link"


def test_corroborated_requirements_always_shown(cur, demo_user, target_career):
    cur.execute("""SELECT COUNT(*) FROM core.v_career_skill_requirement r JOIN core.skills k USING (skill_id)
                   WHERE r.career_id = %s AND r.n_sources > 1 AND k.skill_type <> 'work_activity'
                     AND r.skill_id NOT IN (SELECT skill_id FROM core.fn_gap_analysis(%s, %s, true))""",
                (target_career, demo_user, target_career))
    assert cur.fetchone()[0] == 0
