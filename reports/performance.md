# SkillBridge performance benchmark

- PostgreSQL 16.16
- Median of 7 warm runs per query

Data size: 4,055 careers · 22,796 skills · 321,618 evidence rows · 21,699 skill relations · 100,697 lexicon labels

## 1. Latency of core operations (Data Scientists)

| Operation | Median (ms) | Max (ms) | Rows |
| --- | --- | --- | --- |
| Provenance lookup (v_evidence_detail, one career) | 14.0 | 18.1 | 426 |
| Aggregated requirements (v_career_skill_requirement) | 7.3 | 8.3 | 416 |
| Gap analysis, baseline (fn_gap_analysis, no transfer) | 10.5 | 14.0 | 173 |
| Gap analysis with directional transfer | 9.8 | 10.6 | 173 |
| Readiness for all target careers (fn_readiness x targets) | 82.8 | 89.1 | 24 |
| Skill extraction from a job ad (fn_extract_from_text, exact) | 2.4 | 3.6 | 12 |
| Skill extraction from a job ad (exact + fuzzy) | 90.3 | 112.1 | 13 |
| Roadmap generation incl. snapshot + storage (fn_build_roadmap) | 27.9 | 36.6 | 1 |

## 2. Index effect: all evidence for one skill

`SELECT * FROM career_skill_evidence WHERE skill_id = ?` measured with EXPLAIN ANALYZE.

| Plan | Node | Median execution (ms) |
| --- | --- | --- |
| With index on skill_id | Index Scan | 0.08 |
| Indexes disabled | Gather | 33.03 |

Speed-up from the index: **429x**.

## 3. RQ3: cost of the cycle-checking trigger as the graph grows

A chain of prerequisite edges is inserted one at a time (each insert runs the advisory lock and the recursive reachability check). Rolled back afterwards.

| Edges already in graph | Median insert latency (ms) | Cycle attempt rejected in (ms) |
| --- | --- | --- |
| 10 | 0.26 | 0.5 |
| 100 | 0.13 | 0.4 |
| 250 | 0.29 | 0.5 |
| 500 | 0.53 | 0.7 |
| 1,000 | 1.06 | 1.3 |
| 2,000 | 4.12 | 1.9 |

The worst case is a long chain, because the check must walk the whole path. Curated prerequisite graphs are shallow (a few layers), so real inserts stay near the first row.
