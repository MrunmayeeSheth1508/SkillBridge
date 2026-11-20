-- =====================================================================
-- SkillBridge - 04_views.sql
-- Query layer for Contribution 1 (evidence-aware requirements).
-- =====================================================================
SET search_path = core, staging, public;

-- Every evidence record with readable names (used by the explanation panel)
CREATE OR REPLACE VIEW core.v_evidence_detail AS
SELECT c.career_id, c.title AS career, c.domain,
       k.skill_id, k.name AS skill, k.taxonomy, k.skill_type,
       ds.source_name AS source,
       e.importance, e.level_norm, e.requirement_type, e.confidence,
       e.importance_raw, e.level_raw, e.source_record
FROM core.career_skill_evidence e
JOIN core.careers      c  ON c.career_id  = e.career_id
JOIN core.skills       k  ON k.skill_id   = e.skill_id
JOIN core.data_sources ds ON ds.source_id = e.source_id;

-- Aggregated requirement per (career, skill).
-- I(c,s) = sum(w_d * conf * i) / sum(w_d * conf); records are never overwritten.
CREATE OR REPLACE VIEW core.v_career_skill_requirement AS
SELECT e.career_id, e.skill_id,
       ROUND(SUM(ds.default_weight * e.confidence * e.importance)
             / NULLIF(SUM(ds.default_weight * e.confidence), 0), 4) AS importance,
       COUNT(*)                                              AS n_sources,
       array_agg(ds.source_name ORDER BY ds.source_name)     AS sources,
       ROUND(MAX(e.importance) - MIN(e.importance), 4)       AS disagreement,
       bool_and(e.requirement_type = 'optional')             AS optional_only
FROM core.career_skill_evidence e
JOIN core.data_sources ds ON ds.source_id = e.source_id
GROUP BY e.career_id, e.skill_id;

-- Skills where sources disagree most (meaningful once the crosswalk links
-- ESCO occupations to O*NET careers)
CREATE OR REPLACE VIEW core.v_source_disagreement AS
SELECT r.career_id, c.title AS career, r.skill_id, k.name AS skill,
       r.importance, r.n_sources, r.sources, r.disagreement
FROM core.v_career_skill_requirement r
JOIN core.careers c ON c.career_id = r.career_id
JOIN core.skills  k ON k.skill_id  = r.skill_id
WHERE r.n_sources > 1;

-- Target careers with how much evidence each has
CREATE OR REPLACE VIEW core.v_target_careers AS
SELECT c.career_id, c.title, c.domain, c.origin_code,
       COUNT(e.evidence_id)                                          AS evidence_rows,
       COUNT(e.evidence_id) FILTER (WHERE e.requirement_type = 'scored')  AS scored,
       COUNT(e.evidence_id) FILTER (WHERE e.requirement_type = 'present') AS technologies
FROM core.careers c
LEFT JOIN core.career_skill_evidence e ON e.career_id = c.career_id
WHERE c.is_target
GROUP BY c.career_id, c.title, c.domain, c.origin_code;