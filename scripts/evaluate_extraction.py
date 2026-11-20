"""
SkillBridge - evaluate the in-database skill extractor on SkillSpan.

    python scripts/evaluate_extraction.py                 # test split, exact matching
    python scripts/evaluate_extraction.py --fuzzy         # exact + trigram fuzzy matching
    python scripts/evaluate_extraction.py --split dev --limit 500

Predictions come from core.fn_extract_skills() running inside PostgreSQL over
the SkillSpan sentences already loaded in staging.skillspan_sentences.
Gold spans come from the BIO tags (tags_skill, tags_knowledge).

Metrics (span level, as in the SkillSpan paper):
  strict : predicted span boundaries identical to a gold span
  loose  : predicted span overlaps a gold span by at least one token
Reported for all spans together, per SkillSpan subset (house / tech) and
per span type (skill vs knowledge; technologies count as knowledge).

Writes reports/extraction_eval.md
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_staging as ls  # noqa: E402  (also fixes the Windows libpq PATH)

import psycopg  # noqa: E402

REPORT = ls.PROJECT_ROOT / "reports" / "extraction_eval.md"
TYPE_MAP = {"skill": "skill", "knowledge": "knowledge", "technology": "knowledge"}


def bio_spans(tags: list[str]) -> list[tuple[int, int]]:
    """BIO tags -> list of (start, end), 1-based inclusive (matches SQL)."""
    spans, start = [], None
    for i, t in enumerate(tags, start=1):
        if t == "B" or (t == "I" and start is None):
            if start is not None:
                spans.append((start, i - 1))
            start = i
        elif t == "O":
            if start is not None:
                spans.append((start, i - 1))
            start = None
    if start is not None:
        spans.append((start, len(tags)))
    return spans


def overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


class Score:
    def __init__(self) -> None:
        self.n_pred = self.n_gold = 0
        self.strict_tp = self.loose_pred_tp = self.loose_gold_tp = 0

    def add(self, preds: list[tuple[int, int]], golds: list[tuple[int, int]]) -> None:
        self.n_pred += len(preds)
        self.n_gold += len(golds)
        gold_set = set(golds)
        self.strict_tp += sum(1 for p in preds if p in gold_set)
        self.loose_pred_tp += sum(1 for p in preds if any(overlaps(p, g) for g in golds))
        self.loose_gold_tp += sum(1 for g in golds if any(overlaps(p, g) for p in preds))

    @staticmethod
    def _prf(tp_p: int, n_p: int, tp_g: int, n_g: int) -> tuple[float, float, float]:
        p = tp_p / n_p if n_p else 0.0
        r = tp_g / n_g if n_g else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        return p, r, f

    def strict(self):
        return self._prf(self.strict_tp, self.n_pred, self.strict_tp, self.n_gold)

    def loose(self):
        return self._prf(self.loose_pred_tp, self.n_pred, self.loose_gold_tp, self.n_gold)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["train", "dev", "test"])
    ap.add_argument("--fuzzy", action="store_true", help="also use trigram fuzzy matching (slower)")
    ap.add_argument("--limit", type=int, default=None, help="evaluate only the first N sentences")
    args = ap.parse_args()

    url = ls.get_database_url()
    t0 = time.time()
    with psycopg.connect(url) as conn:
        cur = conn.cursor()
        limit_sql = f"LIMIT {int(args.limit)}" if args.limit else ""
        cur.execute(f"""
            SELECT sentence_id, source, tokens, tags_skill, tags_knowledge
            FROM staging.skillspan_sentences
            WHERE split = %s ORDER BY sentence_id {limit_sql}""", (args.split,))
        sentences = cur.fetchall()
        if not sentences:
            sys.exit(f"No SkillSpan sentences for split '{args.split}'. Run build_database.py first.")

        print(f"Extracting skills from {len(sentences):,} {args.split} sentences "
              f"({'exact + fuzzy' if args.fuzzy else 'exact'}) inside PostgreSQL ...")
        cur.execute(f"""
            SELECT s.sentence_id, x.start_tok, x.end_tok, x.span_text, x.skill, x.skill_type, x.method
            FROM (SELECT sentence_id, tokens FROM staging.skillspan_sentences
                  WHERE split = %s ORDER BY sentence_id {limit_sql}) s
            CROSS JOIN LATERAL core.fn_extract_skills(
                ARRAY(SELECT jsonb_array_elements_text(s.tokens)), %s) x""",
                    (args.split, args.fuzzy))
        rows = cur.fetchall()
        cur.execute("SELECT version()")
        pg_version = cur.fetchone()[0].split(",")[0]
        cur.execute("SELECT (SELECT COUNT(*) FROM core.mv_skill_lexicon), (SELECT COUNT(*) FROM core.lexicon_blocklist)")
        n_lex, n_block = cur.fetchone()
    elapsed = time.time() - t0

    preds_by_sent: dict[int, list] = defaultdict(list)
    for idx, s, e, text, skill, stype, method in rows:
        preds_by_sent[idx].append(((s, e), text, skill, TYPE_MAP.get(stype, "skill"), method))

    overall, by_source, by_type = Score(), defaultdict(Score), defaultdict(Score)
    fp_counter: Counter = Counter()
    fn_counter: Counter = Counter()
    tp_examples: Counter = Counter()

    for idx, source, tokens, tags_skill, tags_knowledge in sentences:
        tokens = tokens if isinstance(tokens, list) else json.loads(tokens)
        gold_s = bio_spans(tags_skill if isinstance(tags_skill, list) else json.loads(tags_skill))
        gold_k = bio_spans(tags_knowledge if isinstance(tags_knowledge, list) else json.loads(tags_knowledge))
        gold_all = sorted(set(gold_s) | set(gold_k))
        preds = preds_by_sent.get(idx, [])
        pred_spans = [p[0] for p in preds]

        overall.add(pred_spans, gold_all)
        by_source[source or "unknown"].add(pred_spans, gold_all)
        by_type["skill"].add([p[0] for p in preds if p[3] == "skill"], gold_s)
        by_type["knowledge"].add([p[0] for p in preds if p[3] == "knowledge"], gold_k)

        for span, text, skill, _, _ in preds:
            if any(overlaps(span, g) for g in gold_all):
                tp_examples[f"{text} -> {skill}"] += 1
            else:
                fp_counter[f"{text} -> {skill}"] += 1
        for g in gold_all:
            if not any(overlaps(p, g) for p in pred_spans):
                fn_counter[" ".join(tokens[g[0] - 1:g[1]])] += 1

    def row(name: str, sc: Score) -> str:
        sp, sr, sf = sc.strict()
        lp, lr, lf = sc.loose()
        return (f"| {name} | {sc.n_gold:,} | {sc.n_pred:,} | {sp:.3f} | {sr:.3f} | **{sf:.3f}** "
                f"| {lp:.3f} | {lr:.3f} | **{lf:.3f}** |")

    header = ("| Subset | Gold spans | Predicted | Strict P | Strict R | Strict F1 "
              "| Loose P | Loose R | Loose F1 |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    mode = "exact + fuzzy (pg_trgm)" if args.fuzzy else "exact"
    lines = [
        "# SkillBridge skill extraction - SkillSpan evaluation", "",
        f"- Split: **{args.split}**, sentences: **{len(sentences):,}**"
        + (f" (first {args.limit})" if args.limit else ""),
        f"- Matching: **{mode}**, lexicon `core.mv_skill_lexicon`: {n_lex:,} O*NET + ESCO labels, "
        f"{n_block} pruned using the train split",
        f"- Runtime: **{elapsed:.1f} s** inside PostgreSQL "
        f"({1000 * elapsed / max(len(sentences), 1):.1f} ms per sentence), {pg_version}",
        "", "Strict = identical span boundaries; Loose = at least one token overlap.", "",
        "## Overall and per SkillSpan subset", "", header, row("All spans", overall),
    ]
    lines += [row(src, sc) for src, sc in sorted(by_source.items())]
    lines += ["", "## Per span type", "",
              "Technologies from O*NET are counted as *knowledge*, matching SkillSpan's guidelines.", "",
              header.replace("Subset", "Type")]
    lines += [row(t, by_type[t]) for t in ("skill", "knowledge")]
    lines += ["", "## Most frequent correct matches", "", "| Match | Count |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in tp_examples.most_common(15)]
    lines += ["", "## Most frequent false positives (no overlap with any gold span)", "",
              "| Prediction | Count |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in fp_counter.most_common(15)]
    lines += ["", "## Most frequent missed gold spans", "", "| Gold span | Count |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in fn_counter.most_common(15)]
    lines += ["", "## Reading these results", "",
              "This is a lexicon baseline: it can only find skills whose wording (or a close spelling) "
              "exists in O*NET/ESCO. SkillSpan annotates long, free-form spans such as "
              "*\"work independently in a fast-paced environment\"*, so strict recall is expected to be "
              "low and loose scores higher. The trained span tagger (Phase 5b) is compared against "
              "this baseline in the paper."]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    sp, sr, sf = overall.strict()
    lp, lr, lf = overall.loose()
    print(f"\nAll spans  strict P/R/F1 = {sp:.3f} / {sr:.3f} / {sf:.3f}")
    print(f"           loose  P/R/F1 = {lp:.3f} / {lr:.3f} / {lf:.3f}")
    print(f"Done in {elapsed:.1f} s. Report: {REPORT.relative_to(ls.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()