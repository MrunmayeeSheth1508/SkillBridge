"""
SkillBridge - learn a lexicon blocklist from the SkillSpan TRAIN split.

    python scripts/tune_lexicon.py                     # defaults below
    python scripts/tune_lexicon.py --min-matches 3 --max-precision 0.25

Method (uses train only, so test results stay unbiased):
  1. Run the extractor (exact matching) over every train sentence.
  2. For each matched label, count how often its span overlaps a gold span.
  3. Labels matched at least --min-matches times with precision below
     --max-precision (e.g. "energy", "plan") are added to the blocklist.
  4. Save data/curated/lexicon_blocklist.csv, load it, refresh the lexicon.
The build re-loads the CSV automatically, so this only needs re-running
when the lexicon or the thresholds change.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402
from evaluate_extraction import bio_spans, overlaps  # noqa: E402

import psycopg  # noqa: E402

CSV_PATH = ls.PROJECT_ROOT / "data" / "curated" / "lexicon_blocklist.csv"


def load_blocklist(conn) -> int:
    """Load the CSV into core.lexicon_blocklist and refresh the lexicon (used by the build)."""
    cur = conn.cursor()
    cur.execute("TRUNCATE core.lexicon_blocklist")
    n = 0
    if CSV_PATH.exists():
        with CSV_PATH.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cur.execute("INSERT INTO core.lexicon_blocklist (alias_norm, train_matches, train_precision) "
                            "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                            (row["alias_norm"], int(row["train_matches"]), float(row["train_precision"])))
                n += 1
    cur.execute("REFRESH MATERIALIZED VIEW core.mv_skill_lexicon")
    conn.commit()
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-matches", type=int, default=3)
    ap.add_argument("--max-precision", type=float, default=0.25)
    args = ap.parse_args()

    with psycopg.connect(ls.get_database_url()) as conn:
        cur = conn.cursor()
        print("Resetting blocklist and refreshing lexicon ...")
        cur.execute("TRUNCATE core.lexicon_blocklist")
        cur.execute("REFRESH MATERIALIZED VIEW core.mv_skill_lexicon")
        conn.commit()

        print("Extracting on the TRAIN split ...")
        cur.execute("""SELECT sentence_id, tags_skill, tags_knowledge FROM staging.skillspan_sentences
                       WHERE split = 'train'""")
        gold = {}
        for sid, ts, tk in cur.fetchall():
            ts = ts if isinstance(ts, list) else json.loads(ts)
            tk = tk if isinstance(tk, list) else json.loads(tk)
            gold[sid] = sorted(set(bio_spans(ts)) | set(bio_spans(tk)))
        cur.execute("""
            SELECT s.sentence_id, x.start_tok, x.end_tok, core.fn_norm(x.span_text)
            FROM staging.skillspan_sentences s
            CROSS JOIN LATERAL core.fn_extract_skills(ARRAY(SELECT jsonb_array_elements_text(s.tokens)), false) x
            WHERE s.split = 'train'""")
        stats = defaultdict(lambda: [0, 0])          # label -> [matches, overlapping gold]
        for sid, s, e, label in cur.fetchall():
            stats[label][0] += 1
            if any(overlaps((s, e), g) for g in gold.get(sid, [])):
                stats[label][1] += 1

        blocked = sorted(
            ((label, n, hit / n) for label, (n, hit) in stats.items()
             if n >= args.min_matches and hit / n < args.max_precision),
            key=lambda x: (-x[1], x[0]))
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["alias_norm", "train_matches", "train_precision"])
            for label, n, p in blocked:
                w.writerow([label, n, f"{p:.3f}"])
        n = load_blocklist(conn)
        cur.execute("SELECT COUNT(*) FROM core.mv_skill_lexicon")
        lex = cur.fetchone()[0]

    print(f"\n{len(stats):,} distinct labels matched on train; {n} blocked "
          f"(>= {args.min_matches} matches, precision < {args.max_precision}).")
    print("Most frequent blocked labels:", ", ".join(b[0] for b in blocked[:15]))
    print(f"Lexicon now has {lex:,} labels. Saved {CSV_PATH.relative_to(ls.PROJECT_ROOT)}")
    print("Now run: python scripts/evaluate_extraction.py")


if __name__ == "__main__":
    main()
