# SkillBridge core database build report

Build time: 127 s

## Integrity self-tests

| Test | Passed | Detail |
| --- | --- | --- |
| Valid chain a->b->c accepted | yes | ok |
| Self-dependency rejected | yes | new row for relation "skill_prerequisites" violates check constraint "skill_prerequisites_ |
| Direct cycle b->a rejected | yes | Prerequisite rejected: skill 2 before skill 1 would create a cycle |
| Transitive cycle c->a rejected | yes | Prerequisite rejected: skill 3 before skill 1 would create a cycle |
| Proficiency 1.5 rejected | yes | new row for relation "user_skills" violates check constraint "user_skills_proficiency_chec |
| Duplicate evidence from the same source rejected | yes | duplicate key value violates unique constraint "career_skill_evidence_career_id_skill_id_s |
| Proficiency history recorded (insert + update) | yes | 2 history rows |
| Directional transfer edges built | yes | 9204 edges; 2310 have a different weight in the reverse direction |
| Transfer credit never lowers readiness | yes | Logistics Analysts: baseline 0.1269, transfer-aware 0.2585 |
| Gap values consistent (0 <= gap <= importance) | yes | 0 inconsistent rows |
| Roadmap respects prerequisites | yes | 13 items, 358.5 h, 45 weeks at 8 h/week, 0 violations |
| Skill extraction finds skills in a job ad | yes | lexicon 101,575 labels; found: Python, Structured query language SQL, Scikit-learn, Mathem |
| Approved extraction becomes Job-postings evidence (trigger) | yes | 1 evidence row(s) |
| RLS: learner sees only own skills | yes | table holds 2 learners' skills; learner role sees 1 |
| Learner cannot read password hashes | yes | permission denied for table users |
| Learner cannot change evidence | yes | permission denied for table career_skill_evidence |

## Build notes

- 38 prerequisite edges loaded
- demo learner user_id=1
- 0 lexicon labels blocked (learned on SkillSpan train)

## Rows per core table

| table_name | rows |
| --- | --- |
| career_skill_evidence | 254059 |
| career_source_codes | 4055 |
| careers | 4055 |
| data_sources | 4 |
| extraction_candidates | 0 |
| gap_snapshots | 0 |
| learning_resources | 0 |
| lexicon_blocklist | 0 |
| model_parameters | 24 |
| mv_skill_lexicon | 101575 |
| resource_skills | 0 |
| roadmap_items | 0 |
| roadmaps | 0 |
| skill_aliases | 111619 |
| skill_prerequisites | 38 |
| skill_similarity | 21699 |
| skills | 22796 |
| user_skill_history | 17 |
| user_skills | 17 |
| users | 3 |

## Careers by source

| source_name | careers | with_onet_ratings | targets |
| --- | --- | --- | --- |
| ESCO | 3039 | 0 | 0 |
| O*NET | 1016 | 910 | 23 |

## Skills by taxonomy

| taxonomy | skill_type | skills |
| --- | --- | --- |
| esco | knowledge | 3219 |
| esco | skill | 10715 |
| onet_knowledge | knowledge | 33 |
| onet_skill | skill | 35 |
| onet_technology | technology | 8753 |
| onet_work_activity | work_activity | 41 |

## Evidence by source and type

| source_name | requirement_type | rows | avg_importance | avg_confidence |
| --- | --- | --- | --- | --- |
| ESCO | essential | 67561 | 0.800 | 0.800 |
| ESCO | optional | 58431 | 0.400 | 0.800 |
| O*NET | present | 31821 | 0.682 | 0.700 |
| O*NET | scored | 96246 | 0.441 | 0.969 |

## Skill relationships seeded

| method | edges |
| --- | --- |
| esco_broader | 6440 |
| esco_relation_essential | 189 |
| esco_relation_optional | 5628 |
| exact_label | 238 |
| transfer_v0 | 9204 |

## Target careers (4 domains)

| domain | title | origin_code | evidence_rows | scored | technologies |
| --- | --- | --- | --- | --- | --- |
| Business & finance analytics | Actuaries | 15-2011.00 | 144 | 102 | 42 |
| Business & finance analytics | Credit Analysts | 13-2041.00 | 143 | 102 | 41 |
| Business & finance analytics | Logistics Analysts | 13-1081.02 | 157 | 104 | 53 |
| Business & finance analytics | Management Analysts | 13-1111.00 | 322 | 106 | 216 |
| Business & finance analytics | Market Research Analysts and Marketing Specialists | 13-1161.00 | 251 | 102 | 149 |
| Data & AI | Computer and Information Research Scientists | 15-1221.00 | 272 | 108 | 164 |
| Data & AI | Data Scientists | 15-2051.00 | 193 | 106 | 87 |
| Data & AI | Database Administrators | 15-1242.00 | 396 | 108 | 288 |
| Data & AI | Database Architects | 15-1243.00 | 430 | 108 | 322 |
| Data & AI | Operations Research Analysts | 15-2031.00 | 218 | 104 | 114 |
| Data & AI | Statisticians | 15-2041.00 | 172 | 102 | 70 |
| Mechanical & manufacturing engineering | Automotive Engineers | 17-2141.02 | 193 | 106 | 87 |
| Mechanical & manufacturing engineering | Industrial Engineers | 17-2112.00 | 208 | 106 | 102 |
| Mechanical & manufacturing engineering | Manufacturing Engineers | 17-2112.03 | 142 | 108 | 34 |
| Mechanical & manufacturing engineering | Mechanical Engineering Technologists and Technicians | 17-3027.00 | 153 | 109 | 44 |
| Mechanical & manufacturing engineering | Mechanical Engineers | 17-2141.00 | 200 | 108 | 92 |
| Mechanical & manufacturing engineering | Robotics Engineers | 17-2199.08 | 176 | 109 | 67 |
| Software engineering | Computer Systems Analysts | 15-1211.00 | 418 | 107 | 311 |
| Software engineering | Network and Computer Systems Administrators | 15-1244.00 | 368 | 107 | 261 |
| Software engineering | Software Developers | 15-1252.00 | 537 | 107 | 430 |
| Software engineering | Software Quality Assurance Analysts and Testers | 15-1253.00 | 537 | 108 | 429 |
| Software engineering | Web and Digital Interface Designers | 15-1255.00 | 339 | 103 | 236 |
| Software engineering | Web Developers | 15-1254.00 | 356 | 105 | 251 |

## Starter-list codes that did not become targets

| origin_code | title | has_ratings |
| --- | --- | --- |
| 13-2051.00 | Financial and Investment Analysts | False |

## Excluded during transform

| what | rows |
| --- | --- |
| ESCO relations to non-skill concepts | 59 |
| O*NET ratings not relevant at minimum importance | 2985 |

## Demo: top 20 requirements for Data Scientists

| skill | taxonomy | source | importance | level_norm | requirement_type | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Tableau | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Structured query language SQL | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Power BI | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Python | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| R | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Snowflake | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Git | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Excel | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| pandas | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| NumPy | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Apache Spark | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| PyTorch | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Scikit-learn | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| SAS | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| C++ | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Apache Hadoop | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Amazon Web Services AWS software | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Azure software | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft PowerPoint | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| TensorFlow | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
