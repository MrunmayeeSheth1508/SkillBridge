-- =====================================================================
-- SkillBridge - DEMO SCRIPT for pgAdmin
-- Open in Query Tool on the `skillbridge` database. Select ONE block and
-- press F5 (Execute selection) to run it. Blocks follow the story:
--   A  The database        B  Contribution 1: evidence & provenance
--   C  Contribution 2: directional transfer & gap analysis
--   D  Contribution 3: prerequisite integrity & roadmap
--   E  History & tracking
-- =====================================================================
SET search_path = core, staging, public;

-- ---------------------------------------------------------------------
-- A1. What is in the database? (row counts of the 3NF model)
-- ---------------------------------------------------------------------
SELECT relname AS table_name, n_live_tup AS rows
FROM pg_stat_user_tables WHERE schemaname = 'core' ORDER BY n_live_tup DESC;

-- A2. Data sources and their weights
SELECT source_name, source_type, version, default_weight, description FROM data_sources;

-- A3. Constraints that protect the data (CHECK, UNIQUE, FK) on the evidence table
SELECT conname AS constraint_name, pg_get_constraintdef(oid) AS definition
FROM pg_constraint WHERE conrelid = 'core.career_skill_evidence'::regclass ORDER BY contype;

-- ---------------------------------------------------------------------
-- B1. Contribution 1 - every requirement keeps its source (provenance)
-- ---------------------------------------------------------------------
SELECT skill, source, requirement_type, importance_raw, importance, level_norm, confidence, source_record
FROM v_evidence_detail
WHERE career = 'Data Scientists' AND requirement_type = 'scored' AND skill_type = 'skill'
ORDER BY importance DESC LIMIT 15;

-- B2. Tools required, with Hot Technology / In Demand provenance
SELECT skill, importance, confidence, source_record
FROM v_evidence_detail
WHERE career = 'Data Scientists' AND skill_type = 'technology'
ORDER BY importance DESC, skill LIMIT 15;

-- B3. Aggregated importance computed at query time (records never overwritten)
SELECT k.name AS skill, r.importance, r.n_sources, r.sources, r.disagreement
FROM v_career_skill_requirement r
JOIN skills k USING (skill_id)
JOIN careers c USING (career_id)
WHERE c.title = 'Data Scientists'
ORDER BY r.importance DESC LIMIT 10;

-- B4. Same career in two taxonomies (ESCO vs O*NET vocabulary sizes)
SELECT taxonomy, skill_type, COUNT(*) AS skills FROM skills GROUP BY 1, 2 ORDER BY 1, 2;

-- ---------------------------------------------------------------------
-- C1. Contribution 2 - transfer is DIRECTIONAL: T(a->b) <> T(b->a)
-- ---------------------------------------------------------------------
SELECT a.name AS from_skill, b.name AS to_skill,
       s1.weight AS t_forward, s2.weight AS t_reverse,
       ROUND(s1.weight - s2.weight, 4) AS asymmetry
FROM skill_similarity s1
JOIN skill_similarity s2 ON s2.from_skill_id = s1.to_skill_id
                        AND s2.to_skill_id   = s1.from_skill_id
                        AND s2.method        = s1.method
JOIN skills a ON a.skill_id = s1.from_skill_id
JOIN skills b ON b.skill_id = s1.to_skill_id
WHERE s1.method = 'transfer_v0' AND s1.from_skill_id < s1.to_skill_id
ORDER BY ABS(s1.weight - s2.weight) DESC LIMIT 15;

-- C2. The demo learner's current profile
SELECT k.name, k.skill_type, us.proficiency
FROM user_skills us JOIN skills k USING (skill_id)
JOIN users u USING (user_id)
WHERE u.email = 'demo@skillbridge.local' ORDER BY us.proficiency DESC;

-- C3. Gap analysis WITH transfer credit, fully explained, computed in SQL
SELECT skill, skill_type, importance, own_proficiency AS own,
       transfer_from, transfer_weight AS t, transfer_credit AS credit,
       effective_proficiency AS p_eff, gap
FROM fn_gap_analysis(
       (SELECT user_id FROM users WHERE email = 'demo@skillbridge.local'),
       (SELECT career_id FROM careers WHERE title = 'Data Scientists'),
       TRUE)
ORDER BY gap DESC LIMIT 15;

-- C4. Ablation: readiness without vs with transfer credit, every target career
SELECT c.domain, c.title,
       fn_readiness(u.user_id, c.career_id, FALSE) AS baseline,
       fn_readiness(u.user_id, c.career_id, TRUE)  AS transfer_aware,
       ROUND(fn_readiness(u.user_id, c.career_id, TRUE)
           - fn_readiness(u.user_id, c.career_id, FALSE), 4) AS lift
FROM careers c CROSS JOIN (SELECT user_id FROM users WHERE email = 'demo@skillbridge.local') u
WHERE c.is_target
ORDER BY transfer_aware DESC;

-- ---------------------------------------------------------------------
-- D1. Contribution 3 - the curated prerequisite graph
-- ---------------------------------------------------------------------
SELECT pk.name AS learn_first, k.name AS then_learn, p.note
FROM skill_prerequisites p
JOIN skills k  ON k.skill_id  = p.skill_id
JOIN skills pk ON pk.skill_id = p.prereq_skill_id
ORDER BY pk.name;

-- D2. The database REJECTS a self-dependency  (expected: ERROR, check constraint)
INSERT INTO skill_prerequisites (skill_id, prereq_skill_id)
SELECT skill_id, skill_id FROM skills WHERE name = 'Python' AND taxonomy = 'onet_technology';

-- D3. The database REJECTS a cycle  (expected: ERROR "would create a cycle")
--     Existing chain: Python -> NumPy -> pandas -> Scikit-learn. Try Scikit-learn before Python:
INSERT INTO skill_prerequisites (skill_id, prereq_skill_id)
SELECT p.skill_id, s.skill_id
FROM skills p, skills s
WHERE p.name = 'Python' AND p.taxonomy = 'onet_technology'
  AND s.name = 'Scikit-learn' AND s.taxonomy = 'onet_technology';

-- D4. Build a prerequisite-valid roadmap at 8 hours/week (stored in roadmaps + roadmap_items)
SELECT fn_build_roadmap(
         (SELECT user_id FROM users WHERE email = 'demo@skillbridge.local'),
         (SELECT career_id FROM careers WHERE title = 'Data Scientists'),
         8, TRUE) AS new_roadmap_id;

-- D5. Show the latest roadmap, layer by layer
SELECT ri.item_no, ri.layer, k.name AS skill, ri.hours, ri.week_start, ri.week_end
FROM roadmap_items ri JOIN skills k USING (skill_id)
WHERE ri.roadmap_id = (SELECT MAX(roadmap_id) FROM roadmaps)
ORDER BY ri.item_no;

-- D6. Verify: prerequisite violations in that roadmap (expected: 0)
SELECT roadmap_id, total_hours, total_weeks, fn_roadmap_violations(roadmap_id) AS violations
FROM roadmaps WHERE roadmap_id = (SELECT MAX(roadmap_id) FROM roadmaps);

-- D7. Ablation, step 1: build the same roadmap with and without transfer credit
SELECT fn_build_roadmap(u.user_id, c.career_id, 8, TRUE)  AS with_transfer_id,
       fn_build_roadmap(u.user_id, c.career_id, 8, FALSE) AS without_transfer_id
FROM (SELECT user_id FROM users WHERE email = 'demo@skillbridge.local') u,
     (SELECT career_id FROM careers WHERE title = 'Data Scientists') c;

-- D8. Ablation, step 2: compare them (run after D7)
SELECT CASE WHEN s.use_transfer THEN 'with transfer' ELSE 'without transfer' END AS variant,
       s.readiness, r.total_hours, r.total_weeks,
       (SELECT COUNT(*) FROM roadmap_items i WHERE i.roadmap_id = r.roadmap_id) AS steps,
       fn_roadmap_violations(r.roadmap_id) AS violations
FROM roadmaps r JOIN gap_snapshots s USING (snapshot_id)
ORDER BY r.roadmap_id DESC LIMIT 2;

-- ---------------------------------------------------------------------
-- E1. Trigger-maintained proficiency history (change a slider in the dashboard first)
-- ---------------------------------------------------------------------
SELECT k.name, h.old_proficiency, h.new_proficiency, h.changed_at
FROM user_skill_history h JOIN skills k USING (skill_id)
ORDER BY h.changed_at DESC LIMIT 15;

-- E2. Readiness snapshots over time (saved each time a roadmap is generated)
SELECT c.title, s.use_transfer, s.readiness, s.created_at
FROM gap_snapshots s JOIN careers c USING (career_id)
ORDER BY s.created_at DESC LIMIT 10;

-- E3. Model parameters used by every calculation (change one, re-run C4)
SELECT param_name, param_value, description FROM model_parameters ORDER BY param_name;

-- ---------------------------------------------------------------------
-- F1. NLP - extract skills from a job description, inside PostgreSQL
-- ---------------------------------------------------------------------
SELECT span_text, skill, skill_type, taxonomy, method, score
FROM fn_extract_from_text(
  'We need a data scientist with Python, SQL and scikit-learn. Strong mathematics and
   critical-thinking; experience with pandas and Apache Spark. Excel is a plus.');

-- F2. Fuzzy matching (pg_trgm) catches spelling variants and typos
SELECT span_text, skill, method, score
FROM fn_extract_from_text('Needs complex problem-solvng and judgement and decision making.');

-- F3. The lexicon is a materialized view with B-tree + trigram (GIN) indexes
SELECT taxonomy, case_sensitive, COUNT(*) AS labels FROM mv_skill_lexicon GROUP BY 1, 2 ORDER BY 1, 2;
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'mv_skill_lexicon';

-- F4. Submit a posting for Data Scientists -> candidates stored as 'pending'
SELECT fn_submit_job_posting((SELECT career_id FROM careers WHERE title = 'Data Scientists'),
       'Data scientist: Python, SQL, PyTorch and Tableau. Strong mathematics.') AS batch_id;
SELECT candidate_id, span_text, method, match_score, status
FROM extraction_candidates ORDER BY candidate_id DESC LIMIT 10;

-- F5. Approve every pending exact match (the TRIGGER turns them into evidence)
SELECT candidate_id, fn_review_candidate(candidate_id,
         (SELECT user_id FROM users WHERE role = 'admin' LIMIT 1), TRUE) AS new_status
FROM extraction_candidates WHERE status = 'pending' AND method = 'exact';

-- F6. Contribution 1 now has several sources per skill - and they disagree
SELECT career, skill, importance, n_sources, sources, disagreement
FROM v_source_disagreement WHERE career = 'Data Scientists' ORDER BY disagreement DESC;

-- ---------------------------------------------------------------------
-- G. Security - each block starts a learner session; run ROLLBACK after it
-- ---------------------------------------------------------------------
-- G1. Row-level security: as the demo learner, only own rows are visible
--     (the table holds 2 learners' skills; select all 4 lines, F5, then run ROLLBACK)
BEGIN;
SELECT set_config('skillbridge.user_id', (SELECT user_id::text FROM core.users WHERE email = 'demo@skillbridge.local'), true);
SET LOCAL ROLE skillbridge_learner;
SELECT user_id, COUNT(*) AS skills FROM core.user_skills GROUP BY user_id;

ROLLBACK;

-- G2. Column privilege: password hashes are invisible to learners
--     (expected: ERROR permission denied; then run ROLLBACK)
BEGIN;
SET LOCAL ROLE skillbridge_learner;
SELECT password_hash FROM core.users;

ROLLBACK;

-- G3. Learners cannot change evidence  (expected: ERROR permission denied; then ROLLBACK)
BEGIN;
SET LOCAL ROLE skillbridge_learner;
DELETE FROM core.career_skill_evidence;

ROLLBACK;

-- G4. Policies and grants defined in the database
SELECT tablename, policyname, roles, cmd, qual FROM pg_policies WHERE schemaname = 'core' ORDER BY 1, 2;
SELECT grantee, table_name, string_agg(privilege_type, ', ') AS privileges
FROM information_schema.role_table_grants
WHERE table_schema = 'core' AND grantee LIKE 'skillbridge%'
GROUP BY 1, 2 ORDER BY 1, 2;
