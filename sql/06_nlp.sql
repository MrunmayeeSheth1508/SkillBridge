-- =====================================================================
-- SkillBridge - 06_nlp.sql
-- Job-description skill extraction, implemented inside PostgreSQL.
--
--   1. Lexicon   : materialized view over SKILL_ALIASES (~100k labels)
--                  + derived tool aliases ("Structured query language SQL" -> "SQL")
--   2. Matching  : n-grams (1-6 tokens) of the text, matched
--                    exact  -> B-tree on the normalised alias
--                    fuzzy  -> pg_trgm trigram similarity (GIN index)
--                  overlapping matches resolved longest-first
--   3. Review    : candidates stored in EXTRACTION_CANDIDATES as 'pending';
--                  a trigger turns approved candidates into
--                  CAREER_SKILL_EVIDENCE rows from the 'Job postings' source
-- Evaluated against SkillSpan by scripts/evaluate_extraction.py.
-- =====================================================================
SET search_path = core, staging, public;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ---------------------------------------------------------------------
-- Schema additions for the extraction workflow
-- ---------------------------------------------------------------------
ALTER TABLE core.skill_aliases DROP CONSTRAINT IF EXISTS skill_aliases_alias_type_check;
ALTER TABLE core.skill_aliases ADD CONSTRAINT skill_aliases_alias_type_check
    CHECK (alias_type IN ('preferred', 'alternative', 'hidden', 'manual', 'derived'));

ALTER TABLE core.extraction_candidates
    ADD COLUMN IF NOT EXISTS batch_id   BIGINT,                 -- one submitted job posting
    ADD COLUMN IF NOT EXISTS method     TEXT CHECK (method IN ('exact', 'fuzzy')),
    ADD COLUMN IF NOT EXISTS span_start INTEGER,
    ADD COLUMN IF NOT EXISTS span_end   INTEGER;
CREATE INDEX IF NOT EXISTS extraction_candidates_batch ON core.extraction_candidates (batch_id);
CREATE INDEX IF NOT EXISTS extraction_candidates_career_skill
    ON core.extraction_candidates (career_id, matched_skill_id) WHERE status = 'approved';
CREATE SEQUENCE IF NOT EXISTS core.job_posting_batch_seq;

INSERT INTO core.model_parameters (param_name, param_value, description) VALUES
 ('nlp_min_similarity', 0.80, 'Minimum trigram similarity for a fuzzy skill match')
ON CONFLICT (param_name) DO NOTHING;

-- ---------------------------------------------------------------------
-- Text normalisation
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_stopwords() RETURNS TEXT[]
LANGUAGE sql IMMUTABLE AS $$
    SELECT ARRAY['a','an','the','and','or','of','in','on','for','to','with','at','by','from','as',
                 'is','are','be','been','will','would','can','could','should','must','may',
                 'you','we','our','your','their','they','this','that','these','those','it','its',
                 'etc','eg','e.g','ie','i.e','including','such','using','use','used','within',
                 'experience','experienced','knowledge','skill','skills','ability','able',
                 'strong','good','excellent','solid','proven','plus','preferred','required',
                 'work','working','job','role','team','candidate','years','year','new','other',
                 'all','any','some','more','most','well','also','into','across','over','per',
                 'have','has','had','not','no','but','if','than','then','who','what','which']
$$;

-- one token -> lower case, punctuation stripped at both ends (keeps c++, c#, node.js)
CREATE OR REPLACE FUNCTION core.fn_norm_token(t TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT regexp_replace(lower(t), '^[^a-z0-9]+|[^a-z0-9+#]+$', '', 'g')
$$;

-- one token -> punctuation stripped, original case kept (for case-sensitive aliases)
CREATE OR REPLACE FUNCTION core.fn_cased_token(t TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT regexp_replace(t, '^[^A-Za-z0-9]+|[^A-Za-z0-9+#]+$', '', 'g')
$$;

-- whole phrase -> normalised tokens joined by single spaces
CREATE OR REPLACE FUNCTION core.fn_norm(p TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT COALESCE(string_agg(n, ' ' ORDER BY i), '')
    FROM (SELECT i, core.fn_norm_token(t) AS n
          FROM regexp_split_to_table(regexp_replace(p, '[-/]', ' ', 'g'), '\s+') WITH ORDINALITY x(t, i)) s
    WHERE n <> ''
$$;

CREATE OR REPLACE FUNCTION core.fn_cased(p TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT COALESCE(string_agg(n, ' ' ORDER BY i), '')
    FROM (SELECT i, core.fn_cased_token(t) AS n
          FROM regexp_split_to_table(regexp_replace(p, '[-/]', ' ', 'g'), '\s+') WITH ORDINALITY x(t, i)) s
    WHERE n <> ''
$$;

-- Split raw text into tokens; punctuation becomes its own token, newlines become '¶'
CREATE OR REPLACE FUNCTION core.fn_tokenize(p_text TEXT) RETURNS TEXT[]
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT COALESCE(array_remove(regexp_split_to_array(btrim(
             regexp_replace(
               regexp_replace(
                 regexp_replace(p_text, E'\\r?\\n', ' ¶ ', 'g'),
               '([/,;:()\[\]!?"])', ' \1 ', 'g'),
             '\s+', ' ', 'g')), ' '), ''), ARRAY[]::TEXT[])
$$;

-- ---------------------------------------------------------------------
-- Derived aliases for O*NET technology names
--   "Structured query language SQL" -> SQL        (trailing acronym)
--   "Microsoft Excel"               -> Excel      (vendor removed)
--   "Amazon Web Services AWS software" -> AWS
-- Derived aliases are matched case-sensitively ("Excel", not "excel").
-- ---------------------------------------------------------------------
WITH base AS (
    SELECT skill_id, regexp_replace(name, '\s+software$', '', 'i') AS nm
    FROM core.skills WHERE taxonomy = 'onet_technology'
),
cand AS (
    SELECT skill_id, substring(nm FROM '\s([A-Z][A-Z0-9+#]{1,6})$') AS alias FROM base
    UNION
    SELECT skill_id, regexp_replace(nm,
        '^(Microsoft|Autodesk|Adobe|Oracle|IBM|SAP|Google|Amazon|Apache|Atlassian|Salesforce|'
        'The MathWorks|Dassault Systemes|PTC|Intuit|Cisco|VMware|Red Hat|Siemens|Bentley|Esri|'
        'Meta|Facebook|Apple|JetBrains|Elastic|MongoDB|Snowflake|Databricks)\s+', '') AS alias
    FROM base
    WHERE nm ~ ('^(Microsoft|Autodesk|Adobe|Oracle|IBM|SAP|Google|Amazon|Apache|Atlassian|Salesforce|'
                'The MathWorks|Dassault Systemes|PTC|Intuit|Cisco|VMware|Red Hat|Siemens|Bentley|Esri|'
                'Meta|Facebook|Apple|JetBrains|Elastic|MongoDB|Snowflake|Databricks)\s+')
)
INSERT INTO core.skill_aliases (skill_id, alias, alias_type)
SELECT skill_id, alias, 'derived'
FROM cand
WHERE alias IS NOT NULL AND length(alias) >= 2
  AND lower(alias) NOT IN ('word', 'access', 'project', 'teams', 'office', 'outlook', 'go', 'edge',
                           'one', 'cloud', 'web', 'data', 'analytics', 'mail', 'sheets', 'docs',
                           'drive', 'forms', 'search', 'maps', 'it', 'pay', 'business', 'help', 'bi')
ON CONFLICT (skill_id, alias) DO NOTHING;

-- ---------------------------------------------------------------------
-- The lexicon (materialized view = precomputed, indexed matching table)
-- ---------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS core.mv_skill_lexicon;
CREATE MATERIALIZED VIEW core.mv_skill_lexicon AS
WITH base AS (
    SELECT a.skill_id, a.alias, a.alias_type, k.taxonomy, k.skill_type,
           (a.alias_type = 'derived' OR (k.taxonomy = 'onet_technology' AND length(a.alias) <= 3)) AS case_sensitive
    FROM core.skill_aliases a
    JOIN core.skills k ON k.skill_id = a.skill_id
    WHERE a.alias_type IN ('preferred', 'alternative', 'derived', 'manual')
      AND k.skill_type <> 'work_activity'
),
normed AS (
    SELECT b.*, core.fn_norm(b.alias) AS alias_norm, core.fn_cased(b.alias) AS alias_cased
    FROM base b
)
SELECT skill_id, alias, alias_type, taxonomy, skill_type, case_sensitive, alias_norm, alias_cased,
       array_length(string_to_array(alias_norm, ' '), 1) AS n_tokens,
       CASE taxonomy WHEN 'onet_technology' THEN 1 WHEN 'onet_skill' THEN 2
                     WHEN 'onet_knowledge'  THEN 3 ELSE 4 END AS priority
FROM normed
WHERE alias_norm <> ''
  AND array_length(string_to_array(alias_norm, ' '), 1) <= 6
  AND (case_sensitive
       OR (length(alias_norm) >= 3 AND NOT (alias_norm = ANY (core.fn_stopwords()))));

CREATE INDEX mv_skill_lexicon_norm  ON core.mv_skill_lexicon (alias_norm) WHERE NOT case_sensitive;
CREATE INDEX mv_skill_lexicon_cased ON core.mv_skill_lexicon (alias_cased) WHERE case_sensitive;
CREATE INDEX mv_skill_lexicon_trgm  ON core.mv_skill_lexicon USING gin (alias_norm gin_trgm_ops)
    WHERE NOT case_sensitive AND n_tokens >= 2;

-- ---------------------------------------------------------------------
-- Extraction over a token array (SkillSpan sentences are already tokenised)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_extract_skills(p_tokens TEXT[],
                                                  p_fuzzy BOOLEAN DEFAULT TRUE,
                                                  p_min_similarity NUMERIC DEFAULT NULL)
RETURNS TABLE (start_tok INTEGER, end_tok INTEGER, span_text TEXT, skill_id BIGINT, skill TEXT,
               skill_type TEXT, taxonomy TEXT, method TEXT, score NUMERIC)
LANGUAGE plpgsql STABLE
SET pg_trgm.similarity_threshold = 0.75
AS $$
#variable_conflict use_column
DECLARE
    n       INTEGER := COALESCE(array_length(p_tokens, 1), 0);
    covered BOOLEAN[];
    v_min   NUMERIC := COALESCE(p_min_similarity, core.param('nlp_min_similarity'), 0.8);
    r       RECORD;
BEGIN
    IF n = 0 THEN RETURN; END IF;
    covered := array_fill(FALSE, ARRAY[n]);

    FOR r IN
        WITH tok AS (
            SELECT i::INT AS i, core.fn_norm(t) AS nm, core.fn_cased(t) AS cs
            FROM unnest(p_tokens) WITH ORDINALITY u(t, i)
        ),
        arr AS (
            SELECT array_agg(nm ORDER BY i) AS nms, array_agg(cs ORDER BY i) AS css FROM tok
        ),
        g AS (
            SELECT s, s + l - 1 AS e, l,
                   array_to_string(array_remove(a.nms[s:s + l - 1], ''), ' ') AS ng,
                   array_to_string(array_remove(a.css[s:s + l - 1], ''), ' ') AS ngc,
                   a.nms[s] AS first_n, a.nms[s + l - 1] AS last_n
            FROM arr a, generate_series(1, n) s, generate_series(1, 6) l
            WHERE s + l - 1 <= n
        ),
        g2 AS (
            SELECT * FROM g
            WHERE first_n <> '' AND last_n <> '' AND ng <> ''
              AND NOT (first_n = ANY (core.fn_stopwords()))
              AND NOT (last_n  = ANY (core.fn_stopwords()))
        ),
        m AS (
            SELECT g2.s, g2.e, g2.l, x.skill_id, 'exact'::TEXT AS method, 1.0::NUMERIC AS score, x.priority
            FROM g2 JOIN core.mv_skill_lexicon x ON NOT x.case_sensitive AND x.alias_norm = g2.ng
            UNION ALL
            SELECT g2.s, g2.e, g2.l, x.skill_id, 'exact', 1.0, x.priority
            FROM g2 JOIN core.mv_skill_lexicon x ON x.case_sensitive AND x.alias_cased = g2.ngc
            UNION ALL
            SELECT g2.s, g2.e, g2.l, x.skill_id, 'fuzzy',
                   ROUND(similarity(x.alias_norm, g2.ng)::NUMERIC, 3), x.priority
            FROM g2 JOIN core.mv_skill_lexicon x
              ON p_fuzzy AND g2.l >= 2 AND length(g2.ng) >= 8
             AND NOT x.case_sensitive AND x.n_tokens >= 2
             AND x.alias_norm % g2.ng
            WHERE similarity(x.alias_norm, g2.ng) >= v_min
        )
        SELECT m.s, m.e, m.skill_id, m.method, m.score
        FROM m
        ORDER BY m.l DESC, (m.method = 'exact') DESC, m.score DESC, m.priority, m.skill_id
    LOOP
        -- longest-match-first: keep a match only if none of its tokens is taken
        IF NOT (TRUE = ANY (covered[r.s:r.e])) THEN
            covered[r.s:r.e] := array_fill(TRUE, ARRAY[r.e - r.s + 1]);
            start_tok := r.s;
            end_tok   := r.e;
            span_text := regexp_replace(array_to_string(p_tokens[r.s:r.e], ' '),
                                        '^[^A-Za-z0-9]+|[^A-Za-z0-9+#]+$', '', 'g');
            skill_id  := r.skill_id;
            SELECT k.name, k.skill_type, k.taxonomy INTO skill, skill_type, taxonomy
            FROM core.skills k WHERE k.skill_id = r.skill_id;
            method := r.method;
            score  := r.score;
            RETURN NEXT;
        END IF;
    END LOOP;
END $$;

-- Extraction over raw text
CREATE OR REPLACE FUNCTION core.fn_extract_from_text(p_text TEXT, p_fuzzy BOOLEAN DEFAULT TRUE)
RETURNS TABLE (start_tok INTEGER, end_tok INTEGER, span_text TEXT, skill_id BIGINT, skill TEXT,
               skill_type TEXT, taxonomy TEXT, method TEXT, score NUMERIC)
LANGUAGE sql STABLE AS $$
    SELECT * FROM core.fn_extract_skills(core.fn_tokenize(p_text), p_fuzzy) ORDER BY 1
$$;

-- ---------------------------------------------------------------------
-- Evidence maintenance: approved candidates -> 'Job postings' evidence
--   importance = share of this career's postings in which the skill
--                was found and approved
--   confidence = mean match score of the approved candidates
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION core.fn_refresh_posting_evidence(p_career BIGINT)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_src  SMALLINT := (SELECT source_id FROM core.data_sources WHERE source_name = 'Job postings');
    v_rows INTEGER;
BEGIN
    DELETE FROM core.career_skill_evidence WHERE career_id = p_career AND source_id = v_src;

    INSERT INTO core.career_skill_evidence
           (career_id, skill_id, source_id, importance, requirement_type, confidence, source_record)
    WITH posts AS (
        SELECT COUNT(DISTINCT batch_id) AS n FROM core.extraction_candidates WHERE career_id = p_career
    ),
    ok AS (
        SELECT matched_skill_id AS skill_id, COUNT(DISTINCT batch_id) AS n_found,
               AVG(match_score) AS avg_score
        FROM core.extraction_candidates
        WHERE career_id = p_career AND status = 'approved' AND matched_skill_id IS NOT NULL
        GROUP BY matched_skill_id
    )
    SELECT p_career, ok.skill_id, v_src,
           ROUND(LEAST(ok.n_found::NUMERIC / GREATEST(posts.n, 1), 1), 4),
           'present',
           GREATEST(ROUND(ok.avg_score, 2), 0.01),
           format('Job postings: found and approved in %s of %s posting(s)', ok.n_found, posts.n)
    FROM ok CROSS JOIN posts;

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RETURN v_rows;
END $$;

CREATE OR REPLACE FUNCTION core.trg_candidate_reviewed() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.career_id IS NOT NULL THEN
        PERFORM core.fn_refresh_posting_evidence(NEW.career_id);
    END IF;
    RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS candidate_reviewed ON core.extraction_candidates;
CREATE TRIGGER candidate_reviewed
AFTER UPDATE OF status ON core.extraction_candidates
FOR EACH ROW WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION core.trg_candidate_reviewed();

-- Submit a job posting: extract, store candidates as pending, return the batch id
CREATE OR REPLACE FUNCTION core.fn_submit_job_posting(p_career BIGINT, p_text TEXT,
                                                      p_fuzzy BOOLEAN DEFAULT TRUE)
RETURNS BIGINT LANGUAGE plpgsql AS $$
DECLARE
    v_batch  BIGINT := nextval('core.job_posting_batch_seq');
    v_tokens TEXT[] := core.fn_tokenize(p_text);
BEGIN
    INSERT INTO core.extraction_candidates
           (career_id, source_text, span_text, matched_skill_id, match_score, status,
            batch_id, method, span_start, span_end)
    SELECT p_career,
           -- context: up to 8 tokens either side, without line-break markers
           array_to_string(array_remove(v_tokens[GREATEST(x.start_tok - 8, 1):x.end_tok + 8], '¶'), ' '),
           x.span_text, x.skill_id, x.score, 'pending', v_batch, x.method, x.start_tok, x.end_tok
    FROM core.fn_extract_skills(v_tokens, p_fuzzy) x;

    PERFORM core.fn_refresh_posting_evidence(p_career);   -- the number of postings changed
    RETURN v_batch;
END $$;

-- Approve / reject (the trigger maintains the evidence)
CREATE OR REPLACE FUNCTION core.fn_review_candidate(p_candidate BIGINT, p_reviewer BIGINT, p_approve BOOLEAN)
RETURNS TEXT LANGUAGE sql AS $$
    UPDATE core.extraction_candidates
    SET status = CASE WHEN p_approve THEN 'approved' ELSE 'rejected' END,
        reviewer_id = p_reviewer, reviewed_at = now()
    WHERE candidate_id = p_candidate
    RETURNING status
$$;
