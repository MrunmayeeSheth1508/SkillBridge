-- =====================================================================
-- SkillBridge - 03_transform.sql
-- Staging -> core. Applies the cleaning rules decided from
-- reports/staging_validation.md:
--   * ESCO duplicate URIs: keep the row with the latest modified_date
--   * ESCO concepts with no skill_type (5 DigComp areas): not skills, excluded
--   * O*NET Recommend Suppress = Y: kept, confidence lowered
--   * O*NET Not Relevant = Y: level = 0; dropped if importance is at minimum
--   * O*NET Technology Skills: binary evidence with prior importance
-- Run after 02_core_schema.sql (which creates empty tables).
-- =====================================================================
SET search_path = core, staging, public;

-- ---------------------------------------------------------------------
-- 1. Reference data
-- ---------------------------------------------------------------------
INSERT INTO core.data_sources (source_name, source_type, version, url, default_weight, description) VALUES
 ('O*NET',           'taxonomy',     NULL,     'https://www.onetcenter.org/database.html', 1.00,
  'US occupational database: scored skills, knowledge, work activities; technology skills'),
 ('ESCO',            'taxonomy',     'v1.2.1', 'https://esco.ec.europa.eu',               0.80,
  'European skills/occupations taxonomy: essential/optional relations, no scores'),
 ('Job postings',    'job_postings', NULL,     NULL,                                       0.60,
  'Skills extracted from job descriptions and approved by an administrator'),
 ('Manual curation', 'manual',       NULL,     NULL,                                       1.00,
  'Entered by a project administrator');

INSERT INTO core.model_parameters (param_name, param_value, description) VALUES
 ('esco_essential_importance', 0.80, 'Prior importance for an ESCO essential skill'),
 ('esco_optional_importance',  0.40, 'Prior importance for an ESCO optional skill'),
 ('esco_confidence',           0.80, 'Confidence of ESCO relations'),
 ('onet_suppressed_confidence',0.50, 'Confidence of O*NET ratings flagged Recommend Suppress = Y'),
 ('tech_base_importance',      0.60, 'Prior importance for an O*NET technology skill'),
 ('tech_hot_importance',       0.80, 'Prior importance for a Hot Technology'),
 ('tech_in_demand_importance', 0.90, 'Prior importance for an In Demand technology'),
 ('tech_confidence',           0.70, 'Confidence of O*NET technology-skill evidence'),
 ('transfer_lambda',           0.80, 'Cap on transfer credit: P_eff = max(P_own, lambda * T)');

-- ---------------------------------------------------------------------
-- 2. Careers
-- ---------------------------------------------------------------------
-- O*NET occupations (1,016; 910 have ratings)
INSERT INTO core.careers (title, description, origin_source_id, origin_code, has_ratings)
SELECT o.title, o.description,
       (SELECT source_id FROM core.data_sources WHERE source_name = 'O*NET'),
       o.onet_soc_code,
       EXISTS (SELECT 1 FROM staging.onet_ratings r
               WHERE r.onet_soc_code = o.onet_soc_code AND r.category LIKE 'skill%')
FROM staging.onet_occupations o;

-- ESCO occupations, de-duplicated (latest modified_date wins)
INSERT INTO core.careers (title, description, origin_source_id, origin_code)
SELECT DISTINCT ON (e.concept_uri)
       e.preferred_label, e.description,
       (SELECT source_id FROM core.data_sources WHERE source_name = 'ESCO'),
       e.concept_uri
FROM staging.esco_occupations e
ORDER BY e.concept_uri, e.modified_date DESC NULLS LAST;

-- Native identifiers
INSERT INTO core.career_source_codes (career_id, source_id, external_code, match_type)
SELECT career_id, origin_source_id, origin_code, 'native' FROM core.careers;

-- Target careers for the 4 domains. Starter list - review it as a team;
-- edit codes here and re-run. Only occupations with O*NET ratings qualify.
WITH target(onet_soc_code, domain) AS (VALUES
  ('15-2051.00', 'Data & AI'),                    -- Data Scientists
  ('15-2041.00', 'Data & AI'),                    -- Statisticians
  ('15-1221.00', 'Data & AI'),                    -- Computer and Information Research Scientists
  ('15-1243.00', 'Data & AI'),                    -- Database Architects
  ('15-1242.00', 'Data & AI'),                    -- Database Administrators
  ('15-2031.00', 'Data & AI'),                    -- Operations Research Analysts
  ('15-1252.00', 'Software engineering'),         -- Software Developers
  ('15-1253.00', 'Software engineering'),         -- Software QA Analysts and Testers
  ('15-1254.00', 'Software engineering'),         -- Web Developers
  ('15-1255.00', 'Software engineering'),         -- Web and Digital Interface Designers
  ('15-1211.00', 'Software engineering'),         -- Computer Systems Analysts
  ('15-1244.00', 'Software engineering'),         -- Network and Computer Systems Administrators
  ('17-2141.00', 'Mechanical & manufacturing engineering'),  -- Mechanical Engineers
  ('17-2112.00', 'Mechanical & manufacturing engineering'),  -- Industrial Engineers
  ('17-2112.03', 'Mechanical & manufacturing engineering'),  -- Manufacturing Engineers
  ('17-2141.02', 'Mechanical & manufacturing engineering'),  -- Automotive Engineers
  ('17-2199.08', 'Mechanical & manufacturing engineering'),  -- Robotics Engineers
  ('17-3027.00', 'Mechanical & manufacturing engineering'),  -- Mechanical Engineering Technologists
  ('13-2099.01', 'Business & finance analytics'), -- Financial and Investment Analysts
  ('13-1111.00', 'Business & finance analytics'), -- Management Analysts
  ('13-1161.00', 'Business & finance analytics'), -- Market Research Analysts
  ('13-2041.00', 'Business & finance analytics'), -- Credit Analysts
  ('15-2011.00', 'Business & finance analytics'), -- Actuaries
  ('13-1081.02', 'Business & finance analytics')  -- Logistics Analysts
)
UPDATE core.careers c
SET domain = t.domain, is_target = c.has_ratings
FROM target t
WHERE c.origin_code = t.onet_soc_code
  AND c.origin_source_id = (SELECT source_id FROM core.data_sources WHERE source_name = 'O*NET');

-- ---------------------------------------------------------------------
-- 3. Skills
-- ---------------------------------------------------------------------
-- O*NET skills (35), knowledge (33), work activities (41)
INSERT INTO core.skills (name, description, taxonomy, skill_type, external_id)
SELECT DISTINCT ON (r.element_id)
       r.element_name, cm.description,
       CASE r.category WHEN 'knowledge'     THEN 'onet_knowledge'
                       WHEN 'work_activity' THEN 'onet_work_activity'
                       ELSE 'onet_skill' END,
       CASE r.category WHEN 'knowledge'     THEN 'knowledge'
                       WHEN 'work_activity' THEN 'work_activity'
                       ELSE 'skill' END,
       r.element_id
FROM staging.onet_ratings r
LEFT JOIN staging.onet_content_model cm USING (element_id)
ORDER BY r.element_id;

-- O*NET technology skills: one skill per tool
INSERT INTO core.skills (name, description, taxonomy, skill_type, external_id, is_hot_technology)
SELECT t.workplace_example,
       string_agg(DISTINCT t.element_name, '; '),
       'onet_technology', 'technology',
       t.workplace_example,
       bool_or(t.hot_technology = 'Y')
FROM staging.onet_technology_skills t
WHERE t.workplace_example IS NOT NULL
GROUP BY t.workplace_example;

-- ESCO skills, de-duplicated; the 5 concepts without skill_type are excluded
INSERT INTO core.skills (name, description, taxonomy, skill_type, external_id, reuse_level)
SELECT DISTINCT ON (s.concept_uri)
       s.preferred_label, s.description, 'esco',
       CASE s.skill_type WHEN 'knowledge' THEN 'knowledge' ELSE 'skill' END,
       s.concept_uri, s.reuse_level
FROM staging.esco_skills s
WHERE s.skill_type IS NOT NULL
ORDER BY s.concept_uri, s.modified_date DESC NULLS LAST;

-- ---------------------------------------------------------------------
-- 4. Skill aliases (preferred first, so it wins on duplicates)
-- ---------------------------------------------------------------------
INSERT INTO core.skill_aliases (skill_id, alias, alias_type)
SELECT skill_id, trim(name), 'preferred' FROM core.skills
ON CONFLICT (skill_id, alias) DO NOTHING;

WITH esco AS (
    SELECT DISTINCT ON (concept_uri) concept_uri, alt_labels, hidden_labels
    FROM staging.esco_skills
    WHERE skill_type IS NOT NULL
    ORDER BY concept_uri, modified_date DESC NULLS LAST
)
INSERT INTO core.skill_aliases (skill_id, alias, alias_type)
SELECT k.skill_id, trim(a.alias), a.alias_type
FROM esco e
JOIN core.skills k ON k.taxonomy = 'esco' AND k.external_id = e.concept_uri
CROSS JOIN LATERAL (
    SELECT regexp_split_to_table(e.alt_labels, E'\\s*\\n\\s*') AS alias, 'alternative' AS alias_type
    UNION ALL
    SELECT regexp_split_to_table(e.hidden_labels, E'\\s*\\n\\s*'), 'hidden'
) a
WHERE a.alias IS NOT NULL AND length(trim(a.alias)) > 0
ON CONFLICT (skill_id, alias) DO NOTHING;

-- ---------------------------------------------------------------------
-- 5. Career-skill evidence
-- ---------------------------------------------------------------------
-- 5a. O*NET scored ratings: one row per occupation x element (IM + LV)
WITH r AS (
    SELECT onet_soc_code, element_id, category,
           MAX(data_value::numeric) FILTER (WHERE scale_id = 'IM') AS im,
           MAX(data_value::numeric) FILTER (WHERE scale_id = 'LV') AS lv,
           bool_or(recommend_suppress = 'Y') AS suppress,
           bool_or(not_relevant = 'Y')       AS not_relevant
    FROM staging.onet_ratings
    GROUP BY onet_soc_code, element_id, category
),
sc AS (
    SELECT MAX(minimum::numeric) FILTER (WHERE scale_id = 'IM') AS im_min,
           MAX(maximum::numeric) FILTER (WHERE scale_id = 'IM') AS im_max,
           MAX(minimum::numeric) FILTER (WHERE scale_id = 'LV') AS lv_min,
           MAX(maximum::numeric) FILTER (WHERE scale_id = 'LV') AS lv_max
    FROM staging.onet_scales
)
INSERT INTO core.career_skill_evidence
       (career_id, skill_id, source_id, importance_raw, level_raw,
        importance, level_norm, requirement_type, confidence, source_record)
SELECT c.career_id, k.skill_id, c.origin_source_id, r.im, r.lv,
       ROUND((r.im - sc.im_min) / (sc.im_max - sc.im_min), 4),
       CASE WHEN r.not_relevant THEN 0
            ELSE ROUND((r.lv - sc.lv_min) / (sc.lv_max - sc.lv_min), 4) END,
       'scored',
       CASE WHEN r.suppress THEN core.param('onet_suppressed_confidence') ELSE 1.0 END,
       'O*NET ' || r.category || ' ' || r.element_id || ' (IM ' || r.im || ', LV ' || r.lv || ')'
FROM r
CROSS JOIN sc
JOIN core.careers c ON c.origin_code = r.onet_soc_code
                   AND c.origin_source_id = (SELECT source_id FROM core.data_sources WHERE source_name = 'O*NET')
JOIN core.skills  k ON k.external_id = r.element_id
                   AND k.taxonomy IN ('onet_skill', 'onet_knowledge', 'onet_work_activity')
WHERE r.im IS NOT NULL
  AND NOT (r.not_relevant AND r.im <= sc.im_min);

-- 5b. O*NET technology skills (binary evidence with priors)
WITH t AS (
    SELECT onet_soc_code, workplace_example,
           bool_or(hot_technology = 'Y') AS hot,
           bool_or(in_demand = 'Y')      AS in_demand
    FROM staging.onet_technology_skills
    WHERE workplace_example IS NOT NULL
    GROUP BY onet_soc_code, workplace_example
)
INSERT INTO core.career_skill_evidence
       (career_id, skill_id, source_id, importance, requirement_type, confidence, source_record)
SELECT c.career_id, k.skill_id, c.origin_source_id,
       CASE WHEN t.in_demand THEN core.param('tech_in_demand_importance')
            WHEN t.hot       THEN core.param('tech_hot_importance')
            ELSE core.param('tech_base_importance') END,
       'present',
       core.param('tech_confidence'),
       'O*NET Technology Skills'
         || CASE WHEN t.hot THEN ' [Hot Technology]' ELSE '' END
         || CASE WHEN t.in_demand THEN ' [In Demand]' ELSE '' END
FROM t
JOIN core.careers c ON c.origin_code = t.onet_soc_code
                   AND c.origin_source_id = (SELECT source_id FROM core.data_sources WHERE source_name = 'O*NET')
JOIN core.skills  k ON k.taxonomy = 'onet_technology' AND k.external_id = t.workplace_example;

-- 5c. ESCO essential/optional relations
INSERT INTO core.career_skill_evidence
       (career_id, skill_id, source_id, importance, requirement_type, confidence, source_record)
SELECT c.career_id, k.skill_id, c.origin_source_id,
       CASE r.relation_type WHEN 'essential' THEN core.param('esco_essential_importance')
                            ELSE core.param('esco_optional_importance') END,
       r.relation_type,
       core.param('esco_confidence'),
       'ESCO v1.2.1 occupationSkillRelations (' || r.relation_type || ')'
FROM staging.esco_occupation_skill_relations r
JOIN core.careers c ON c.origin_code = r.occupation_uri
                   AND c.origin_source_id = (SELECT source_id FROM core.data_sources WHERE source_name = 'ESCO')
JOIN core.skills  k ON k.taxonomy = 'esco' AND k.external_id = r.skill_uri
WHERE r.relation_type IN ('essential', 'optional')
ON CONFLICT (career_id, skill_id, source_id) DO NOTHING;

-- ---------------------------------------------------------------------
-- 6. Seed skill relationships (raw signals for the transfer engine)
-- ---------------------------------------------------------------------
-- 6a. Exact label matches between O*NET tools/skills and ESCO skills (both directions)
WITH m AS (
    SELECT DISTINCT o.skill_id AS onet_id, e.skill_id AS esco_id
    FROM core.skills o
    JOIN core.skill_aliases a ON lower(a.alias) = lower(o.name)
                             AND a.alias_type IN ('preferred', 'alternative')
    JOIN core.skills e ON e.skill_id = a.skill_id AND e.taxonomy = 'esco'
    WHERE o.taxonomy IN ('onet_technology', 'onet_skill', 'onet_knowledge')
)
INSERT INTO core.skill_similarity (from_skill_id, to_skill_id, method, weight, model_version)
SELECT onet_id, esco_id, 'exact_label', 1, 'v1' FROM m
UNION ALL
SELECT esco_id, onet_id, 'exact_label', 1, 'v1' FROM m
ON CONFLICT DO NOTHING;

-- 6b. ESCO skill-skill relations (original -> related)
INSERT INTO core.skill_similarity (from_skill_id, to_skill_id, method, weight, model_version)
SELECT DISTINCT a.skill_id, b.skill_id, 'esco_relation_' || r.relation_type,
       CASE r.relation_type WHEN 'essential' THEN 0.6 ELSE 0.3 END, 'ESCO v1.2.1'
FROM staging.esco_skill_skill_relations r
JOIN core.skills a ON a.taxonomy = 'esco' AND a.external_id = r.original_skill_uri
JOIN core.skills b ON b.taxonomy = 'esco' AND b.external_id = r.related_skill_uri
WHERE a.skill_id <> b.skill_id
ON CONFLICT DO NOTHING;

-- 6c. ESCO hierarchy: narrower skill -> broader skill (used for the asymmetry term)
INSERT INTO core.skill_similarity (from_skill_id, to_skill_id, method, weight, model_version)
SELECT DISTINCT child.skill_id, parent.skill_id, 'esco_broader', 1, 'ESCO v1.2.1'
FROM staging.esco_broader_skill_relations b
JOIN core.skills child  ON child.taxonomy  = 'esco' AND child.external_id  = b.concept_uri
JOIN core.skills parent ON parent.taxonomy = 'esco' AND parent.external_id = b.broader_uri
WHERE child.skill_id <> parent.skill_id
ON CONFLICT DO NOTHING;

ANALYZE;
