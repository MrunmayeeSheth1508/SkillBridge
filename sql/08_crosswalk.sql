-- =====================================================================
-- SkillBridge - 08_crosswalk.sql
-- Contribution 1, completed: the official ESCO-O*NET crosswalk links each
-- O*NET career to ESCO occupations, so the SAME career carries evidence
-- from BOTH taxonomies and their disagreement becomes measurable.
--
--   staging.esco_onet_crosswalk  (loaded by scripts/crosswalk.py)
--     -> core.career_source_codes  (crosswalk_exact / close / narrow / broad)
--     -> ESCO evidence copied onto the O*NET career, with
--          confidence  = ESCO confidence x match-type factor
--          skill       = the equivalent O*NET skill when an exact label exists
--                        (e.g. ESCO "Python" -> O*NET "Python"), so both
--                        sources describe one skill and can be compared
--          provenance  = which ESCO occupation, which match type
-- 'related' matches (not validated by the U.S. DOL) are not used.
-- =====================================================================
SET search_path = core, staging, public;

CREATE TABLE IF NOT EXISTS staging.esco_onet_crosswalk (
    onet_code      TEXT NOT NULL,
    esco_uri       TEXT NOT NULL,
    match_type     TEXT NOT NULL,      -- exact / close / narrow / broad / related
    raw_match_type TEXT,
    source_file    TEXT NOT NULL
);

INSERT INTO core.model_parameters (param_name, param_value, description) VALUES
 ('crosswalk_close_factor',        0.90, 'Confidence factor for ESCO evidence reached through a close match'),
 ('crosswalk_broad_narrow_factor', 0.75, 'Confidence factor for ESCO evidence reached through a broad or narrow match'),
 ('crosswalk_use_broad_narrow',    0,    '1 = also import ESCO evidence through broad/narrow matches; 0 = exact + close only (default: more defensible)')
ON CONFLICT (param_name) DO NOTHING;

CREATE OR REPLACE FUNCTION core.fn_apply_crosswalk()
RETURNS TABLE (links INTEGER, careers_linked INTEGER, evidence_rows INTEGER, shared_skills INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    v_onet SMALLINT := (SELECT source_id FROM core.data_sources WHERE source_name = 'O*NET');
    v_esco SMALLINT := (SELECT source_id FROM core.data_sources WHERE source_name = 'ESCO');
BEGIN
    -- 1. career links
    DELETE FROM core.career_source_codes WHERE match_type LIKE 'crosswalk%';
    INSERT INTO core.career_source_codes (career_id, source_id, external_code, match_type)
    SELECT DISTINCT c.career_id, v_esco, x.esco_uri, 'crosswalk_' || x.match_type
    FROM staging.esco_onet_crosswalk x
    JOIN core.careers c ON c.origin_source_id = v_onet AND c.origin_code = x.onet_code
    JOIN core.careers e ON e.origin_source_id = v_esco AND e.origin_code = x.esco_uri
    WHERE x.match_type IN ('exact', 'close', 'narrow', 'broad');

    -- 2. ESCO evidence on the O*NET careers (rebuilt from scratch)
    DELETE FROM core.career_skill_evidence ev
    USING core.careers c
    WHERE ev.career_id = c.career_id AND c.origin_source_id = v_onet AND ev.source_id = v_esco;

    INSERT INTO core.career_skill_evidence
           (career_id, skill_id, source_id, importance, requirement_type, confidence, source_record)
    WITH lk AS (
        SELECT csc.career_id, e.career_id AS esco_career, e.title AS esco_title, csc.match_type,
               CASE csc.match_type
                    WHEN 'crosswalk_exact' THEN 1.0
                    WHEN 'crosswalk_close' THEN core.param('crosswalk_close_factor')
                    ELSE core.param('crosswalk_broad_narrow_factor') END AS factor
        FROM core.career_source_codes csc
        JOIN core.careers e ON e.origin_source_id = v_esco AND e.origin_code = csc.external_code
        WHERE csc.match_type IN ('crosswalk_exact', 'crosswalk_close')
           OR (csc.match_type IN ('crosswalk_broad', 'crosswalk_narrow')
               AND core.param('crosswalk_use_broad_narrow') = 1)
    ),
    canon AS (   -- ESCO skill -> equivalent O*NET skill, when an exact label links them
        SELECT DISTINCT ON (s.from_skill_id) s.from_skill_id AS esco_skill, s.to_skill_id AS onet_skill
        FROM core.skill_similarity s
        JOIN core.skills f ON f.skill_id = s.from_skill_id AND f.taxonomy = 'esco'
        JOIN core.skills t ON t.skill_id = s.to_skill_id AND t.taxonomy LIKE 'onet%'
        WHERE s.method = 'exact_label'
        ORDER BY s.from_skill_id, t.taxonomy, t.skill_id
    ),
    ev AS (
        SELECT lk.career_id, COALESCE(canon.onet_skill, ee.skill_id) AS skill_id,
               ee.importance, ee.requirement_type,
               ROUND(ee.confidence * lk.factor, 2) AS conf,
               lk.match_type, lk.esco_title
        FROM lk
        JOIN core.career_skill_evidence ee ON ee.career_id = lk.esco_career AND ee.source_id = v_esco
        LEFT JOIN canon ON canon.esco_skill = ee.skill_id
    )
    SELECT DISTINCT ON (career_id, skill_id)
           career_id, skill_id, v_esco, importance, requirement_type, GREATEST(conf, 0.01),
           format('ESCO v1.2.1 via crosswalk (%s match): "%s" - %s',
                  replace(match_type, 'crosswalk_', ''), esco_title, requirement_type)
    FROM ev
    ORDER BY career_id, skill_id, importance DESC, conf DESC;

    RETURN QUERY
    SELECT (SELECT COUNT(*)::INT FROM core.career_source_codes WHERE match_type LIKE 'crosswalk%'),
           (SELECT COUNT(DISTINCT career_id)::INT FROM core.career_source_codes WHERE match_type LIKE 'crosswalk%'),
           (SELECT COUNT(*)::INT FROM core.career_skill_evidence ev JOIN core.careers c USING (career_id)
             WHERE c.origin_source_id = v_onet AND ev.source_id = v_esco),
           (SELECT COUNT(*)::INT FROM core.v_career_skill_requirement r
             JOIN core.careers c USING (career_id)
             WHERE c.origin_source_id = v_onet AND r.n_sources > 1);
END $$;

-- Which ESCO occupations a career is linked to (for the dashboard and the report)
CREATE OR REPLACE VIEW core.v_career_crosswalk AS
SELECT c.career_id, c.title AS career, c.origin_code AS onet_code,
       replace(csc.match_type, 'crosswalk_', '') AS match_type,
       e.title AS esco_occupation, csc.external_code AS esco_uri
FROM core.career_source_codes csc
JOIN core.careers c ON c.career_id = csc.career_id
JOIN core.careers e ON e.origin_code = csc.external_code
                   AND e.origin_source_id = (SELECT source_id FROM core.data_sources WHERE source_name = 'ESCO')
WHERE csc.match_type LIKE 'crosswalk%';

-- ---------------------------------------------------------------------
-- Comparable evidence tiers (RQ1). Sources use different scales (O*NET
-- measured importance, ESCO essential/optional, priors for tools), so raw
-- importance differences mostly compare our priors. Tiers make them comparable:
--   3 core       : O*NET IM >= 3.5 | ESCO essential | O*NET In-Demand tool | in >= 50% of postings
--   2 supporting : O*NET IM 2.5-3.5 | ESCO optional | other O*NET tools     | in < 50% of postings
--   1 peripheral : O*NET IM < 2.5
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW core.v_evidence_tier AS
SELECT e.career_id, e.skill_id, d.source_name AS source, e.requirement_type, e.importance,
       CASE
         WHEN e.requirement_type = 'scored'    THEN CASE WHEN e.importance >= 0.625 THEN 3
                                                         WHEN e.importance >= 0.375 THEN 2 ELSE 1 END
         WHEN e.requirement_type = 'essential' THEN 3
         WHEN e.requirement_type = 'optional'  THEN 2
         WHEN d.source_name = 'Job postings'   THEN CASE WHEN e.importance >= 0.5 THEN 3 ELSE 2 END
         ELSE CASE WHEN e.importance >= core.param('tech_in_demand_importance') THEN 3 ELSE 2 END
       END AS tier
FROM core.career_skill_evidence e
JOIN core.data_sources d ON d.source_id = e.source_id;

-- Strong disagreements: one source says core (3), the other peripheral/supporting with a gap of 2,
-- or one says core while the other says only optional.
CREATE OR REPLACE VIEW core.v_tier_disagreement AS
SELECT c.career_id, c.title AS career, c.is_target, k.name AS skill, k.skill_type,
       o.tier AS onet_tier, s.tier AS esco_tier, o.requirement_type AS onet_type,
       s.requirement_type AS esco_type, o.importance AS onet_importance,
       abs(o.tier - s.tier) AS tier_gap
FROM core.v_evidence_tier o
JOIN core.v_evidence_tier s ON s.career_id = o.career_id AND s.skill_id = o.skill_id AND s.source = 'ESCO'
JOIN core.careers c ON c.career_id = o.career_id
JOIN core.skills  k ON k.skill_id  = o.skill_id
WHERE o.source = 'O*NET' AND o.tier <> s.tier;
