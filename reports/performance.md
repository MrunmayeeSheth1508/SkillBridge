# SkillBridge performance benchmark

- PostgreSQL 16.16
- Median of 7 warm runs per query

Data size: 4,055 careers · 22,796 skills · 254,059 evidence rows · 21,699 skill relations · 101,512 lexicon labels

## 1. Latency of core operations (Data Scientists)

| Operation | Median (ms) | Max (ms) | Rows |
| --- | --- | --- | --- |
| Provenance lookup (v_evidence_detail, one career) | 5.1 | 5.3 | 193 |
| Aggregated requirements (v_career_skill_requirement) | 3.1 | 3.4 | 193 |
| Gap analysis, baseline (fn_gap_analysis, no transfer) | 5.2 | 5.6 | 52 |
| Gap analysis with directional transfer | 5.2 | 5.5 | 52 |
| Readiness for all target careers (fn_readiness x targets) | 60.3 | 70.4 | 23 |
| Skill extraction from a job ad (fn_extract_from_text, exact) | 2.6 | 3.9 | 12 |
| Skill extraction from a job ad (exact + fuzzy) | 91.1 | 102.8 | 13 |
| Roadmap generation incl. snapshot + storage (fn_build_roadmap) | 18.7 | 25.3 | 1 |

## 2. Index effect: all evidence for one skill

`SELECT * FROM career_skill_evidence WHERE skill_id = ?` measured with EXPLAIN ANALYZE.

| Plan | Node | Median execution (ms) |
| --- | --- | --- |
| With index on skill_id | Index Scan | 0.07 |
| Indexes disabled | Gather | 41.18 |

Speed-up from the index: **588x**.

## 3. RQ3: cost of the cycle-checking trigger as the graph grows

A chain of prerequisite edges is inserted one at a time (each insert runs the advisory lock and the recursive reachability check). Rolled back afterwards.

| Edges already in graph | Median insert latency (ms) | Cycle attempt rejected in (ms) |
| --- | --- | --- |
| 10 | 0.32 | 0.5 |
| 100 | 0.32 | 0.7 |
| 250 | 1.53 | 1.8 |
| 500 | 18.97 | 16.5 |
| 1,000 | 74.50 | 67.6 |
| 2,000 | 268.67 | 316.0 |

The worst case is a long chain, because the check must walk the whole path. Curated prerequisite graphs are shallow (a few layers), so real inserts stay near the first row.
