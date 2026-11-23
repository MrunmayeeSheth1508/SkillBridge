-- =====================================================================
-- SkillBridge - 05_analytics.sql
-- The computation engine, all inside PostgreSQL:
--   Contribution 2  fn_build_transfer_edges, fn_gap_analysis, fn_readiness
--   Contribution 3  fn_build_roadmap (prerequisite closure, topological
--                   layers, weekly time budget), fn_roadmap_violations
--   Tracking        fn_save_gap_snapshot
-- =====================================================================
SET search_path = core, staging, public;

INSERT INTO core.model_parameters (param_name, param_value, description) VALUES
 ('transfer_alpha',              0.50, 'Exponent on the symmetric similarity term'),
 ('transfer_beta',               1.00, 'Exponent on the directional asymmetry term P(b|a)'),
 ('transfer_min_weight',         0.15, 'Transfer edges below this weight are pruned (tau)'),
 ('transfer_top_k',              15,   'Keep at most k outgoing transfer edges per skill'),
 ('transfer_required_threshold', 0.60, 'O*NET importance at which a skill counts as required for P(b|a)'),
 ('transfer_min_support',        5,    'A skill must be required by at least this many careers'),
 ('gap_min_importance',          0.25, 'Scored skills/knowledge below this importance are not shown as gaps'),
 ('gap_min_importance_tech',     0.90, 'Technologies below this prior (i.e. not In Demand) are not shown'),
 ('roadmap_min_gap',             0.05, 'Gaps smaller than this are not put in a roadmap'),
 ('roadmap_max_skills',          12,   'Maximum target skills per roadmap (before prerequisites)'),
 ('prereq_mastery',              0.50, 'A prerequisite with effective proficiency below this is added to the plan'),
 ('hours_skill',                 40,   'Estimated hours to learn an O*NET skill from zero (scaled by gap and level)'),
 ('hours_knowledge',             40,   'Estimated hours for a knowledge area from zero'),
 ('hours_technology',            25,   'Estimated hours for a technology/tool from zero'),
 ('gap_include_esco_optional',   0,    '1 = also show skills that only ESCO lists, and only as optional')
ON CONFLICT (param_name) DO NOTHING;

-- ---------------------------------------------------------------------
-- Contribution 2: directional transfer edges (data-driven, v0)
--
--   T(a -> b) = sim(a,b)^alpha * A(a -> b)^beta
--     sim  symmetric:  O*NET skills/knowledge -> Pearson correlation of the
--                      importance profiles over all rated careers (>= 0)
--                      technologies -> Jaccard overlap of the careers using them
--     A    directional: P(b required | a required) over careers
--
--   A(a->b) != A(b->a) in general, so T is directional. In the embedding
--   phase, sim is replaced by sentence-embedding cosine similarity.
-- ---------------------------------------------------------------------
-- p_exclude: careers left out of fitting (used by the RQ2 evaluation to avoid leakage)
CREATE OR REPLACE FUNCTION core.fn_build_transfer_edges(p_exclude BIGINT[] DEFAULT '{}') RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    v_rows INTEGER;
BEGIN
    DELETE FROM core.skill_similarity WHERE method = 'transfer_v0';

    -- (1) O*NET scored skills and knowledge
    INSERT INTO core.skill_similarity (from_skill_id, to_skill_id, method, weight, model_version)
    WITH ev AS (
        SELECT e.career_id, e.skill_id, e.importance
        FROM core.career_skill_evidence e
        JOIN core.skills k ON k.skill_id = e.skill_id
        WHERE e.requirement_type = 'scored'
          AND k.taxonomy IN ('onet_skill', 'onet_knowledge')
          AND NOT (e.career_id = ANY (p_exclude))
    ),
    req AS (
        SELECT career_id, skill_id FROM ev
        WHERE importance >= core.param('transfer_required_threshold')
    ),
    n_a AS (
        SELECT skill_id, COUNT(*) AS n FROM req GROUP BY skill_id
        HAVING COUNT(*) >= core.param('transfer_min_support')
    ),
    sim AS (
        SELECT a.skill_id AS a_id, b.skill_id AS b_id,
               GREATEST(corr(a.importance, b.importance), 0)::numeric AS s
        FROM ev a JOIN ev b ON b.career_id = a.career_id AND b.skill_id <> a.skill_id
        GROUP BY a.skill_id, b.skill_id
    ),
    co AS (
        SELECT a.skill_id AS a_id, b.skill_id AS b_id, COUNT(*) AS n_ab
        FROM req a JOIN req b ON b.career_id = a.career_id AND b.skill_id <> a.skill_id
        GROUP BY a.skill_id, b.skill_id
    ),
    t AS (
        SELECT co.a_id, co.b_id,
               power(sim.s, core.param('transfer_alpha'))
             * power(co.n_ab::numeric / n_a.n, core.param('transfer_beta')) AS w
        FROM co
        JOIN n_a ON n_a.skill_id = co.a_id
        JOIN sim ON sim.a_id = co.a_id AND sim.b_id = co.b_id
        WHERE sim.s > 0
    ),
    ranked AS (
        SELECT *, row_number() OVER (PARTITION BY a_id ORDER BY w DESC) AS rn FROM t
    )
    SELECT a_id, b_id, 'transfer_v0', ROUND(LEAST(w, 1), 4), 'corr^a * P(b|a)^b'
    FROM ranked
    WHERE w >= core.param('transfer_min_weight') AND rn <= core.param('transfer_top_k');

    -- (2) O*NET technologies (binary evidence)
    INSERT INTO core.skill_similarity (from_skill_id, to_skill_id, method, weight, model_version)
    WITH used AS (
        SELECT e.career_id, e.skill_id
        FROM core.career_skill_evidence e
        JOIN core.skills k ON k.skill_id = e.skill_id
        WHERE k.taxonomy = 'onet_technology'
          AND NOT (e.career_id = ANY (p_exclude))
    ),
    n_a AS (
        SELECT skill_id, COUNT(*) AS n FROM used GROUP BY skill_id
        HAVING COUNT(*) >= core.param('transfer_min_support')
    ),
    u AS (SELECT used.* FROM used JOIN n_a USING (skill_id)),
    co AS (
        SELECT a.skill_id AS a_id, b.skill_id AS b_id, COUNT(*) AS n_ab
        FROM u a JOIN u b ON b.career_id = a.career_id AND b.skill_id <> a.skill_id
        GROUP BY a.skill_id, b.skill_id
    ),
    t AS (
        SELECT co.a_id, co.b_id,
               power(co.n_ab::numeric / (na.n + nb.n - co.n_ab), core.param('transfer_alpha'))  -- Jaccard
             * power(co.n_ab::numeric / na.n, core.param('transfer_beta')) AS w                 -- P(b|a)
        FROM co
        JOIN n_a na ON na.skill_id = co.a_id
        JOIN n_a nb ON nb.skill_id = co.b_id
    ),
    ranked AS (
        SELECT *, row_number() OVER (PARTITION BY a_id ORDER BY w DESC) AS rn FROM t
    )
    SELECT a_id, b_id, 'transfer_v0', ROUND(LEAST(w, 1), 4), 'jaccard^a * P(b|a)^b'
    FROM ranked
    WHERE w >= core.param('transfer_min_weight') AND rn <= core.param('transfer_top_k');

    SELECT COUNT(*) INTO v_rows FROM core.skill_similarity WHERE method = 'transfer_v0';
    RETURN v_rows;
END $$;

-- ---------------------------------------------------------------------
-- Effective proficiency of one learner in one skill
--   P_eff = max(P_own, lambda * max_a p(u,a) * T(a -> s))
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_skill_effective(p_user BIGINT, p_skill BIGINT, p_use_transfer BOOLEAN)
RETURNS NUMERIC LANGUAGE sql STABLE AS $$
    SELECT GREATEST(
        COALESCE((SELECT proficiency FROM core.user_skills
                  WHERE user_id = p_user AND skill_id = p_skill), 0),
        CASE WHEN p_use_transfer THEN
            core.param('transfer_lambda') * COALESCE((
                SELECT MAX(us.proficiency * s.weight)
                FROM core.skill_similarity s
                JOIN core.user_skills us ON us.skill_id = s.from_skill_id AND us.user_id = p_user
                WHERE s.to_skill_id = p_skill AND s.method IN ('transfer_v0', 'exact_label')), 0)
        ELSE 0 END)
$$;

-- ---------------------------------------------------------------------
-- Gap analysis with full explanation (one row per required skill)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_gap_analysis(p_user BIGINT, p_career BIGINT,
                                                p_use_transfer BOOLEAN DEFAULT TRUE)
RETURNS TABLE (
    skill_id              BIGINT,
    skill                 TEXT,
    skill_type            TEXT,
    importance            NUMERIC,
    n_sources             INTEGER,
    sources               TEXT[],
    level_required        NUMERIC,
    own_proficiency       NUMERIC,
    transfer_from_id      BIGINT,
    transfer_from         TEXT,
    transfer_weight       NUMERIC,
    transfer_credit       NUMERIC,
    transfer_used         BOOLEAN,
    effective_proficiency NUMERIC,
    gap                   NUMERIC
)
LANGUAGE sql STABLE AS $$
    WITH req AS (
        SELECT r.skill_id, k.name, k.skill_type, r.importance, r.n_sources, r.sources,
               (SELECT MAX(e.level_norm) FROM core.career_skill_evidence e
                WHERE e.career_id = p_career AND e.skill_id = r.skill_id) AS level_required
        FROM core.v_career_skill_requirement r
        JOIN core.skills k ON k.skill_id = r.skill_id
        WHERE r.career_id = p_career
          AND k.skill_type IN ('skill', 'knowledge', 'technology')
          AND (r.importance >= CASE WHEN k.skill_type = 'technology'
                                    THEN core.param('gap_min_importance_tech')
                                    ELSE core.param('gap_min_importance') END
               OR r.n_sources > 1)             -- corroborated by 2+ sources: always a requirement
          AND (NOT r.optional_only OR COALESCE(core.param('gap_include_esco_optional'), 0) = 1)
    ),
    own AS (
        SELECT us.skill_id, us.proficiency FROM core.user_skills us WHERE us.user_id = p_user
    ),
    tr AS (   -- strongest transfer contribution into each required skill
        SELECT DISTINCT ON (s.to_skill_id)
               s.to_skill_id, s.from_skill_id, s.weight, o.proficiency * s.weight AS contrib
        FROM core.skill_similarity s
        JOIN own o ON o.skill_id = s.from_skill_id
        WHERE p_use_transfer
          AND s.method IN ('transfer_v0', 'exact_label')
          AND s.to_skill_id IN (SELECT req.skill_id FROM req)
        ORDER BY s.to_skill_id, o.proficiency * s.weight DESC
    ),
    calc AS (
        SELECT req.*, COALESCE(o.proficiency, 0) AS own_p,
               tr.from_skill_id, tr.weight,
               ROUND(core.param('transfer_lambda') * COALESCE(tr.contrib, 0), 4) AS credit
        FROM req
        LEFT JOIN own o ON o.skill_id = req.skill_id
        LEFT JOIN tr    ON tr.to_skill_id = req.skill_id
    )
    SELECT c.skill_id, c.name, c.skill_type, c.importance, c.n_sources::INT, c.sources,
           c.level_required, c.own_p,
           c.from_skill_id, fk.name, c.weight, c.credit,
           c.credit > c.own_p,
           GREATEST(c.own_p, c.credit),
           ROUND(c.importance * (1 - GREATEST(c.own_p, c.credit)), 4)
    FROM calc c
    LEFT JOIN core.skills fk ON fk.skill_id = c.from_skill_id
$$;

CREATE OR REPLACE FUNCTION core.fn_readiness(p_user BIGINT, p_career BIGINT,
                                             p_use_transfer BOOLEAN DEFAULT TRUE)
RETURNS NUMERIC LANGUAGE sql STABLE AS $$
    SELECT ROUND(1 - SUM(gap) / NULLIF(SUM(importance), 0), 4)
    FROM core.fn_gap_analysis(p_user, p_career, p_use_transfer)
$$;

CREATE OR REPLACE FUNCTION core.fn_save_gap_snapshot(p_user BIGINT, p_career BIGINT,
                                                     p_use_transfer BOOLEAN DEFAULT TRUE)
RETURNS BIGINT LANGUAGE sql AS $$
    INSERT INTO core.gap_snapshots (user_id, career_id, use_transfer, readiness, parameters, details)
    SELECT p_user, p_career, p_use_transfer,
           COALESCE(core.fn_readiness(p_user, p_career, p_use_transfer), 0),
           (SELECT jsonb_object_agg(param_name, param_value) FROM core.model_parameters),
           COALESCE((SELECT jsonb_agg(to_jsonb(g) ORDER BY g.gap DESC)
                     FROM core.fn_gap_analysis(p_user, p_career, p_use_transfer) g), '[]'::jsonb)
    RETURNING snapshot_id
$$;

-- ---------------------------------------------------------------------
-- Contribution 3: prerequisite-valid, time-budgeted roadmap
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_build_roadmap(p_user BIGINT, p_career BIGINT,
                                                 p_weekly_hours NUMERIC,
                                                 p_use_transfer BOOLEAN DEFAULT TRUE)
RETURNS BIGINT LANGUAGE plpgsql AS $$
DECLARE
    v_snapshot BIGINT;
    v_roadmap  BIGINT;
    v_total    NUMERIC;
BEGIN
    IF p_weekly_hours IS NULL OR p_weekly_hours <= 0 OR p_weekly_hours > 80 THEN
        RAISE EXCEPTION 'weekly hours must be between 0 and 80' USING ERRCODE = 'check_violation';
    END IF;

    v_snapshot := core.fn_save_gap_snapshot(p_user, p_career, p_use_transfer);

    DROP TABLE IF EXISTS pg_temp.rm_items;
    CREATE TEMP TABLE rm_items AS
    WITH RECURSIVE
    targets AS (
        SELECT g.skill_id, g.gap, g.effective_proficiency, g.level_required
        FROM core.fn_gap_analysis(p_user, p_career, p_use_transfer) g
        WHERE g.gap >= core.param('roadmap_min_gap')
        ORDER BY g.gap DESC
        LIMIT core.param('roadmap_max_skills')::INT
    ),
    need(skill_id) AS (                       -- prerequisite closure
        SELECT skill_id FROM targets
        UNION
        SELECT p.prereq_skill_id
        FROM core.skill_prerequisites p
        JOIN need n ON p.skill_id = n.skill_id
        WHERE core.fn_skill_effective(p_user, p.prereq_skill_id, p_use_transfer)
              < core.param('prereq_mastery')
    ),
    lay(skill_id, layer) AS (                 -- longest prerequisite path = layer
        SELECT skill_id, 1 FROM need
        UNION ALL
        SELECT p.skill_id, l.layer + 1
        FROM lay l
        JOIN core.skill_prerequisites p ON p.prereq_skill_id = l.skill_id
        JOIN need n ON n.skill_id = p.skill_id
    ),
    layered AS (
        SELECT skill_id, MAX(layer) AS layer FROM lay GROUP BY skill_id
    ),
    sized AS (
        SELECT l.skill_id, l.layer, t.gap,
               COALESCE(t.effective_proficiency,
                        core.fn_skill_effective(p_user, l.skill_id, p_use_transfer)) AS p_eff,
               ROUND(
                 CASE k.skill_type WHEN 'technology' THEN core.param('hours_technology')
                                   WHEN 'knowledge'  THEN core.param('hours_knowledge')
                                   ELSE core.param('hours_skill') END
                 * (1 - COALESCE(t.effective_proficiency,
                                 core.fn_skill_effective(p_user, l.skill_id, p_use_transfer)))
                 * (0.5 + COALESCE(t.level_required, 0.5)), 1) AS hours
        FROM layered l
        JOIN core.skills k ON k.skill_id = l.skill_id
        LEFT JOIN targets t ON t.skill_id = l.skill_id
    ),
    ordered AS (
        SELECT s.*,
               row_number() OVER (ORDER BY s.layer, s.gap DESC NULLS LAST, s.skill_id) AS item_no,
               SUM(s.hours) OVER (ORDER BY s.layer, s.gap DESC NULLS LAST, s.skill_id) AS cum_hours
        FROM sized s
        WHERE s.hours > 0
    )
    SELECT item_no, skill_id, layer, hours,
           (FLOOR((cum_hours - hours) / p_weekly_hours) + 1)::INT AS week_start,
           GREATEST(CEIL(cum_hours / p_weekly_hours),
                    FLOOR((cum_hours - hours) / p_weekly_hours) + 1)::INT AS week_end
    FROM ordered;

    SELECT COALESCE(SUM(hours), 0) INTO v_total FROM rm_items;

    INSERT INTO core.roadmaps (user_id, career_id, snapshot_id, weekly_hours, total_hours, total_weeks)
    VALUES (p_user, p_career, v_snapshot, p_weekly_hours, v_total,
            COALESCE((SELECT MAX(week_end) FROM rm_items), 0))
    RETURNING roadmap_id INTO v_roadmap;

    INSERT INTO core.roadmap_items (roadmap_id, item_no, skill_id, layer, week_start, week_end, hours)
    SELECT v_roadmap, item_no, skill_id, layer, week_start, week_end, hours FROM rm_items;

    -- Learning resources (when curated): greedy set cover, then reschedule with real hours
    PERFORM core.fn_assign_resources(v_roadmap);

    RETURN v_roadmap;
END $$;

-- ---------------------------------------------------------------------
-- Resource selection = weighted set cover (NP-hard). Greedy rule (Chvatal 1979):
-- repeatedly take the resource with the lowest hours per NEWLY covered skill;
-- approximation factor H(n) = 1 + 1/2 + ... + 1/n. Compared with the exact
-- ILP optimum in scripts/rq4_roadmap_eval.py (RQ4).
-- Skills no resource covers keep their estimated hours.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_assign_resources(p_roadmap BIGINT)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    r        RECORD;
    v_weekly NUMERIC := (SELECT weekly_hours FROM core.roadmaps WHERE roadmap_id = p_roadmap);
    v_picked INTEGER := 0;
BEGIN
    LOOP
        SELECT lr.resource_id, lr.effort_hours, COUNT(*) AS n_new
        INTO r
        FROM core.roadmap_items ri
        JOIN core.resource_skills rs     ON rs.skill_id = ri.skill_id
        JOIN core.learning_resources lr  ON lr.resource_id = rs.resource_id
        WHERE ri.roadmap_id = p_roadmap AND ri.resource_id IS NULL
        GROUP BY lr.resource_id, lr.effort_hours
        ORDER BY lr.effort_hours / COUNT(*), COUNT(*) DESC, lr.resource_id
        LIMIT 1;
        EXIT WHEN NOT FOUND;

        UPDATE core.roadmap_items ri
        SET resource_id = r.resource_id
        WHERE ri.roadmap_id = p_roadmap AND ri.resource_id IS NULL
          AND ri.skill_id IN (SELECT skill_id FROM core.resource_skills WHERE resource_id = r.resource_id);
        v_picked := v_picked + 1;
    END LOOP;

    IF v_picked = 0 THEN
        RETURN 0;
    END IF;

    -- a resource's hours are shared by the roadmap steps it covers
    UPDATE core.roadmap_items ri
    SET hours = ROUND(lr.effort_hours / x.n_items, 1), hours_source = 'resource'
    FROM core.learning_resources lr,
         (SELECT resource_id, COUNT(*) AS n_items FROM core.roadmap_items
          WHERE roadmap_id = p_roadmap AND resource_id IS NOT NULL GROUP BY resource_id) x
    WHERE ri.roadmap_id = p_roadmap AND ri.resource_id = lr.resource_id AND x.resource_id = lr.resource_id;

    -- reschedule in the same (prerequisite-valid) order with the new hours
    WITH o AS (
        SELECT item_no, hours, SUM(hours) OVER (ORDER BY item_no) AS cum
        FROM core.roadmap_items WHERE roadmap_id = p_roadmap
    )
    UPDATE core.roadmap_items ri
    SET week_start = (FLOOR((o.cum - o.hours) / v_weekly) + 1)::INT,
        week_end   = GREATEST(CEIL(o.cum / v_weekly), FLOOR((o.cum - o.hours) / v_weekly) + 1)::INT
    FROM o
    WHERE ri.roadmap_id = p_roadmap AND ri.item_no = o.item_no;

    UPDATE core.roadmaps
    SET total_hours = (SELECT COALESCE(SUM(hours), 0) FROM core.roadmap_items WHERE roadmap_id = p_roadmap),
        total_weeks = (SELECT COALESCE(MAX(week_end), 0) FROM core.roadmap_items WHERE roadmap_id = p_roadmap)
    WHERE roadmap_id = p_roadmap;
    RETURN v_picked;
END $$;

-- Number of prerequisite violations in a stored roadmap (must be 0)
CREATE OR REPLACE FUNCTION core.fn_roadmap_violations(p_roadmap BIGINT)
RETURNS INTEGER LANGUAGE sql STABLE AS $$
    SELECT COUNT(*)::INT
    FROM core.skill_prerequisites p
    JOIN core.roadmap_items a ON a.roadmap_id = p_roadmap AND a.skill_id = p.prereq_skill_id
    JOIN core.roadmap_items b ON b.roadmap_id = p_roadmap AND b.skill_id = p.skill_id
    WHERE NOT (a.item_no < b.item_no AND a.layer < b.layer AND a.week_start <= b.week_start)
$$;

-- Build the transfer edges now
SELECT core.fn_build_transfer_edges();
