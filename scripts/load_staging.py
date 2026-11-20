"""
SkillBridge - Phase 2.2 / 2.3: load every raw file into the `staging` schema,
then run validation checks and write reports/staging_validation.md.

Usage (project root, venv active, .env containing DATABASE_URL):
    python scripts/load_staging.py data/raw

What it does
  1. Runs sql/01_staging_schema.sql (drops and recreates the staging schema).
  2. Loads O*NET CSVs, ESCO CSVs (read straight from the zip) and SkillSpan JSON.
     Every value is loaded as text, exactly as in the file. Empty cells -> NULL.
  3. Records each load in staging.load_log.
  4. Runs data-quality checks and writes a Markdown report.

Safe to re-run: the staging schema is rebuilt from scratch each time.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_SQL = PROJECT_ROOT / "sql" / "01_staging_schema.sql"
REPORT_PATH = PROJECT_ROOT / "reports" / "staging_validation.md"

# ---------------------------------------------------------------------------
# File -> staging table mapping
# ---------------------------------------------------------------------------
# O*NET files that share the Importance/Level rating layout
ONET_RATING_FILES = {
    "essential_skills_dbms.csv": "skill_basic",
    "transferable_skills_dbms.csv": "skill_cross_functional",
    "knowledge_dbms.csv": "knowledge",
    "work_activities_dbms.csv": "work_activity",
}
ONET_OTHER_FILES = {
    "occupation_data_dbms.csv": "onet_occupations",
    "software_skills_dbms.csv": "onet_technology_skills",
    "job_titles_csv.csv": "onet_alternate_titles",
    "scales_reference_dbms.csv": "onet_scales",
}
# Found by base name, inside the zip or loose in data/raw
ZIPPED_FILES = {
    "content_model_reference_dbms.csv": "onet_content_model",
    "occupations_en.csv": "esco_occupations",
    "skills_en.csv": "esco_skills",
    "occupationSkillRelations_en.csv": "esco_occupation_skill_relations",
    "skillSkillRelations_en.csv": "esco_skill_skill_relations",
    "broaderRelationsSkillPillar_en.csv": "esco_broader_skill_relations",
    "broaderRelationsOccPillar_en.csv": "esco_broader_occupation_relations",
    "skillGroups_en.csv": "esco_skill_groups",
    "ISCOGroups_en.csv": "esco_isco_groups",
}
ESCO_COLLECTIONS = {
    "digitalSkillsCollection_en.csv": "digital",
    "transversalSkillsCollection_en.csv": "transversal",
    "greenSkillsCollection_en.csv": "green",
    "researchSkillsCollection_en.csv": "research",
    "languageSkillsCollection_en.csv": "language",
    "digCompSkillsCollection_en.csv": "digcomp",
}
SKILLSPAN_FILES = {"train_dbms.json": "train", "dev_dbms.json": "dev", "test_dbms.json": "test"}

# Source header -> staging column, where the automatic snake_case rule is not enough
HEADER_OVERRIDES = {
    "O*NET-SOC Code": "onet_soc_code",
    "Date": "date_text",
    "Source(s)": "sources",
    "N": "n",
    "broaderConceptPT": "broader_concept_pt",
}


def to_snake(header: str) -> str:
    if header in HEADER_OVERRIDES:
        return HEADER_OVERRIDES[header]
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", header.strip())  # camelCase -> camel_Case
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s)                         # spaces/punctuation -> _
    return s.strip("_").lower()


# ---------------------------------------------------------------------------
# Reading files
# ---------------------------------------------------------------------------
def read_csv_bytes(raw: bytes) -> pd.DataFrame:
    """Read a CSV as all-text. keep_default_na=False stops strings like 'NA'
    (a real label) from becoming null; only truly empty cells become NULL."""
    text = raw.decode("utf-8-sig")
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False, na_values=[""])
    df = df.astype(object).where(df.notna(), None)
    return df


def collect_sources(raw_dir: Path) -> tuple[dict[str, bytes], list[str]]:
    """Return {base_name: bytes} for every CSV/JSON in raw_dir and inside any zip.
    Duplicate base names are compared; identical copies are fine, differing
    copies are reported and the first one found is used."""
    files: dict[str, bytes] = {}
    origin: dict[str, str] = {}
    notes: list[str] = []

    def add(name: str, data: bytes, where: str) -> None:
        if name in files:
            same = hashlib.sha256(files[name]).digest() == hashlib.sha256(data).digest()
            if not same:
                notes.append(f"`{name}` appears twice with DIFFERENT content "
                             f"({origin[name]} vs {where}); using the first.")
            return
        files[name] = data
        origin[name] = where

    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in (".csv", ".json", ".jsonl"):
            add(path.name, path.read_bytes(), str(path.relative_to(raw_dir)))
        elif path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as zf:
                # root-level members first, then sub-folders
                members = sorted(zf.namelist(), key=lambda m: (m.count("/"), m))
                for m in members:
                    base = m.rsplit("/", 1)[-1]
                    if base.lower().endswith(".csv"):
                        add(base, zf.read(m), f"{path.name}::{m}")
    return files, notes


def load_json_records(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8-sig")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
            return [data]
        return data
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def table_columns(cur: psycopg.Cursor, table: str) -> list[str]:
    cur.execute(
        """SELECT column_name FROM information_schema.columns
           WHERE table_schema = 'staging' AND table_name = %s
           ORDER BY ordinal_position""",
        (table,),
    )
    return [r[0] for r in cur.fetchall()]


def copy_frame(cur: psycopg.Cursor, table: str, df: pd.DataFrame, source_file: str,
               fixed: dict[str, str] | None = None) -> tuple[int, list[str]]:
    """COPY a DataFrame into staging.<table>. Only columns present in both the
    file and the table are loaded. Returns (rows_loaded, warnings)."""
    warnings: list[str] = []
    df = df.rename(columns={c: to_snake(c) for c in df.columns})
    fixed = dict(fixed or {})
    fixed["source_file"] = source_file

    target = [c for c in table_columns(cur, table) if c != "loaded_at"]
    file_cols = [c for c in target if c in df.columns]
    missing = [c for c in target if c not in df.columns and c not in fixed]
    extra = [c for c in df.columns if c not in target]
    if missing:
        warnings.append(f"{source_file}: columns expected but not in file -> {missing}")
    if extra and table != "esco_skill_collections":  # collections: extra columns skipped on purpose
        warnings.append(f"{source_file}: columns in file not loaded -> {extra}")

    cols = file_cols + list(fixed.keys())
    col_sql = ", ".join(cols)
    fixed_vals = list(fixed.values())
    with cur.copy(f"COPY staging.{table} ({col_sql}) FROM STDIN") as copy:
        for row in df[file_cols].itertuples(index=False, name=None):
            copy.write_row(list(row) + fixed_vals)
    return len(df), warnings


def log_load(cur, table: str, source_file: str, rows_in_file: int, rows_loaded: int) -> None:
    cur.execute(
        "INSERT INTO staging.load_log (table_name, source_file, rows_in_file, rows_loaded) "
        "VALUES (%s, %s, %s, %s)",
        (table, source_file, rows_in_file, rows_loaded),
    )


def load_all(conn: psycopg.Connection, files: dict[str, bytes]) -> list[str]:
    warnings: list[str] = []
    cur = conn.cursor()

    def csv_job(name: str, table: str, fixed: dict | None = None) -> None:
        if name not in files:
            warnings.append(f"MISSING FILE: `{name}` (target staging.{table}) - skipped")
            return
        df = read_csv_bytes(files[name])
        n, w = copy_frame(cur, table, df, name, fixed)
        warnings.extend(w)
        log_load(cur, table, name, len(df), n)
        print(f"  {name:<40} -> staging.{table:<34} {n:>8,} rows")

    print("O*NET")
    for name, table in ONET_OTHER_FILES.items():
        csv_job(name, table)
    for name, category in ONET_RATING_FILES.items():
        csv_job(name, "onet_ratings", {"category": category})

    print("ESCO (and files found inside the zip)")
    for name, table in ZIPPED_FILES.items():
        csv_job(name, table)
    for name, collection in ESCO_COLLECTIONS.items():
        csv_job(name, "esco_skill_collections", {"collection": collection})

    print("SkillSpan")
    for name, split in SKILLSPAN_FILES.items():
        if name not in files:
            warnings.append(f"MISSING FILE: `{name}` - skipped")
            continue
        recs = load_json_records(files[name])
        with cur.copy(
            "COPY staging.skillspan_sentences "
            "(split, idx, source, tokens, tags_skill, tags_knowledge, source_file) FROM STDIN"
        ) as copy:
            for r in recs:
                copy.write_row([
                    split,
                    None if r.get("idx") is None else str(r.get("idx")),
                    r.get("source"),
                    json.dumps(r.get("tokens"), ensure_ascii=False),
                    json.dumps(r.get("tags_skill"), ensure_ascii=False),
                    json.dumps(r.get("tags_knowledge"), ensure_ascii=False),
                    name,
                ])
        log_load(cur, "skillspan_sentences", name, len(recs), len(recs))
        print(f"  {name:<40} -> staging.skillspan_sentences{'':<14} {len(recs):>8,} rows")

    conn.commit()
    return warnings


# ---------------------------------------------------------------------------
# Validation checks: (title, explanation, SQL)
# ---------------------------------------------------------------------------
NUMERIC = r"'^-?[0-9]+(\.[0-9]+)?$'"

CHECKS: list[tuple[str, str, str]] = [
    ("Rows loaded per file",
     "rows_in_file should equal rows_loaded for every file.",
     """SELECT table_name, source_file, rows_in_file, rows_loaded,
               rows_in_file - rows_loaded AS difference
        FROM staging.load_log ORDER BY table_name, source_file"""),

    # ---------------- O*NET ----------------
    ("O*NET: elements per rating category",
     "Expected: skill_basic 10, skill_cross_functional 25 (together the 35 O*NET skills), "
     "knowledge 33, work_activity 41.",
     """SELECT category,
               COUNT(DISTINCT element_id)    AS elements,
               COUNT(DISTINCT onet_soc_code) AS occupations,
               COUNT(*)                      AS rows
        FROM staging.onet_ratings GROUP BY category ORDER BY category"""),

    ("O*NET: non-numeric Data Value",
     "Should be 0. Any row here cannot be normalised.",
     f"""SELECT category, COUNT(*) AS bad_rows
         FROM staging.onet_ratings
         WHERE data_value IS NULL OR data_value !~ {NUMERIC}
         GROUP BY category"""),

    ("O*NET: Data Value outside the official scale range",
     "Compares each rating with Minimum/Maximum in scales_reference. Should be 0.",
     f"""SELECT r.category, r.scale_id, s.minimum, s.maximum,
                MIN(r.data_value::numeric) AS min_seen,
                MAX(r.data_value::numeric) AS max_seen,
                COUNT(*) FILTER (WHERE r.data_value::numeric < s.minimum::numeric
                                    OR r.data_value::numeric > s.maximum::numeric) AS out_of_range
         FROM staging.onet_ratings r
         JOIN staging.onet_scales s ON s.scale_id = r.scale_id
         WHERE r.data_value ~ {NUMERIC}
         GROUP BY r.category, r.scale_id, s.minimum, s.maximum
         ORDER BY r.category, r.scale_id"""),

    ("O*NET: Importance rows without a matching Level row (and vice versa)",
     "Every (occupation, element) should have both IM and LV. Should be 0.",
     """SELECT category, COUNT(*) AS unpaired
        FROM (SELECT category, onet_soc_code, element_id,
                     COUNT(*) FILTER (WHERE scale_id = 'IM') AS im,
                     COUNT(*) FILTER (WHERE scale_id = 'LV') AS lv
              FROM staging.onet_ratings
              GROUP BY category, onet_soc_code, element_id) t
        WHERE im <> 1 OR lv <> 1
        GROUP BY category"""),

    ("O*NET: duplicate ratings",
     "Same occupation + element + scale more than once. Should be 0.",
     """SELECT category, COUNT(*) AS duplicate_keys
        FROM (SELECT category, onet_soc_code, element_id, scale_id
              FROM staging.onet_ratings
              GROUP BY 1, 2, 3, 4 HAVING COUNT(*) > 1) d
        GROUP BY category"""),

    ("O*NET: quality flags",
     "Recommend Suppress = Y means low precision -> lower confidence. "
     "Not Relevant = Y (on LV rows) means the element is not relevant for that occupation.",
     """SELECT category,
               COUNT(*) FILTER (WHERE recommend_suppress = 'Y') AS suppress_y,
               COUNT(*) FILTER (WHERE recommend_suppress IS NULL) AS suppress_null,
               COUNT(*) FILTER (WHERE not_relevant = 'Y')       AS not_relevant_y,
               COUNT(DISTINCT domain_source)                    AS domain_sources
        FROM staging.onet_ratings GROUP BY category ORDER BY category"""),

    ("O*NET: rated occupations missing from Occupation Data",
     "Orphans: ratings whose SOC code is not in occupation_data. Should be 0.",
     """SELECT r.category, COUNT(DISTINCT r.onet_soc_code) AS orphan_occupations
        FROM staging.onet_ratings r
        LEFT JOIN staging.onet_occupations o USING (onet_soc_code)
        WHERE o.onet_soc_code IS NULL
        GROUP BY r.category"""),

    ("O*NET: occupations with no skill ratings",
     "Expected to be non-zero: O*NET has 1,016 occupations but only ~910 carry ratings. "
     "These cannot be target careers for gap analysis.",
     """SELECT COUNT(*) AS occupations_without_skill_ratings
        FROM staging.onet_occupations o
        WHERE NOT EXISTS (SELECT 1 FROM staging.onet_ratings r
                          WHERE r.onet_soc_code = o.onet_soc_code
                            AND r.category LIKE 'skill%')"""),

    ("O*NET: rated elements without a description in the Content Model",
     "Descriptions are needed for embeddings. Should be 0.",
     """SELECT DISTINCT r.category, r.element_id, r.element_name
        FROM staging.onet_ratings r
        LEFT JOIN staging.onet_content_model c USING (element_id)
        WHERE c.element_id IS NULL OR c.description IS NULL
        ORDER BY 1, 2"""),

    ("O*NET Technology Skills: overview",
     "Workplace examples are the concrete tools (Python, SQL, Excel ...).",
     """SELECT COUNT(*) AS rows,
               COUNT(DISTINCT workplace_example) AS distinct_tools,
               COUNT(DISTINCT element_id)        AS categories,
               COUNT(DISTINCT onet_soc_code)     AS occupations,
               COUNT(*) FILTER (WHERE hot_technology = 'Y') AS hot_technology_rows,
               COUNT(*) FILTER (WHERE in_demand = 'Y')      AS in_demand_rows
        FROM staging.onet_technology_skills"""),

    # ---------------- ESCO ----------------
    ("ESCO: duplicate concept URIs",
     "The inspection found more rows than distinct URIs. 'distinct_versions' > 1 means the "
     "copies differ in some column and the transform step must choose one.",
     """SELECT 'esco_skills' AS tbl, COUNT(*) AS duplicated_uris,
               MAX(n) AS max_copies, MAX(v) AS distinct_versions
        FROM (SELECT concept_uri, COUNT(*) n,
                     COUNT(DISTINCT (skill_type, reuse_level, preferred_label, alt_labels,
                                     description, modified_date)) v
              FROM staging.esco_skills GROUP BY concept_uri HAVING COUNT(*) > 1) d
        UNION ALL
        SELECT 'esco_occupations', COUNT(*), MAX(n), MAX(v)
        FROM (SELECT concept_uri, COUNT(*) n,
                     COUNT(DISTINCT (preferred_label, alt_labels, description, code,
                                     modified_date)) v
              FROM staging.esco_occupations GROUP BY concept_uri HAVING COUNT(*) > 1) d"""),

    ("ESCO: example duplicated skill URIs",
     "Look at these rows to see what differs between the copies.",
     """SELECT concept_uri, preferred_label, skill_type, reuse_level, modified_date
        FROM staging.esco_skills
        WHERE concept_uri IN (SELECT concept_uri FROM staging.esco_skills
                              GROUP BY concept_uri HAVING COUNT(*) > 1
                              ORDER BY concept_uri LIMIT 3)
        ORDER BY concept_uri"""),

    ("ESCO: skills with no skill_type",
     "Needs a rule in the transform step (e.g. take it from occupationSkillRelations).",
     """SELECT concept_uri, preferred_label, reuse_level
        FROM staging.esco_skills WHERE skill_type IS NULL"""),

    ("ESCO: occupation-skill relations that point to unknown concepts",
     "Orphan foreign keys. Should be 0 in both columns.",
     """SELECT
          COUNT(*) FILTER (WHERE s.concept_uri IS NULL) AS unknown_skill_uri,
          COUNT(*) FILTER (WHERE o.concept_uri IS NULL) AS unknown_occupation_uri
        FROM staging.esco_occupation_skill_relations r
        LEFT JOIN (SELECT DISTINCT concept_uri FROM staging.esco_skills) s
               ON s.concept_uri = r.skill_uri
        LEFT JOIN (SELECT DISTINCT concept_uri FROM staging.esco_occupations) o
               ON o.concept_uri = r.occupation_uri"""),

    ("ESCO: relation types",
     "essential vs optional, by skill type.",
     """SELECT relation_type, COALESCE(skill_type, '(null)') AS skill_type, COUNT(*) AS rows
        FROM staging.esco_occupation_skill_relations
        GROUP BY 1, 2 ORDER BY 1, 2"""),

    ("ESCO: duplicate occupation-skill pairs",
     "Same occupation + skill listed more than once. Should be 0.",
     """SELECT COUNT(*) AS duplicate_pairs
        FROM (SELECT occupation_uri, skill_uri FROM staging.esco_occupation_skill_relations
              GROUP BY 1, 2 HAVING COUNT(*) > 1) d"""),

    ("ESCO: broader (parent) links that point to unknown concepts",
     "Parents should be a skill or a skill group. Should be 0.",
     """SELECT COUNT(*) AS unknown_parent
        FROM staging.esco_broader_skill_relations b
        WHERE NOT EXISTS (SELECT 1 FROM staging.esco_skills s WHERE s.concept_uri = b.broader_uri)
          AND NOT EXISTS (SELECT 1 FROM staging.esco_skill_groups g WHERE g.concept_uri = b.broader_uri)"""),

    ("ESCO: skills per reuse level",
     "transversal / cross-sector skills are the most likely to transfer between careers.",
     """SELECT COALESCE(reuse_level, '(null)') AS reuse_level,
               COUNT(DISTINCT concept_uri) AS skills
        FROM staging.esco_skills GROUP BY 1 ORDER BY 2 DESC"""),

    ("ESCO: collection sizes",
     "",
     """SELECT collection, COUNT(DISTINCT concept_uri) AS skills
        FROM staging.esco_skill_collections GROUP BY 1 ORDER BY 2 DESC"""),

    # ---------------- SkillSpan ----------------
    ("SkillSpan: sentences per split and source",
     "Use these counts in the paper's dataset table.",
     """SELECT split, source, COUNT(*) AS sentences,
               SUM(jsonb_array_length(tokens)) AS tokens
        FROM staging.skillspan_sentences GROUP BY 1, 2 ORDER BY 1, 2"""),

    ("SkillSpan: token/tag length mismatches",
     "Every sentence needs one skill tag and one knowledge tag per token. Should be 0.",
     """SELECT split, COUNT(*) AS mismatched
        FROM staging.skillspan_sentences
        WHERE jsonb_array_length(tokens) <> jsonb_array_length(tags_skill)
           OR jsonb_array_length(tokens) <> jsonb_array_length(tags_knowledge)
        GROUP BY split"""),

    ("SkillSpan: long sentences",
     "Sentences over 200 tokens will need splitting or truncation before a 512-subword BERT model.",
     """SELECT split, COUNT(*) AS over_200_tokens, MAX(jsonb_array_length(tokens)) AS longest
        FROM staging.skillspan_sentences
        WHERE jsonb_array_length(tokens) > 200 GROUP BY split"""),
]


def run_checks(conn: psycopg.Connection) -> list[str]:
    out: list[str] = []
    cur = conn.cursor()
    for title, note, sql in CHECKS:
        out += [f"## {title}", ""]
        if note:
            out += [note, ""]
        try:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
            if not rows:
                out += ["_No rows (nothing to report)._", ""]
                continue
            out.append("| " + " | ".join(cols) + " |")
            out.append("| " + " | ".join("---" for _ in cols) + " |")
            for r in rows[:50]:
                cells = ["" if v is None else str(v).replace("|", "/").replace("\n", " ")[:80]
                         for v in r]
                out.append("| " + " | ".join(cells) + " |")
            if len(rows) > 50:
                out.append(f"\n_{len(rows) - 50} more rows not shown._")
            out.append("")
        except Exception as exc:
            conn.rollback()
            out += [f"**Check failed:** `{exc}`", ""]
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/load_staging.py <raw_data_dir>")
    raw_dir = Path(sys.argv[1])
    if not raw_dir.is_dir():
        sys.exit(f"Folder not found: {raw_dir}")

    load_dotenv(PROJECT_ROOT / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is not set. Create a .env file in the project root.")

    print("Reading source files ...")
    files, notes = collect_sources(raw_dir)
    print(f"  {len(files)} distinct CSV/JSON files found")

    with psycopg.connect(url) as conn:
        print("Creating staging schema ...")
        conn.execute(SCHEMA_SQL.read_text(encoding="utf-8"))
        conn.commit()

        print("Loading ...")
        warnings = load_all(conn, files)

        print("Running validation checks ...")
        report = ["# SkillBridge staging validation report", ""]
        if notes or warnings:
            report += ["## Loader notes", ""]
            report += [f"- {n}" for n in notes + warnings]
            report.append("")
        report += run_checks(conn)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    for w in notes + warnings:
        print("  NOTE:", w)
    print(f"\nDone. Report written to {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()