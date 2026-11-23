"""
SkillBridge - Step 2.1 dataset inspection.

Usage (from the project root, with the venv active):
    python scripts/inspect_datasets.py data/raw reports/data_inspection.md

What it does, for every file under data/raw (including CSVs inside the ESCO zip):
  - CSV/TXT: delimiter, rows, columns, dtypes, nulls, duplicate rows,
    candidate ID columns, sample rows, and O*NET-specific hints (Scale ID values).
  - JSON / JSONL (SkillSpan): record count, keys, tag vocabulary, example record.
  - ZIP: lists members and inspects every CSV inside without extracting to disk.
Writes one Markdown report you can hand in as the "dataset quality report" draft.
"""

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd

ENCODINGS = ("utf-8", "utf-8-sig", "latin-1")
ONET_HINT_COLS = ("O*NET-SOC Code", "Element ID", "Element Name", "Scale ID",
                  "Data Value", "Recommend Suppress", "Not Relevant", "Hot Technology")


def sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;|").delimiter
    except csv.Error:
        return ","


def read_table(raw: bytes) -> tuple[pd.DataFrame, str, str]:
    for enc in ENCODINGS:
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    delim = sniff_delimiter(text[:20000])
    df = pd.read_csv(io.StringIO(text), sep=delim, low_memory=False)
    return df, delim, enc


def describe_table(name: str, df: pd.DataFrame, delim: str, enc: str) -> list[str]:
    out = [f"## {name}", ""]
    out.append(f"- Encoding: `{enc}` | Delimiter: `{repr(delim)}`")
    out.append(f"- Rows: **{len(df):,}** | Columns: **{df.shape[1]}**")
    out.append(f"- Fully duplicated rows: **{int(df.duplicated().sum()):,}**")
    out.append("")
    out.append("| Column | dtype | Nulls | Null % | Distinct | Example |")
    out.append("| --- | --- | --- | --- | --- | --- |")
    for col in df.columns:
        s = df[col]
        nulls = int(s.isna().sum())
        distinct = int(s.nunique(dropna=True))
        example = str(s.dropna().iloc[0])[:60].replace("|", "/") if s.notna().any() else ""
        pct = 100 * nulls / len(df) if len(df) else 0
        out.append(f"| {col} | {s.dtype} | {nulls:,} | {pct:.1f} | {distinct:,} | {example} |")
    out.append("")

    # Candidate identifier columns: fully unique, no nulls
    ids = [c for c in df.columns if df[c].notna().all() and df[c].is_unique]
    out.append(f"- Candidate single-column keys: {', '.join(f'`{c}`' for c in ids) or 'none'}")

    # O*NET hints
    present = [c for c in ONET_HINT_COLS if c in df.columns]
    if present:
        out.append(f"- Looks like O*NET (columns found: {', '.join(present)})")
        if "Scale ID" in df.columns:
            scales = df["Scale ID"].value_counts().to_dict()
            out.append(f"- Scale ID values: {scales}")
            if "Data Value" in df.columns:
                rng = df.groupby("Scale ID")["Data Value"].agg(["min", "max"]).round(2)
                out.append(f"- Data Value range per scale: {rng.to_dict('index')}")
        if "O*NET-SOC Code" in df.columns:
            out.append(f"- Distinct occupations: {df['O*NET-SOC Code'].nunique():,}")
        if "Element Name" in df.columns:
            out.append(f"- Distinct elements (skills/knowledge/activities): "
                       f"{df['Element Name'].nunique():,}")
    if any("uri" in c.lower() for c in df.columns):
        out.append("- Looks like ESCO (URI columns present)")
    if "relationType" in df.columns:
        out.append(f"- relationType values: {df['relationType'].value_counts().to_dict()}")

    out.append("")
    out.append("Sample rows:")
    out.append("")
    out.append("```")
    out.append(df.head(3).to_string(max_colwidth=50))
    out.append("```")
    out.append("")
    return out


def load_json_records(raw: bytes) -> list:
    text = raw.decode("utf-8-sig")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            # e.g. {"data": [...]} or a dict of records
            for v in data.values():
                if isinstance(v, list):
                    return v
            return [data]
        return data
    except json.JSONDecodeError:
        # JSON Lines
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def describe_json(name: str, raw: bytes) -> list[str]:
    out = [f"## {name}", ""]
    recs = load_json_records(raw)
    out.append(f"- Records: **{len(recs):,}**")
    if not recs:
        return out + [""]
    keys = Counter(k for r in recs if isinstance(r, dict) for k in r.keys())
    out.append(f"- Keys (record count): {dict(keys)}")

    # Tag vocabularies for any list-valued field whose name suggests tags
    for k in keys:
        if any(t in k.lower() for t in ("tag", "label", "ner")):
            vocab = Counter()
            for r in recs:
                v = r.get(k)
                if isinstance(v, list):
                    vocab.update(map(str, v))
            if vocab:
                out.append(f"- `{k}` vocabulary: {dict(vocab.most_common(20))}")
    token_key = next((k for k in keys if "token" in k.lower()), None)
    if token_key:
        lens = [len(r.get(token_key) or []) for r in recs]
        out.append(f"- `{token_key}` length: min {min(lens)}, max {max(lens)}, "
                   f"mean {sum(lens)/len(lens):.1f}")
    out.append("")
    out.append("Example record:")
    out.append("")
    out.append("```json")
    out.append(json.dumps(recs[0], ensure_ascii=False)[:1500])
    out.append("```")
    out.append("")
    return out


def main(raw_dir: Path, report_path: Path) -> None:
    lines = ["# SkillBridge dataset inspection report", ""]
    files = sorted(p for p in raw_dir.rglob("*") if p.is_file())
    lines.append(f"Files found: {len(files)}")
    lines.append("")

    for path in files:
        suffix = path.suffix.lower()
        print(f"Inspecting {path.name} ...")
        try:
            if suffix in (".csv", ".txt", ".tsv"):
                df, d, e = read_table(path.read_bytes())
                lines += describe_table(path.name, df, d, e)
            elif suffix in (".json", ".jsonl"):
                lines += describe_json(path.name, path.read_bytes())
            elif suffix == ".zip":
                with zipfile.ZipFile(path) as zf:
                    members = zf.namelist()
                    lines += [f"# ZIP: {path.name}", "", f"Members ({len(members)}):", ""]
                    lines += [f"- {m}" for m in members]
                    lines.append("")
                    for m in members:
                        if m.lower().endswith(".csv"):
                            print(f"   - {m}")
                            df, d, e = read_table(zf.read(m))
                            lines += describe_table(f"{path.name} :: {m}", df, d, e)
            else:
                lines += [f"## {path.name}", "", f"- Skipped (type `{suffix}`)", ""]
        except Exception as exc:  # keep going, record the problem
            lines += [f"## {path.name}", "", f"- **ERROR:** {exc!r}", ""]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python inspect_datasets.py <raw_data_dir> <report.md>")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
