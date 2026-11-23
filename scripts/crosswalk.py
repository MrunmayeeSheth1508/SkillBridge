"""
SkillBridge - load the official ESCO-O*NET crosswalk.

Download "O*NET - ESCO Crosswalk (Occupations)" from
    https://esco.ec.europa.eu/en/use-esco/other-crosswalks
and put the file (CSV, XLSX or a ZIP containing either) anywhere in data/raw.
The build (scripts/build_database.py) calls this automatically; to run it alone:

    python scripts/crosswalk.py data/raw

The column names are not fixed, so they are DETECTED from the contents:
  O*NET code column : values like 15-2051.00
  ESCO column       : values like http://data.europa.eu/esco/occupation/...
  match-type column : values containing exact / close / narrow / broad / related
"""

from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402

import pandas as pd  # noqa: E402
import psycopg  # noqa: E402

SOC = re.compile(r"^\d{2}-\d{4}(\.\d{2})?$")
ESCO_OCC = "data.europa.eu/esco/occupation/"
MATCH_TYPES = ("exact", "close", "narrow", "broad", "related")
NAME_HINTS = ("crosswalk", "onet", "o_net", "o-net", "o*net")


def _read_table(name: str, raw: bytes) -> pd.DataFrame | None:
    low = name.lower()
    try:
        if low.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(raw), dtype=str)          # needs: pip install openpyxl
        if low.endswith((".csv", ".tsv", ".txt")):
            for enc in ("utf-8-sig", "latin-1"):
                try:
                    return pd.read_csv(io.BytesIO(raw), dtype=str, sep=None, engine="python",
                                       encoding=enc, keep_default_na=False)
                except UnicodeDecodeError:
                    continue
    except ImportError as exc:
        raise SystemExit(f"Reading {name} needs an extra package: {exc}. Run: python -m pip install openpyxl")
    return None


def candidate_files(raw_dir: Path):
    """Yield (name, bytes) for files whose name suggests the crosswalk (also inside zips)."""
    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        low = path.name.lower()
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as zf:
                for m in zf.namelist():
                    base = m.rsplit("/", 1)[-1].lower()
                    if any(h in base for h in NAME_HINTS) or any(h in low for h in NAME_HINTS):
                        if base.endswith((".csv", ".xlsx", ".xls", ".tsv", ".txt")):
                            yield f"{path.name}::{m}", zf.read(m)
        elif any(h in low for h in NAME_HINTS) and low.endswith((".csv", ".xlsx", ".xls", ".tsv", ".txt")):
            yield path.name, path.read_bytes()


def detect_columns(df: pd.DataFrame) -> tuple[str, str, str] | None:
    onet = esco = mtype = None
    for col in df.columns:
        vals = df[col].dropna().astype(str).str.strip()
        vals = vals[vals != ""].head(1000)
        if vals.empty:
            continue
        if onet is None and vals.str.match(SOC).mean() > 0.8:
            onet = col
        elif esco is None and vals.str.contains(ESCO_OCC, regex=False).mean() > 0.5:
            esco = col
        elif mtype is None and vals.str.lower().apply(lambda v: any(t in v for t in MATCH_TYPES)).mean() > 0.8:
            mtype = col
    return (onet, esco, mtype) if onet and esco and mtype else None


def normalise_type(v: str) -> str | None:
    v = str(v).lower()
    return next((t for t in MATCH_TYPES if t in v), None)


def load_crosswalk(conn: psycopg.Connection, raw_dir: Path) -> list[str]:
    """Find, detect, stage and apply. Returns notes for the build report."""
    for name, raw in candidate_files(raw_dir):
        df = _read_table(name, raw)
        if df is None or df.empty:
            continue
        cols = detect_columns(df)
        if not cols:
            continue
        onet_col, esco_col, type_col = cols
        rows = []
        for code, uri, mt in df[[onet_col, esco_col, type_col]].itertuples(index=False, name=None):
            code, uri = str(code).strip(), str(uri).strip()
            t = normalise_type(mt)
            if not t or not SOC.match(code) or ESCO_OCC not in uri:
                continue
            if "." not in code:
                code += ".00"
            rows.append((code, uri, t, str(mt), name))

        cur = conn.cursor()
        cur.execute("TRUNCATE staging.esco_onet_crosswalk")
        with cur.copy("COPY staging.esco_onet_crosswalk "
                      "(onet_code, esco_uri, match_type, raw_match_type, source_file) FROM STDIN") as cp:
            for r in rows:
                cp.write_row(r)
        cur.execute("SELECT match_type, COUNT(*) FROM staging.esco_onet_crosswalk GROUP BY 1 ORDER BY 2 DESC")
        by_type = ", ".join(f"{t} {n:,}" for t, n in cur.fetchall())
        cur.execute("SELECT * FROM core.fn_apply_crosswalk()")
        links, careers, ev, shared = cur.fetchone()
        conn.commit()
        return [f"Crosswalk `{name}`: columns detected -> O*NET `{onet_col}`, ESCO `{esco_col}`, "
                f"type `{type_col}`; {len(rows):,} usable rows ({by_type})",
                f"Crosswalk applied: {links:,} links for {careers:,} O*NET careers; "
                f"{ev:,} ESCO evidence rows attached; {shared:,} career-skill pairs now have 2+ sources"]
    return ["ESCO-O*NET crosswalk NOT found in data/raw - O*NET careers have O*NET evidence only. "
            "Download it from https://esco.ec.europa.eu/en/use-esco/other-crosswalks"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/crosswalk.py <raw_data_dir>")
    with psycopg.connect(ls.get_database_url()) as c:
        for note in load_crosswalk(c, Path(sys.argv[1])):
            print(note)
        from tune_lexicon import load_blocklist
        load_blocklist(c)       # refresh the lexicon (skill popularity changed)
