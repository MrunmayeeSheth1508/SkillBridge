-- =====================================================================
-- SkillBridge - 01_staging_schema.sql
-- Staging layer: raw copies of the source files, loaded as-is.
--
-- Design rules
--   * Every data column is TEXT. Values are kept exactly as in the source
--     file; casting, cleaning and de-duplication happen in the transform
--     step (02_*), where failures can be reported instead of aborting a load.
--   * Each table records which file a row came from and when it was loaded.
--   * These tables are NOT part of the 13-entity ER model. They are the
--     import and validation area described in Phase 2.
--   * Re-runnable: the whole schema is dropped and recreated.
-- =====================================================================

DROP SCHEMA IF EXISTS staging CASCADE;
CREATE SCHEMA staging;

-- ---------------------------------------------------------------------
-- Load log: one row per file loaded
-- ---------------------------------------------------------------------
CREATE TABLE staging.load_log (
    load_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name   TEXT        NOT NULL,
    source_file  TEXT        NOT NULL,
    rows_in_file INTEGER     NOT NULL,
    rows_loaded  INTEGER     NOT NULL,
    loaded_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- O*NET
-- =====================================================================

-- occupation_data_dbms.csv  (1,016 occupations)
CREATE TABLE staging.onet_occupations (
    onet_soc_code TEXT,
    title         TEXT,
    description   TEXT,
    source_file   TEXT NOT NULL,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One table for every O*NET file that uses the Importance/Level rating
-- structure. `category` says which file the row came from:
--   skill_basic            essential_skills_dbms.csv     (10 Basic Skills, 2.A.*)
--   skill_cross_functional transferable_skills_dbms.csv  (25 Cross-Functional Skills, 2.B.*)
--   knowledge              knowledge_dbms.csv            (33 Knowledge areas, 2.C.*)
--   work_activity          work_activities_dbms.csv      (41 Work Activities, 4.A.*)
CREATE TABLE staging.onet_ratings (
    category           TEXT NOT NULL,
    onet_soc_code      TEXT,
    title              TEXT,
    element_id         TEXT,
    element_name       TEXT,
    scale_id           TEXT,
    scale_name         TEXT,
    data_value         TEXT,
    n                  TEXT,
    standard_error     TEXT,
    lower_ci_bound     TEXT,
    upper_ci_bound     TEXT,
    recommend_suppress TEXT,
    not_relevant       TEXT,
    date_text          TEXT,
    domain_source      TEXT,
    source_file        TEXT NOT NULL,
    loaded_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- software_skills_dbms.csv = O*NET Technology Skills (no importance scores)
CREATE TABLE staging.onet_technology_skills (
    onet_soc_code     TEXT,
    title             TEXT,
    workplace_example TEXT,   -- the actual tool, e.g. "Python", "Atlassian JIRA"
    element_id        TEXT,   -- commodity category, e.g. 2.E.5.b
    element_name      TEXT,   -- e.g. "Document management software"
    hot_technology    TEXT,   -- Y/N
    in_demand         TEXT,   -- Y/N
    source_file       TEXT NOT NULL,
    loaded_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- job_titles_csv.csv = O*NET Alternate Titles
CREATE TABLE staging.onet_alternate_titles (
    onet_soc_code TEXT,
    title         TEXT,
    job_title     TEXT,
    short_title   TEXT,
    sources       TEXT,
    source_file   TEXT NOT NULL,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- scales_reference_dbms.csv
CREATE TABLE staging.onet_scales (
    scale_id    TEXT,
    scale_name  TEXT,
    minimum     TEXT,
    maximum     TEXT,
    source_file TEXT NOT NULL,
    loaded_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- content_model_reference_dbms.csv (was inside the ESCO zip)
-- Gives a text description for every O*NET element -> used for embeddings.
CREATE TABLE staging.onet_content_model (
    element_id   TEXT,
    element_name TEXT,
    description  TEXT,
    source_file  TEXT NOT NULL,
    loaded_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- ESCO v1.2.1
-- =====================================================================

CREATE TABLE staging.esco_occupations (
    concept_type              TEXT,
    concept_uri               TEXT,
    isco_group                TEXT,
    preferred_label           TEXT,
    alt_labels                TEXT,   -- newline-separated list
    hidden_labels             TEXT,
    status                    TEXT,
    modified_date             TEXT,
    regulated_profession_note TEXT,
    scope_note                TEXT,
    definition                TEXT,
    in_scheme                 TEXT,
    description               TEXT,
    code                      TEXT,
    nace_code                 TEXT,
    source_file               TEXT NOT NULL,
    loaded_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staging.esco_skills (
    concept_type    TEXT,
    concept_uri     TEXT,
    skill_type      TEXT,   -- 'skill/competence' or 'knowledge'
    reuse_level     TEXT,   -- transversal / cross-sector / sector-specific / occupation-specific
    preferred_label TEXT,
    alt_labels      TEXT,   -- newline-separated list
    hidden_labels   TEXT,
    status          TEXT,
    modified_date   TEXT,
    scope_note      TEXT,
    definition      TEXT,
    in_scheme       TEXT,
    description     TEXT,
    source_file     TEXT NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staging.esco_occupation_skill_relations (
    occupation_uri   TEXT,
    occupation_label TEXT,
    relation_type    TEXT,   -- 'essential' or 'optional'
    skill_type       TEXT,
    skill_uri        TEXT,
    skill_label      TEXT,
    source_file      TEXT NOT NULL,
    loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staging.esco_skill_skill_relations (
    original_skill_uri  TEXT,
    original_skill_type TEXT,
    relation_type       TEXT,
    related_skill_type  TEXT,
    related_skill_uri   TEXT,
    source_file         TEXT NOT NULL,
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- broaderRelationsSkillPillar_en.csv: child -> parent links (skills and skill groups)
CREATE TABLE staging.esco_broader_skill_relations (
    concept_type  TEXT,
    concept_uri   TEXT,
    concept_label TEXT,
    broader_type  TEXT,
    broader_uri   TEXT,
    broader_label TEXT,
    source_file   TEXT NOT NULL,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- broaderRelationsOccPillar_en.csv: occupation -> parent occupation / ISCO group
CREATE TABLE staging.esco_broader_occupation_relations (
    concept_type  TEXT,
    concept_uri   TEXT,
    concept_label TEXT,
    broader_type  TEXT,
    broader_uri   TEXT,
    broader_label TEXT,
    source_file   TEXT NOT NULL,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staging.esco_skill_groups (
    concept_type    TEXT,
    concept_uri     TEXT,
    preferred_label TEXT,
    alt_labels      TEXT,
    hidden_labels   TEXT,
    status          TEXT,
    modified_date   TEXT,
    scope_note      TEXT,
    in_scheme       TEXT,
    description     TEXT,
    code            TEXT,
    source_file     TEXT NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staging.esco_isco_groups (
    concept_type    TEXT,
    concept_uri     TEXT,
    code            TEXT,
    preferred_label TEXT,
    status          TEXT,
    alt_labels      TEXT,
    in_scheme       TEXT,
    description     TEXT,
    source_file     TEXT NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Collections: membership flags (digital, transversal, green, research, language, digcomp)
CREATE TABLE staging.esco_skill_collections (
    collection          TEXT NOT NULL,
    concept_uri         TEXT,
    preferred_label     TEXT,
    skill_type          TEXT,
    reuse_level         TEXT,
    broader_concept_uri TEXT,
    broader_concept_pt  TEXT,
    source_file         TEXT NOT NULL,
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- SkillSpan (train / dev / test)
-- Stored for traceability and for joining extraction results later.
-- Model training reads the JSON files directly.
-- =====================================================================
CREATE TABLE staging.skillspan_sentences (
    split          TEXT NOT NULL,   -- train / dev / test
    idx            TEXT,
    source         TEXT,            -- e.g. 'tech', 'house'
    tokens         JSONB,
    tags_skill     JSONB,
    tags_knowledge JSONB,
    source_file    TEXT NOT NULL,
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
