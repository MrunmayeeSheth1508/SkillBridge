-- =====================================================================
-- SkillBridge - 02_core_schema.sql
-- The relational model (3NF), schema `core`.
--
--   Module A  Core:            users, careers, skills, data_sources
--   Module B  Evidence/graph:  career_skill_evidence, skill_aliases,
--                              skill_similarity, skill_prerequisites
--   Module C  Learning:        user_skills, learning_resources, resource_skills
--   Module D  Tracking:        gap_snapshots, user_skill_history,
--                              extraction_candidates
--   Option B  Roadmaps:        roadmaps, roadmap_items
--
--   Supporting (not conceptual entities):
--     career_source_codes  external identifiers + ESCO-O*NET crosswalk links
--     model_parameters     tunable constants (priors, lambda, ...) used by SQL
--
-- Re-running this file DROPS the core schema. Curated data (prerequisites,
-- resources) must therefore live in CSV files under data/curated and be
-- re-loaded by script, which also keeps the project reproducible.
-- =====================================================================

DROP SCHEMA IF EXISTS core CASCADE;
CREATE SCHEMA core;

-- Make `core` the default schema for this database (pgAdmin, psql, Flask)
DO $$ BEGIN
  EXECUTE format('ALTER DATABASE %I SET search_path = core, staging, public', current_database());
END $$;
SET search_path = core, staging, public;

-- =====================================================================
-- Supporting: parameters
-- =====================================================================
CREATE TABLE core.model_parameters (
    param_name  TEXT PRIMARY KEY,
    param_value NUMERIC NOT NULL,
    description TEXT NOT NULL
);

CREATE FUNCTION core.param(p_name TEXT) RETURNS NUMERIC
LANGUAGE sql STABLE AS $$
    SELECT param_value FROM core.model_parameters WHERE param_name = p_name
$$;

-- =====================================================================
-- Module A - Core entities
-- =====================================================================
CREATE TABLE core.users (
    user_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%'),
    password_hash TEXT NOT NULL,                       -- Werkzeug hash, never plain text
    role          TEXT NOT NULL DEFAULT 'learner' CHECK (role IN ('learner', 'admin')),
    weekly_hours  NUMERIC(4,1) NOT NULL DEFAULT 8 CHECK (weekly_hours > 0 AND weekly_hours <= 80),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE core.data_sources (
    source_id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name    TEXT NOT NULL UNIQUE,
    source_type    TEXT NOT NULL CHECK (source_type IN ('taxonomy', 'job_postings', 'manual')),
    version        TEXT,
    url            TEXT,
    default_weight NUMERIC(3,2) NOT NULL CHECK (default_weight > 0 AND default_weight <= 1),
    description    TEXT
);

CREATE TABLE core.careers (
    career_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title            TEXT NOT NULL,
    description      TEXT,
    origin_source_id SMALLINT NOT NULL REFERENCES core.data_sources,
    origin_code      TEXT NOT NULL,            -- O*NET-SOC code or ESCO occupation URI
    domain           TEXT CHECK (domain IN ('Data & AI', 'Software engineering',
                                            'Mechanical & manufacturing engineering',
                                            'Business & finance analytics')),
    is_target        BOOLEAN NOT NULL DEFAULT FALSE,   -- offered to learners as a goal
    has_ratings      BOOLEAN NOT NULL DEFAULT FALSE,   -- O*NET: has scored skill ratings
    UNIQUE (origin_source_id, origin_code),
    CHECK (NOT is_target OR domain IS NOT NULL)
);
CREATE INDEX ON core.careers (domain) WHERE is_target;
CREATE INDEX ON core.careers (lower(title));

CREATE TABLE core.career_source_codes (
    career_id     BIGINT   NOT NULL REFERENCES core.careers ON DELETE CASCADE,
    source_id     SMALLINT NOT NULL REFERENCES core.data_sources,
    external_code TEXT     NOT NULL,
    match_type    TEXT     NOT NULL CHECK (match_type IN
                    ('native', 'crosswalk_exact', 'crosswalk_broad', 'crosswalk_narrow', 'crosswalk_close')),
    PRIMARY KEY (career_id, source_id, external_code)
);
CREATE INDEX ON core.career_source_codes (source_id, external_code);

CREATE TABLE core.skills (
    skill_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name              TEXT NOT NULL,
    description       TEXT,
    taxonomy          TEXT NOT NULL CHECK (taxonomy IN
                        ('onet_skill', 'onet_knowledge', 'onet_work_activity', 'onet_technology', 'esco')),
    skill_type        TEXT NOT NULL CHECK (skill_type IN ('skill', 'knowledge', 'work_activity', 'technology')),
    external_id       TEXT NOT NULL,           -- O*NET element ID, tool name, or ESCO URI
    reuse_level       TEXT CHECK (reuse_level IN
                        ('transversal', 'cross-sector', 'sector-specific', 'occupation-specific')),
    is_hot_technology BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (taxonomy, external_id)
);
CREATE INDEX ON core.skills (lower(name));
-- An `embedding vector(384)` column + HNSW index is added in the transfer phase,
-- once pgvector is installed.

-- =====================================================================
-- Module B - Evidence and skill relationships
-- =====================================================================
CREATE TABLE core.career_skill_evidence (
    evidence_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    career_id        BIGINT   NOT NULL REFERENCES core.careers ON DELETE CASCADE,
    skill_id         BIGINT   NOT NULL REFERENCES core.skills  ON DELETE CASCADE,
    source_id        SMALLINT NOT NULL REFERENCES core.data_sources,
    importance_raw   NUMERIC,                  -- as published (O*NET IM 1-5); NULL for ESCO
    level_raw        NUMERIC,                  -- O*NET LV 0-7
    importance       NUMERIC(5,4) NOT NULL CHECK (importance >= 0 AND importance <= 1),
    level_norm       NUMERIC(5,4)          CHECK (level_norm >= 0 AND level_norm <= 1),
    requirement_type TEXT NOT NULL CHECK (requirement_type IN ('scored', 'essential', 'optional', 'present')),
    confidence       NUMERIC(3,2) NOT NULL CHECK (confidence > 0 AND confidence <= 1),
    source_record    TEXT NOT NULL,            -- where exactly the evidence came from
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (career_id, skill_id, source_id)
);
CREATE INDEX ON core.career_skill_evidence (skill_id);
CREATE INDEX ON core.career_skill_evidence (source_id);

CREATE TABLE core.skill_aliases (
    alias_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    skill_id   BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    alias      TEXT   NOT NULL CHECK (length(trim(alias)) > 0),
    alias_type TEXT   NOT NULL CHECK (alias_type IN ('preferred', 'alternative', 'hidden', 'manual')),
    UNIQUE (skill_id, alias)
);
CREATE INDEX ON core.skill_aliases (lower(alias));

-- Directional: a row (from, to) says nothing about (to, from).
CREATE TABLE core.skill_similarity (
    from_skill_id BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    to_skill_id   BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    method        TEXT   NOT NULL,   -- exact_label, esco_relation, esco_broader, embedding, transfer
    weight        NUMERIC(5,4) NOT NULL CHECK (weight >= 0 AND weight <= 1),
    model_version TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (from_skill_id, to_skill_id, method),
    CHECK (from_skill_id <> to_skill_id)
);
CREATE INDEX ON core.skill_similarity (to_skill_id, method);

-- Row (skill_id, prereq_skill_id): prereq must be learned BEFORE skill.
CREATE TABLE core.skill_prerequisites (
    skill_id        BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    prereq_skill_id BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    created_by      BIGINT REFERENCES core.users,
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (skill_id, prereq_skill_id),
    CHECK (skill_id <> prereq_skill_id)                 -- no self-dependency
);
CREATE INDEX ON core.skill_prerequisites (prereq_skill_id);

-- Cycle guard (Contribution 3). The advisory lock serialises prerequisite
-- writes so two concurrent inserts cannot each pass the check and together
-- close a cycle.
-- Planner settings (RQ3 finding): with default settings PostgreSQL either builds a
-- hash over the whole edge table, or - when statistics say the table is small -
-- seq-scans it, on EVERY recursion step. Both make one insert O(n^2) in the path
-- length. Inside this function only, hash/merge joins and seq scans are disabled,
-- forcing an index-driven nested loop on the primary key (O(n log n)):
-- 2,000-edge chain: 745 ms -> ~3 ms per insert.
CREATE FUNCTION core.trg_prerequisite_no_cycle() RETURNS trigger
LANGUAGE plpgsql
SET enable_hashjoin = off
SET enable_mergejoin = off
SET enable_seqscan = off
AS $$
DECLARE
    v_cycle BOOLEAN;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('core.skill_prerequisites'));

    -- Adding "P before S" closes a cycle if S is already (transitively)
    -- a prerequisite of P. Walk P's prerequisite chain looking for S.
    WITH RECURSIVE chain(id) AS (
        SELECT p.prereq_skill_id
        FROM core.skill_prerequisites p
        WHERE p.skill_id = NEW.prereq_skill_id
          AND NOT (TG_OP = 'UPDATE' AND p.skill_id = OLD.skill_id
                                    AND p.prereq_skill_id = OLD.prereq_skill_id)
        UNION                                   -- UNION (not ALL): each node once
        SELECT p.prereq_skill_id
        FROM core.skill_prerequisites p
        JOIN chain c ON p.skill_id = c.id
        WHERE NOT (TG_OP = 'UPDATE' AND p.skill_id = OLD.skill_id
                                    AND p.prereq_skill_id = OLD.prereq_skill_id)
    )
    SELECT EXISTS (SELECT 1 FROM chain WHERE id = NEW.skill_id) INTO v_cycle;

    IF v_cycle THEN
        RAISE EXCEPTION 'Prerequisite rejected: skill % before skill % would create a cycle',
            NEW.prereq_skill_id, NEW.skill_id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER prerequisite_no_cycle
BEFORE INSERT OR UPDATE ON core.skill_prerequisites
FOR EACH ROW EXECUTE FUNCTION core.trg_prerequisite_no_cycle();

-- =====================================================================
-- Module C - Learner and learning resources
-- =====================================================================
CREATE TABLE core.user_skills (
    user_id     BIGINT NOT NULL REFERENCES core.users  ON DELETE CASCADE,
    skill_id    BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    proficiency NUMERIC(3,2) NOT NULL CHECK (proficiency >= 0 AND proficiency <= 1),
    origin      TEXT NOT NULL DEFAULT 'self' CHECK (origin IN ('self', 'assessment', 'extracted')),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE core.learning_resources (
    resource_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title         TEXT NOT NULL,
    provider      TEXT,
    url           TEXT UNIQUE,
    resource_type TEXT NOT NULL CHECK (resource_type IN ('course', 'book', 'tutorial', 'project', 'video', 'certification')),
    effort_hours  NUMERIC(6,1) NOT NULL CHECK (effort_hours > 0),
    difficulty    TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    is_free       BOOLEAN,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE core.resource_skills (
    resource_id BIGINT NOT NULL REFERENCES core.learning_resources ON DELETE CASCADE,
    skill_id    BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    coverage    NUMERIC(3,2) NOT NULL DEFAULT 1 CHECK (coverage > 0 AND coverage <= 1),
    PRIMARY KEY (resource_id, skill_id)
);
CREATE INDEX ON core.resource_skills (skill_id);

-- =====================================================================
-- Module D - Tracking and review
-- =====================================================================
CREATE TABLE core.gap_snapshots (
    snapshot_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES core.users   ON DELETE CASCADE,
    career_id    BIGINT NOT NULL REFERENCES core.careers ON DELETE CASCADE,
    use_transfer BOOLEAN NOT NULL,
    readiness    NUMERIC(5,4) NOT NULL CHECK (readiness >= 0 AND readiness <= 1),
    parameters   JSONB NOT NULL,       -- lambda, weights ... used for this run
    details      JSONB NOT NULL,       -- per-skill gaps + explanations
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON core.gap_snapshots (user_id, career_id, created_at DESC);

CREATE TABLE core.user_skill_history (
    history_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES core.users  ON DELETE CASCADE,
    skill_id        BIGINT NOT NULL REFERENCES core.skills ON DELETE CASCADE,
    old_proficiency NUMERIC(3,2),
    new_proficiency NUMERIC(3,2),
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON core.user_skill_history (user_id, skill_id, changed_at);

CREATE FUNCTION core.trg_user_skill_history() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO core.user_skill_history (user_id, skill_id, old_proficiency, new_proficiency)
        VALUES (OLD.user_id, OLD.skill_id, OLD.proficiency, NULL);
        RETURN OLD;
    ELSIF TG_OP = 'INSERT' OR NEW.proficiency IS DISTINCT FROM OLD.proficiency THEN
        INSERT INTO core.user_skill_history (user_id, skill_id, old_proficiency, new_proficiency)
        VALUES (NEW.user_id, NEW.skill_id,
                CASE WHEN TG_OP = 'UPDATE' THEN OLD.proficiency END, NEW.proficiency);
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER user_skill_history
AFTER INSERT OR UPDATE OR DELETE ON core.user_skills
FOR EACH ROW EXECUTE FUNCTION core.trg_user_skill_history();

CREATE TABLE core.extraction_candidates (
    candidate_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    career_id        BIGINT REFERENCES core.careers ON DELETE CASCADE,
    source_text      TEXT NOT NULL,          -- the job-description sentence
    span_text        TEXT NOT NULL,          -- the extracted skill mention
    matched_skill_id BIGINT REFERENCES core.skills,
    match_score      NUMERIC(5,4) CHECK (match_score >= 0 AND match_score <= 1),
    status           TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewer_id      BIGINT REFERENCES core.users,
    reviewed_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK ((status = 'pending') = (reviewed_at IS NULL)),
    CHECK (status <> 'approved' OR matched_skill_id IS NOT NULL)
);
CREATE INDEX ON core.extraction_candidates (status);

-- =====================================================================
-- Option B - Roadmaps
-- =====================================================================
CREATE TABLE core.roadmaps (
    roadmap_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES core.users   ON DELETE CASCADE,
    career_id    BIGINT NOT NULL REFERENCES core.careers ON DELETE CASCADE,
    snapshot_id  BIGINT REFERENCES core.gap_snapshots ON DELETE SET NULL,
    weekly_hours NUMERIC(4,1) NOT NULL CHECK (weekly_hours > 0 AND weekly_hours <= 80),
    total_hours  NUMERIC(7,1) NOT NULL CHECK (total_hours >= 0),
    total_weeks  INTEGER      NOT NULL CHECK (total_weeks >= 0),
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE core.roadmap_items (
    roadmap_id  BIGINT  NOT NULL REFERENCES core.roadmaps ON DELETE CASCADE,
    item_no     INTEGER NOT NULL CHECK (item_no > 0),
    skill_id    BIGINT  NOT NULL REFERENCES core.skills,
    resource_id BIGINT  REFERENCES core.learning_resources,
    layer       INTEGER NOT NULL CHECK (layer > 0),      -- topological layer
    week_start  INTEGER NOT NULL CHECK (week_start > 0),
    week_end    INTEGER NOT NULL,
    hours       NUMERIC(6,1) NOT NULL CHECK (hours >= 0),
    PRIMARY KEY (roadmap_id, item_no),
    CHECK (week_end >= week_start)
);
