# SkillBridge performance benchmark

- PostgreSQL 16.16
- Median of 7 warm runs per query

Data size: 4,055 careers · 22,796 skills · 254,059 evidence rows · 21,699 skill relations · 101,578 lexicon labels

## 1. Latency of core operations (Data Scientists)

| Operation | Median (ms) | Max (ms) | Rows |
| --- | --- | --- | --- |
| Provenance lookup (v_evidence_detail, one career) | 5.6 | 5.9 | 193 |
| Aggregated requirements (v_career_skill_requirement) | 2.8 | 3.1 | 193 |
| Gap analysis, baseline (fn_gap_analysis, no transfer) | 5.5 | 5.9 | 89 |
| Gap analysis with directional transfer | 6.0 | 6.7 | 89 |
| Readiness for all target careers (fn_readiness x targets) | 67.0 | 73.7 | 23 |
| Skill extraction from a job ad (fn_extract_from_text, exact) | 2.2 | 3.1 | 12 |
| Skill extraction from a job ad (exact + fuzzy) | 97.9 | 105.4 | 13 |
| Roadmap generation incl. snapshot + storage (fn_build_roadmap) | 22.3 | 27.0 | 1 |

## 2. Index effect: all evidence for one skill

`SELECT * FROM career_skill_evidence WHERE skill_id = ?` measured with EXPLAIN ANALYZE.

| Plan | Node | Median execution (ms) |
| --- | --- | --- |
| With index on skill_id | Index Scan | 0.07 |
| Indexes disabled | Gather | 37.16 |

Speed-up from the index: **531x**.

## 3. RQ3: cost of the cycle-checking trigger as the graph grows

A chain of prerequisite edges is inserted one at a time (each insert runs the advisory lock and the recursive reachability check). Rolled back afterwards.

| Edges already in graph | Median insert latency (ms) | Cycle attempt rejected in (ms) |
| --- | --- | --- |
| 10 | 0.23 | 0.5 |
| 100 | 0.91 | 1.2 |
| 250 | 4.38 | 5.2 |
| 500 | 51.12 | 49.8 |
| 1,000 | 197.92 | 186.0 |
| 2,000 | 745.36 | 794.5 |

The worst case is a long chain, because the check must walk the whole path. Curated prerequisite graphs are shallow (a few layers), so real inserts stay near the first row.
