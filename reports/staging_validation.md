# SkillBridge staging validation report

## Rows loaded per file

rows_in_file should equal rows_loaded for every file.

| table_name | source_file | rows_in_file | rows_loaded | difference |
| --- | --- | --- | --- | --- |
| esco_broader_occupation_relations | broaderRelationsOccPillar_en.csv | 3648 | 3648 | 0 |
| esco_broader_skill_relations | broaderRelationsSkillPillar_en.csv | 20819 | 20819 | 0 |
| esco_isco_groups | ISCOGroups_en.csv | 619 | 619 | 0 |
| esco_occupation_skill_relations | occupationSkillRelations_en.csv | 126051 | 126051 | 0 |
| esco_occupations | occupations_en.csv | 3043 | 3043 | 0 |
| esco_skill_collections | digCompSkillsCollection_en.csv | 25 | 25 | 0 |
| esco_skill_collections | digitalSkillsCollection_en.csv | 1284 | 1284 | 0 |
| esco_skill_collections | greenSkillsCollection_en.csv | 629 | 629 | 0 |
| esco_skill_collections | languageSkillsCollection_en.csv | 359 | 359 | 0 |
| esco_skill_collections | researchSkillsCollection_en.csv | 40 | 40 | 0 |
| esco_skill_collections | transversalSkillsCollection_en.csv | 95 | 95 | 0 |
| esco_skill_groups | skillGroups_en.csv | 640 | 640 | 0 |
| esco_skill_skill_relations | skillSkillRelations_en.csv | 5818 | 5818 | 0 |
| esco_skills | skills_en.csv | 13960 | 13960 | 0 |
| onet_alternate_titles | job_titles_csv.csv | 54269 | 54269 | 0 |
| onet_content_model | content_model_reference_dbms.csv | 3006 | 3006 | 0 |
| onet_occupations | occupation_data_dbms.csv | 1016 | 1016 | 0 |
| onet_ratings | essential_skills_dbms.csv | 18200 | 18200 | 0 |
| onet_ratings | knowledge_dbms.csv | 60060 | 60060 | 0 |
| onet_ratings | transferable_skills_dbms.csv | 45500 | 45500 | 0 |
| onet_ratings | work_activities_dbms.csv | 74702 | 74702 | 0 |
| onet_scales | scales_reference_dbms.csv | 33 | 33 | 0 |
| onet_technology_skills | software_skills_dbms.csv | 31821 | 31821 | 0 |
| skillspan_sentences | dev_dbms.json | 3174 | 3174 | 0 |
| skillspan_sentences | test_dbms.json | 3569 | 3569 | 0 |
| skillspan_sentences | train_dbms.json | 4800 | 4800 | 0 |

## O*NET: elements per rating category

Expected: skill_basic 10, skill_cross_functional 25 (together the 35 O*NET skills), knowledge 33, work_activity 41.

| category | elements | occupations | rows |
| --- | --- | --- | --- |
| knowledge | 33 | 910 | 60060 |
| skill_basic | 10 | 910 | 18200 |
| skill_cross_functional | 25 | 910 | 45500 |
| work_activity | 41 | 911 | 74702 |

## O*NET: non-numeric Data Value

Should be 0. Any row here cannot be normalised.

_No rows (nothing to report)._

## O*NET: Data Value outside the official scale range

Compares each rating with Minimum/Maximum in scales_reference. Should be 0.

| category | scale_id | minimum | maximum | min_seen | max_seen | out_of_range |
| --- | --- | --- | --- | --- | --- | --- |
| knowledge | IM | 1 | 5 | 1.00 | 5.00 | 0 |
| knowledge | LV | 0 | 7 | 0.00 | 6.97 | 0 |
| skill_basic | IM | 1 | 5 | 1.00 | 5.00 | 0 |
| skill_basic | LV | 0 | 7 | 0.00 | 6.00 | 0 |
| skill_cross_functional | IM | 1 | 5 | 1.00 | 5.00 | 0 |
| skill_cross_functional | LV | 0 | 7 | 0.00 | 5.75 | 0 |
| work_activity | IM | 1 | 5 | 1.00 | 5.00 | 0 |
| work_activity | LV | 0 | 7 | 0.00 | 6.94 | 0 |

## O*NET: Importance rows without a matching Level row (and vice versa)

Every (occupation, element) should have both IM and LV. Should be 0.

_No rows (nothing to report)._

## O*NET: duplicate ratings

Same occupation + element + scale more than once. Should be 0.

_No rows (nothing to report)._

## O*NET: quality flags

Recommend Suppress = Y means low precision -> lower confidence. Not Relevant = Y (on LV rows) means the element is not relevant for that occupation.

| category | suppress_y | suppress_null | not_relevant_y | domain_sources |
| --- | --- | --- | --- | --- |
| knowledge | 4947 | 16434 | 6082 | 3 |
| skill_basic | 21 | 0 | 298 | 1 |
| skill_cross_functional | 136 | 0 | 3217 | 1 |
| work_activity | 1078 | 20418 | 1129 | 3 |

## O*NET: rated occupations missing from Occupation Data

Orphans: ratings whose SOC code is not in occupation_data. Should be 0.

_No rows (nothing to report)._

## O*NET: occupations with no skill ratings

Expected to be non-zero: O*NET has 1,016 occupations but only ~910 carry ratings. These cannot be target careers for gap analysis.

| occupations_without_skill_ratings |
| --- |
| 106 |

## O*NET: rated elements without a description in the Content Model

Descriptions are needed for embeddings. Should be 0.

_No rows (nothing to report)._

## O*NET Technology Skills: overview

Workplace examples are the concrete tools (Python, SQL, Excel ...).

| rows | distinct_tools | categories | occupations | hot_technology_rows | in_demand_rows |
| --- | --- | --- | --- | --- | --- |
| 31821 | 8753 | 134 | 923 | 11571 | 2425 |

## ESCO: duplicate concept URIs

The inspection found more rows than distinct URIs. 'distinct_versions' > 1 means the copies differ in some column and the transform step must choose one.

| tbl | duplicated_uris | max_copies | distinct_versions |
| --- | --- | --- | --- |
| esco_occupations | 4 | 2 | 2 |
| esco_skills | 21 | 2 | 2 |

## ESCO: example duplicated skill URIs

Look at these rows to see what differs between the copies.

| concept_uri | preferred_label | skill_type | reuse_level | modified_date |
| --- | --- | --- | --- | --- |
| http://data.europa.eu/esco/skill/11dc8e6b-dffa-42e4-9de1-c47293a848ff | operate pumping equipment | skill/competence | sector-specific | 2025-07-31T09:41:33.786Z |
| http://data.europa.eu/esco/skill/11dc8e6b-dffa-42e4-9de1-c47293a848ff | operate pumping equipment | skill/competence | sector-specific | 2025-11-26T10:07:57.331Z |
| http://data.europa.eu/esco/skill/1258cc12-37bb-4a12-b219-9c3d6b294533 | work in an organised manner | skill/competence | cross-sector | 2025-07-31T09:42:24.033Z |
| http://data.europa.eu/esco/skill/1258cc12-37bb-4a12-b219-9c3d6b294533 | work in an organised manner | skill/competence | cross-sector | 2025-11-26T10:08:15.494Z |
| http://data.europa.eu/esco/skill/1330576d-b3c7-4776-94cb-b7bd92d62993 | implement airport emergency plans | skill/competence | sector-specific | 2025-07-31T09:42:50.86Z |
| http://data.europa.eu/esco/skill/1330576d-b3c7-4776-94cb-b7bd92d62993 | implement airport emergency plans | skill/competence | sector-specific | 2025-11-26T10:08:32.133Z |

## ESCO: skills with no skill_type

Needs a rule in the transform step (e.g. take it from occupationSkillRelations).

| concept_uri | preferred_label | reuse_level |
| --- | --- | --- |
| http://data.europa.eu/esco/skill/426ceaba-6867-481c-bb6b-aee3933da7d2 | ICT safety |  |
| http://data.europa.eu/esco/skill/574257ea-7b64-4100-b7b6-e27c233fe143 | digital communication and collaboration |  |
| http://data.europa.eu/esco/skill/629685b8-5f9e-4522-8cff-b3e2c4ec625a | digital data processing |  |
| http://data.europa.eu/esco/skill/7e5147d1-60b1-4a68-804b-1f5cb0396b91 | problem-solving with digital tools |  |
| http://data.europa.eu/esco/skill/f5369f2f-e52b-43d8-8d31-79a6c11188d8 | digital content creation |  |

## ESCO: occupation-skill relations that point to unknown concepts

Orphan foreign keys. Should be 0 in both columns.

| unknown_skill_uri | unknown_occupation_uri |
| --- | --- |
| 0 | 0 |

## ESCO: relation types

essential vs optional, by skill type.

| relation_type | skill_type | rows |
| --- | --- | --- |
| essential | (null) | 39 |
| essential | knowledge | 16406 |
| essential | skill/competence | 51155 |
| optional | (null) | 20 |
| optional | knowledge | 17978 |
| optional | skill/competence | 40453 |

## ESCO: duplicate occupation-skill pairs

Same occupation + skill listed more than once. Should be 0.

| duplicate_pairs |
| --- |
| 0 |

## ESCO: broader (parent) links that point to unknown concepts

Parents should be a skill or a skill group. Should be 0.

| unknown_parent |
| --- |
| 0 |

## ESCO: skills per reuse level

transversal / cross-sector skills are the most likely to transfer between careers.

| reuse_level | skills |
| --- | --- |
| sector-specific | 6655 |
| cross-sector | 3783 |
| occupation-specific | 3044 |
| transversal | 452 |
| (null) | 5 |

## ESCO: collection sizes

| collection | skills |
| --- | --- |
| digital | 1284 |
| green | 629 |
| language | 359 |
| transversal | 95 |
| research | 40 |
| digcomp | 25 |

## SkillSpan: sentences per split and source

Use these counts in the paper's dataset table.

| split | source | sentences | tokens |
| --- | --- | --- | --- |
| dev | house | 1018 | 19156 |
| dev | tech | 2156 | 20901 |
| test | house | 1283 | 22573 |
| test | tech | 2286 | 20213 |
| train | house | 1667 | 36968 |
| train | tech | 3133 | 56485 |

## SkillSpan: token/tag length mismatches

Every sentence needs one skill tag and one knowledge tag per token. Should be 0.

_No rows (nothing to report)._

## SkillSpan: long sentences

Sentences over 200 tokens will need splitting or truncation before a 512-subword BERT model.

| split | over_200_tokens | longest |
| --- | --- | --- |
| train | 18 | 748 |
