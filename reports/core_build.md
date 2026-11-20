# SkillBridge core database build report

Build time: 150 s

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
| Transfer credit never lowers readiness | yes | Logistics Analysts: baseline 0.0623, transfer-aware 0.1259 |
| Gap values consistent (0 <= gap <= importance) | yes | 0 inconsistent rows |
| Roadmap respects prerequisites | yes | 13 items, 447.7 h, 56 weeks at 8 h/week, 0 violations |
| Skill extraction finds skills in a job ad | yes | lexicon 100,697 labels; found: Python, Structured query language SQL, Scikit-learn, Mathem |
| Approved extraction becomes Job-postings evidence (trigger) | yes | 1 evidence row(s) |
| RLS: learner sees only own skills | yes | table holds 2 learners' skills; learner role sees 1 |
| Learner cannot read password hashes | yes | permission denied for table users |
| Learner cannot change evidence | yes | permission denied for table career_skill_evidence |
| Crosswalk gives target careers ESCO evidence | yes | 4,207 links; 24/24 target careers have ESCO evidence; 1,406 career-skill pairs with 2+ sou |

## Build notes

- 38 prerequisite edges loaded
- demo learner user_id=1
- Crosswalk `ONET_(Ocuupations)_0_updated.csv`: columns detected -> O*NET `Mapping project name`, ESCO `Unnamed: 3`, type `Unnamed: 6`; 4,210 usable rows (broad 2,053, close 1,432, exact 498, narrow 227)
- Crosswalk applied: 4,207 links for 940 O*NET careers; 114,809 ESCO evidence rows attached; 1,406 career-skill pairs now have 2+ sources
- 53 lexicon labels blocked (learned on SkillSpan train)

## Rows per core table

| table_name | rows |
| --- | --- |
| career_skill_evidence | 368868 |
| career_source_codes | 8262 |
| careers | 4055 |
| data_sources | 4 |
| extraction_candidates | 0 |
| gap_snapshots | 0 |
| learning_resources | 0 |
| lexicon_blocklist | 53 |
| model_parameters | 28 |
| mv_skill_lexicon | 100697 |
| resource_skills | 0 |
| roadmap_items | 0 |
| roadmaps | 0 |
| skill_aliases | 110797 |
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
| O*NET | 1016 | 910 | 24 |

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
| ESCO | essential | 128718 | 0.800 | 0.746 |
| ESCO | optional | 112083 | 0.400 | 0.744 |
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
| Business & finance analytics | Actuaries | 15-2011.00 | 210 | 102 | 42 |
| Business & finance analytics | Credit Analysts | 13-2041.00 | 266 | 102 | 41 |
| Business & finance analytics | Financial Quantitative Analysts | 13-2099.01 | 250 | 104 | 36 |
| Business & finance analytics | Logistics Analysts | 13-1081.02 | 239 | 104 | 53 |
| Business & finance analytics | Management Analysts | 13-1111.00 | 406 | 106 | 216 |
| Business & finance analytics | Market Research Analysts and Marketing Specialists | 13-1161.00 | 534 | 102 | 149 |
| Data & AI | Computer and Information Research Scientists | 15-1221.00 | 376 | 108 | 164 |
| Data & AI | Data Scientists | 15-2051.00 | 440 | 106 | 87 |
| Data & AI | Database Administrators | 15-1242.00 | 593 | 108 | 288 |
| Data & AI | Database Architects | 15-1243.00 | 605 | 108 | 322 |
| Data & AI | Operations Research Analysts | 15-2031.00 | 383 | 104 | 114 |
| Data & AI | Statisticians | 15-2041.00 | 331 | 102 | 70 |
| Mechanical & manufacturing engineering | Automotive Engineers | 17-2141.02 | 456 | 106 | 87 |
| Mechanical & manufacturing engineering | Industrial Engineers | 17-2112.00 | 381 | 106 | 102 |
| Mechanical & manufacturing engineering | Manufacturing Engineers | 17-2112.03 | 339 | 108 | 34 |
| Mechanical & manufacturing engineering | Mechanical Engineering Technologists and Technicians | 17-3027.00 | 325 | 109 | 44 |
| Mechanical & manufacturing engineering | Mechanical Engineers | 17-2141.00 | 371 | 108 | 92 |
| Mechanical & manufacturing engineering | Robotics Engineers | 17-2199.08 | 337 | 109 | 67 |
| Software engineering | Computer Systems Analysts | 15-1211.00 | 638 | 107 | 311 |
| Software engineering | Network and Computer Systems Administrators | 15-1244.00 | 534 | 107 | 261 |
| Software engineering | Software Developers | 15-1252.00 | 876 | 107 | 430 |
| Software engineering | Software Quality Assurance Analysts and Testers | 15-1253.00 | 725 | 108 | 429 |
| Software engineering | Web and Digital Interface Designers | 15-1255.00 | 496 | 103 | 236 |
| Software engineering | Web Developers | 15-1254.00 | 495 | 105 | 251 |

## Starter-list codes that did not become targets

_No rows._

## Excluded during transform

| what | rows |
| --- | --- |
| ESCO relations to non-skill concepts | 59 |
| O*NET ratings not relevant at minimum importance | 2985 |

## Crosswalk links by match type

| match_type | links | onet_careers |
| --- | --- | --- |
| broad | 2053 | 540 |
| close | 1429 | 624 |
| exact | 498 | 490 |
| narrow | 227 | 196 |

## Contribution 1: strongest O*NET vs ESCO tier disagreements (target careers)

| career | skill | onet_type | onet_tier | esco_type | esco_tier |
| --- | --- | --- | --- | --- | --- |
| Industrial Engineers | Troubleshooting | scored | 1 | essential | 3 |
| Computer Systems Analysts | Git | present | 2 | essential | 3 |
| Computer Systems Analysts | Python | present | 3 | optional | 2 |
| Data Scientists | Apache Hadoop | present | 3 | optional | 2 |
| Data Scientists | C++ | present | 3 | optional | 2 |
| Data Scientists | Operations Analysis | scored | 1 | optional | 2 |
| Data Scientists | R | present | 3 | optional | 2 |
| Database Administrators | Microsoft Access | present | 3 | optional | 2 |
| Database Administrators | MySQL | present | 3 | optional | 2 |
| Database Administrators | PostgreSQL | present | 3 | optional | 2 |
| Database Administrators | Python | present | 3 | optional | 2 |
| Database Administrators | Scala | present | 3 | optional | 2 |
| Database Architects | CloverETL | present | 2 | essential | 3 |
| Database Architects | Database management systems | present | 2 | essential | 3 |
| Database Architects | Python | present | 3 | optional | 2 |
| Logistics Analysts | Operations Analysis | scored | 1 | optional | 2 |
| Manufacturing Engineers | Mathematics | scored | 3 | optional | 2 |
| Market Research Analysts and Marketing Specialists | Geography | scored | 1 | optional | 2 |
| Mechanical Engineering Technologists and Technicians | Physics | scored | 2 | essential | 3 |
| Mechanical Engineering Technologists and Technicians | Troubleshooting | scored | 2 | essential | 3 |

## Demo: top 20 requirements for Data Scientists

| skill | taxonomy | source | importance | level_norm | requirement_type | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Tableau | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Structured query language SQL | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| R | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| PyTorch | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Snowflake | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Scikit-learn | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft PowerPoint | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Power BI | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| pandas | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Python | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| C++ | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| SAS | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Apache Hadoop | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Apache Spark | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Azure software | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Git | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Microsoft Excel | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| Amazon Web Services AWS software | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| NumPy | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
| TensorFlow | onet_technology | O*NET | 0.9000 |  | present | 0.70 |
