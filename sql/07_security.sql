-- =====================================================================
-- SkillBridge - 07_security.sql
-- Access control inside the DBMS:
--   * three roles with least privilege (GRANT / REVOKE)
--   * column-level privilege: learners can never read password hashes
--   * row-level security (RLS): a learner sees and edits only their own
--     skills, history, snapshots and roadmaps
--   * SECURITY DEFINER audit trigger: history cannot be forged by learners
-- The application identifies the learner per transaction with
--   SELECT set_config('skillbridge.user_id', '<id>', true);
-- Roles are NOLOGIN group roles; real login users would be members of them.
-- =====================================================================
SET search_path = core, staging, public;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skillbridge_readonly') THEN
        CREATE ROLE skillbridge_readonly NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skillbridge_learner') THEN
        CREATE ROLE skillbridge_learner NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skillbridge_admin') THEN
        CREATE ROLE skillbridge_admin NOLOGIN;
    END IF;
END $$;

-- Start from nothing (re-runnable)
REVOKE ALL ON ALL TABLES    IN SCHEMA core FROM skillbridge_readonly, skillbridge_learner, skillbridge_admin;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA core FROM skillbridge_readonly, skillbridge_learner, skillbridge_admin;
GRANT USAGE ON SCHEMA core TO skillbridge_readonly, skillbridge_learner, skillbridge_admin;

-- ---------------------------------------------------------------------
-- Read-only analyst: reference data and evidence, no personal data
-- ---------------------------------------------------------------------
GRANT SELECT ON core.careers, core.career_source_codes, core.skills, core.data_sources,
                core.career_skill_evidence, core.skill_aliases, core.skill_similarity,
                core.skill_prerequisites, core.learning_resources, core.resource_skills,
                core.model_parameters, core.mv_skill_lexicon,
                core.v_evidence_detail, core.v_career_skill_requirement,
                core.v_source_disagreement, core.v_target_careers
TO skillbridge_readonly;

-- ---------------------------------------------------------------------
-- Learner: reference data + own profile; cannot change evidence,
-- prerequisites, parameters or review extractions
-- ---------------------------------------------------------------------
GRANT skillbridge_readonly TO skillbridge_learner;
GRANT SELECT (user_id, full_name, email, role, weekly_hours, created_at) ON core.users TO skillbridge_learner;
GRANT UPDATE (full_name, weekly_hours) ON core.users TO skillbridge_learner;
GRANT SELECT, INSERT, UPDATE, DELETE ON core.user_skills TO skillbridge_learner;
GRANT SELECT ON core.user_skill_history TO skillbridge_learner;
GRANT SELECT, INSERT ON core.gap_snapshots, core.roadmaps, core.roadmap_items TO skillbridge_learner;
GRANT UPDATE (resource_id, hours, hours_source, week_start, week_end) ON core.roadmap_items
      TO skillbridge_learner;                     -- fn_assign_resources attaches courses and reschedules
GRANT UPDATE (total_hours, total_weeks) ON core.roadmaps TO skillbridge_learner;
GRANT USAGE ON SEQUENCE core.gap_snapshots_snapshot_id_seq, core.roadmaps_roadmap_id_seq TO skillbridge_learner;

-- ---------------------------------------------------------------------
-- Administrator: everything (curation, extraction review, parameters)
-- ---------------------------------------------------------------------
GRANT ALL ON ALL TABLES    IN SCHEMA core TO skillbridge_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA core TO skillbridge_admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA core TO skillbridge_admin, skillbridge_learner, skillbridge_readonly;

-- ---------------------------------------------------------------------
-- Row-level security
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.current_learner() RETURNS BIGINT
LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('skillbridge.user_id', TRUE), '')::BIGINT
$$;

ALTER TABLE core.users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.user_skills        ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.user_skill_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.gap_snapshots      ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.roadmaps           ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.roadmap_items      ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS own_user     ON core.users;
DROP POLICY IF EXISTS own_skills   ON core.user_skills;
DROP POLICY IF EXISTS own_history  ON core.user_skill_history;
DROP POLICY IF EXISTS own_snapshot ON core.gap_snapshots;
DROP POLICY IF EXISTS own_roadmap  ON core.roadmaps;
DROP POLICY IF EXISTS own_items    ON core.roadmap_items;
DROP POLICY IF EXISTS admin_all    ON core.users;
DROP POLICY IF EXISTS admin_all    ON core.user_skills;
DROP POLICY IF EXISTS admin_all    ON core.user_skill_history;
DROP POLICY IF EXISTS admin_all    ON core.gap_snapshots;
DROP POLICY IF EXISTS admin_all    ON core.roadmaps;
DROP POLICY IF EXISTS admin_all    ON core.roadmap_items;

CREATE POLICY own_user     ON core.users              TO skillbridge_learner
    USING (user_id = core.current_learner()) WITH CHECK (user_id = core.current_learner());
CREATE POLICY own_skills   ON core.user_skills        TO skillbridge_learner
    USING (user_id = core.current_learner()) WITH CHECK (user_id = core.current_learner());
CREATE POLICY own_history  ON core.user_skill_history TO skillbridge_learner
    USING (user_id = core.current_learner());
CREATE POLICY own_snapshot ON core.gap_snapshots      TO skillbridge_learner
    USING (user_id = core.current_learner()) WITH CHECK (user_id = core.current_learner());
CREATE POLICY own_roadmap  ON core.roadmaps           TO skillbridge_learner
    USING (user_id = core.current_learner()) WITH CHECK (user_id = core.current_learner());
CREATE POLICY own_items    ON core.roadmap_items      TO skillbridge_learner
    USING (EXISTS (SELECT 1 FROM core.roadmaps r WHERE r.roadmap_id = roadmap_items.roadmap_id
                   AND r.user_id = core.current_learner()))
    WITH CHECK (EXISTS (SELECT 1 FROM core.roadmaps r WHERE r.roadmap_id = roadmap_items.roadmap_id
                        AND r.user_id = core.current_learner()));

CREATE POLICY admin_all ON core.users              TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY admin_all ON core.user_skills        TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY admin_all ON core.user_skill_history TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY admin_all ON core.gap_snapshots      TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY admin_all ON core.roadmaps           TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY admin_all ON core.roadmap_items      TO skillbridge_admin USING (TRUE) WITH CHECK (TRUE);

-- Audit trigger runs with the owner's rights: learners have no INSERT on the
-- history table, so they cannot write or alter audit rows themselves.
ALTER FUNCTION core.trg_user_skill_history() SECURITY DEFINER SET search_path = core, public;
REVOKE ALL ON FUNCTION core.trg_user_skill_history() FROM PUBLIC;
