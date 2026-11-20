# SkillBridge dataset inspection report

Files found: 12

## dev_dbms.json

- Records: **3,174**
- Keys (record count): {'idx': 3174, 'tokens': 3174, 'tags_skill': 3174, 'tags_knowledge': 3174, 'source': 3174}
- `tags_skill` vocabulary: {'O': 35190, 'I': 3797, 'B': 1070}
- `tags_knowledge` vocabulary: {'O': 38051, 'B': 1093, 'I': 913}
- `tokens` length: min 1, max 80, mean 12.6

Example record:

```json
{"idx": 1, "tokens": ["DevOps", "Engineer", "(", "CI", "CD", "Cloud", "Docker", "Jenkins", ")", "<ORGANIZATION>"], "tags_skill": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "tags_knowledge": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "source": "tech"}
```

# ZIP: ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip

Members (42):

- occupations_en.csv
- dictionary_en.csv
- skills_en.csv
- ISCOGroups_en.csv
- skillGroups_en.csv
- broaderRelationsOccPillar_en.csv
- broaderRelationsSkillPillar_en.csv
- occupationSkillRelations_en.csv
- transversalSkillsCollection_en.csv
- languageSkillsCollection_en.csv
- skillSkillRelations_en.csv
- conceptSchemes_en.csv
- digCompSkillsCollection_en.csv
- greenSkillsCollection_en.csv
- researchSkillsCollection_en.csv
- digitalSkillsCollection_en.csv
- researchOccupationsCollection_en.csv
- skillsHierarchy_en.csv
- greenShareOcc_en.csv
- Component_2_Requirement_Specification.pdf
- Component_3_ER_Diagram_and_Schema.pdf
- content_model_reference_dbms.csv
- DBMS_Synopsis_Skill_Gap_Analysis.pdf
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/broaderRelationsOccPillar_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/broaderRelationsSkillPillar_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/conceptSchemes_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/dictionary_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/digCompSkillsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/digitalSkillsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/greenShareOcc_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/greenSkillsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/ISCOGroups_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/languageSkillsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/occupations_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/occupationSkillRelations_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/researchOccupationsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/researchSkillsCollection_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillGroups_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/skills_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillsHierarchy_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillSkillRelations_en.csv
- ESCO dataset - v1.2.1 - classification - en - csv_dbms/transversalSkillsCollection_en.csv

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: occupations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,043** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | Occupation |
| conceptUri | str | 0 | 0.0 | 3,039 | http://data.europa.eu/esco/occupation/00030d09-2b3a-4efd-87c |
| iscoGroup | int64 | 0 | 0.0 | 426 | 2654 |
| preferredLabel | str | 0 | 0.0 | 3,039 | technical director |
| altLabels | str | 0 | 0.0 | 3,039 | director of technical arts
technical supervisor
head of tech |
| hiddenLabels | str | 3,035 | 99.7 | 8 | sexual health consultant
youth policy manager
youth operator |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 0 | 0.0 | 2,902 | 2024-01-25T11:28:50.295Z |
| regulatedProfessionNote | str | 0 | 0.0 | 2 | http://data.europa.eu/esco/regulated-professions/unregulated |
| scopeNote | str | 2,733 | 89.8 | 274 | Excludes people performing analysis of blood samples, cell c |
| definition | str | 3,035 | 99.7 | 8 | Excludes choreologist. |
| inScheme | str | 0 | 0.0 | 2 | http://data.europa.eu/esco/concept-scheme/member-occupations |
| description | str | 0 | 0.0 | 3,039 | Technical directors realise the artistic visions of the crea |
| code | str | 0 | 0.0 | 3,039 | 2654.1.7 |
| naceCode | str | 0 | 0.0 | 1,121 | http://data.europa.eu/ux2/nace2.1/9031 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                                         conceptUri  iscoGroup                  preferredLabel                                          altLabels hiddenLabels    status              modifiedDate                            regulatedProfessionNote scopeNote definition                                           inScheme                                        description       code                                naceCode
0  Occupation  http://data.europa.eu/esco/occupation/00030d09...       2654              technical director  director of technical arts\ntechnical supervis...          NaN  released  2024-01-25T11:28:50.295Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Technical directors realise the artistic visio...   2654.1.7  http://data.europa.eu/ux2/nace2.1/9031
1  Occupation  http://data.europa.eu/esco/occupation/000e93a3...       8121  metal drawing machine operator  wire drawer\nforming machine operative\ndraw m...          NaN  released  2024-01-23T10:09:32.099Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Metal drawing machine operators set up and ope...     8121.4   http://data.europa.eu/ux2/nace2.1/242
2  Occupation  http://data.europa.eu/esco/occupation/0019b951...       7543      precision device inspector  precision device quality control supervisor\np...          NaN  released  2024-01-25T15:00:12.188Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Precision device inspectors make sure precisio...  7543.10.3  http://data.europa.eu/ux2/nace2.1/2651
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: dictionary_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **160** | Columns: **4**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| filename | str | 0 | 0.0 | 18 | occupations |
| data header | str | 0 | 0.0 | 50 | conceptType |
| property | str | 47 | 29.4 | 18 | http://www.w3.org/2004/02/skos/core#notation |
| description | str | 0 | 0.0 | 19 | No direct related property exists |

- Candidate single-column keys: none

Sample rows:

```
      filename  data header                                      property                                        description
0  occupations  conceptType                                           NaN                  No direct related property exists
1  occupations   conceptUri                                           NaN                  No direct related property exists
2  occupations    iscoGroup  http://www.w3.org/2004/02/skos/core#notation  A notation, also known as classification code,...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: skills_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **13,960** | Columns: **13**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 13,939 | http://data.europa.eu/esco/skill/0005c151-5b5a-4a66-8aac-60e |
| skillType | str | 5 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 5 | 0.0 | 4 | sector-specific |
| preferredLabel | str | 0 | 0.0 | 13,939 | manage musical staff |
| altLabels | str | 18 | 0.1 | 13,918 | manage music staff
coordinate duties of musical staff
direct |
| hiddenLabels | str | 13,807 | 98.9 | 153 | active participation
activity
initiative
great initiative
se |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 0 | 0.0 | 2,669 | 2023-11-30T15:53:37.136Z |
| scopeNote | str | 13,724 | 98.3 | 224 | It includes building stone, sand, bricks, clay and gravel. |
| definition | str | 13,958 | 100.0 | 2 | Bilingual examination of target language content against sou |
| inScheme | str | 0 | 0.0 | 15 | http://data.europa.eu/esco/concept-scheme/skills,
http://dat |
| description | str | 0 | 0.0 | 13,935 | Assign and manage staff tasks in areas such as scoring, arra |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType           reuseLevel                     preferredLabel                                          altLabels hiddenLabels    status              modifiedDate scopeNote definition                                           inScheme                                        description
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0005c151-5b5a...  skill/competence      sector-specific               manage musical staff  manage music staff\ncoordinate duties of music...          NaN  released  2023-11-30T15:53:37.136Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Assign and manage staff tasks in areas such as...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00064735-8fad...  skill/competence  occupation-specific  supervise correctional procedures  manage prison procedures\nmonitor correctional...          NaN  released  2023-11-30T15:04:00.689Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Supervise the operations of a correctional fac...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/000709ed-2be5...  skill/competence      sector-specific    apply anti-oppressive practices  make use of anti-oppressive practices\nuse ant...          NaN  released   2023-11-28T10:45:53.54Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Identify oppression in societies, economies, c...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ISCOGroups_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **619** | Columns: **8**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | ISCOGroup |
| conceptUri | str | 0 | 0.0 | 619 | http://data.europa.eu/esco/isco/C0 |
| code | int64 | 0 | 0.0 | 613 | 0 |
| preferredLabel | str | 0 | 0.0 | 582 | Armed forces occupations |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | float64 | 619 | 100.0 | 0 |  |
| inScheme | str | 0 | 0.0 | 1 | http://data.europa.eu/esco/concept-scheme/occupations,
http: |
| description | str | 0 | 0.0 | 619 | Armed forces occupations include all jobs held by members of |

- Candidate single-column keys: `conceptUri`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                            conceptUri  code                      preferredLabel    status  altLabels                                           inScheme                                        description
0   ISCOGroup    http://data.europa.eu/esco/isco/C0     0            Armed forces occupations  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Armed forces occupations include all jobs held...
1   ISCOGroup   http://data.europa.eu/esco/isco/C01     1  Commissioned armed forces officers  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Commissioned armed forces officers provide lea...
2   ISCOGroup  http://data.europa.eu/esco/isco/C011    11  Commissioned armed forces officers  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Commissioned armed forces officers provide lea...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: skillGroups_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **640** | Columns: **11**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | SkillGroup |
| conceptUri | str | 0 | 0.0 | 640 | http://data.europa.eu/esco/isced-f/00 |
| preferredLabel | str | 0 | 0.0 | 518 | generic programmes and qualifications |
| altLabels | str | 528 | 82.5 | 70 | self-discipline
self-management
self-control
self-regulation |
| hiddenLabels | str | 623 | 97.3 | 17 | professional orientation and perfection
demonstrate self-man |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 301 | 47.0 | 319 | 2023-07-13T15:16:44.968Z |
| scopeNote | str | 316 | 49.4 | 281 | Examples:
- escort students on a field trip
- supervise spec |
| inScheme | str | 0 | 0.0 | 3 | http://data.europa.eu/esco/concept-scheme/skills
http://data |
| description | str | 133 | 20.8 | 425 | Generic programmes and qualifications are those providing fu |
| code | str | 0 | 0.0 | 640 | 00 |

- Candidate single-column keys: `conceptUri`, `code`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                               conceptUri                                     preferredLabel altLabels hiddenLabels    status              modifiedDate scopeNote                                           inScheme                                        description  code
0  SkillGroup    http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications       NaN          NaN  released                       NaN       NaN  http://data.europa.eu/esco/concept-scheme/skil...  Generic programmes and qualifications are thos...    00
1  SkillGroup   http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...       NaN          NaN  released  2023-07-13T15:16:44.968Z       NaN  http://data.europa.eu/esco/concept-scheme/skil...                                                NaN   000
2  SkillGroup  http://data.europa.eu/esco/isced-f/0000  generic programmes and qualifications not furt...       NaN          NaN  released                       NaN       NaN  http://data.europa.eu/esco/concept-scheme/skil...                                                NaN  0000
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: broaderRelationsOccPillar_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,648** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 2 | ISCOGroup |
| conceptUri | str | 0 | 0.0 | 3,648 | http://data.europa.eu/esco/isco/C01 |
| conceptLabel | str | 0 | 0.0 | 3,611 | Commissioned armed forces officers |
| broaderType | str | 0 | 0.0 | 2 | ISCOGroup |
| broaderUri | str | 0 | 0.0 | 882 | http://data.europa.eu/esco/isco/C0 |
| broaderLabel | str | 0 | 0.0 | 850 | Armed forces occupations |

- Candidate single-column keys: `conceptUri`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                             conceptUri                        conceptLabel broaderType                            broaderUri                        broaderLabel
0   ISCOGroup    http://data.europa.eu/esco/isco/C01  Commissioned armed forces officers   ISCOGroup    http://data.europa.eu/esco/isco/C0            Armed forces occupations
1   ISCOGroup   http://data.europa.eu/esco/isco/C011  Commissioned armed forces officers   ISCOGroup   http://data.europa.eu/esco/isco/C01  Commissioned armed forces officers
2   ISCOGroup  http://data.europa.eu/esco/isco/C0110  Commissioned armed forces officers   ISCOGroup  http://data.europa.eu/esco/isco/C011  Commissioned armed forces officers
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: broaderRelationsSkillPillar_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **20,819** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 2 | SkillGroup |
| conceptUri | str | 0 | 0.0 | 14,575 | http://data.europa.eu/esco/isced-f/00 |
| conceptLabel | str | 0 | 0.0 | 14,444 | generic programmes and qualifications |
| broaderType | str | 0 | 0.0 | 2 | SkillGroup |
| broaderUri | str | 0 | 0.0 | 2,856 | http://data.europa.eu/esco/skill/c46fcb45-5c14-4ffa-abed-5a4 |
| broaderLabel | str | 0 | 0.0 | 2,756 | knowledge |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                               conceptUri                                       conceptLabel broaderType                                         broaderUri                                       broaderLabel
0  SkillGroup    http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications  SkillGroup  http://data.europa.eu/esco/skill/c46fcb45-5c14...                                          knowledge
1  SkillGroup   http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...  SkillGroup              http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications
2  SkillGroup  http://data.europa.eu/esco/isced-f/0000  generic programmes and qualifications not furt...  SkillGroup             http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: occupationSkillRelations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **126,051** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| occupationUri | str | 0 | 0.0 | 3,039 | http://data.europa.eu/esco/occupation/00030d09-2b3a-4efd-87c |
| occupationLabel | str | 0 | 0.0 | 3,039 | technical director |
| relationType | str | 0 | 0.0 | 2 | essential |
| skillType | str | 59 | 0.0 | 2 | knowledge |
| skillUri | str | 0 | 0.0 | 13,475 | http://data.europa.eu/esco/skill/fed5b267-73fa-461d-9f69-827 |
| skillLabel | str | 0 | 0.0 | 13,475 | theatre techniques |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)
- relationType values: {'essential': 67600, 'optional': 58451}

Sample rows:

```
                                       occupationUri     occupationLabel relationType         skillType                                           skillUri                                         skillLabel
0  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential         knowledge  http://data.europa.eu/esco/skill/fed5b267-73fa...                                 theatre techniques
1  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential  skill/competence  http://data.europa.eu/esco/skill/05bc7677-5a64...                                organise rehearsals
2  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential  skill/competence  http://data.europa.eu/esco/skill/271a36a0-bc7a...  write risk assessment on performing arts produ...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: transversalSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **95** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 95 | http://data.europa.eu/esco/skill/001115fb-569f-4ee6-8381-c68 |
| skillType | str | 0 | 0.0 | 1 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 2 | transversal |
| preferredLabel | str | 0 | 0.0 | 95 | show initiative |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 0 | 0.0 | 95 | initiate action / be a driving force / give impetus / take t |
| description | str | 0 | 0.0 | 95 | Be proactive and take the first step in an action without wa |
| broaderConceptUri | str | 0 | 0.0 | 24 | http://data.europa.eu/esco/skill/91860993-1a8b-4473-91f3-600 |
| broaderConceptPT | str | 0 | 0.0 | 24 | taking a proactive approach |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType   reuseLevel                                     preferredLabel    status                                          altLabels                                        description                                  broaderConceptUri                               broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/001115fb-569f...  skill/competence  transversal                                    show initiative  released  initiate action | be a driving force | give im...  Be proactive and take the first step in an act...  http://data.europa.eu/esco/skill/91860993-1a8b...                    taking a proactive approach
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0171653e-c8e9...  skill/competence  transversal  adopt ways to foster biodiversity and animal w...  released  concretely support biodiversity and animal wel...  Engage in behaviours that help maintaining sta...  http://data.europa.eu/esco/skill/80cf002a-6586...  applying environmental skills and competences
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/045f71e6-0699...  skill/competence  transversal                                      advise others  released  mentor others | mentor individuals | counsel o...  Offer suggestions about the best course of act...  http://data.europa.eu/esco/skill/82463bb1-85d1...                              supporting others
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: languageSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **359** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 359 | http://data.europa.eu/esco/skill/01f10952-cb59-4347-9aee-d4f |
| skillType | str | 0 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 2 | transversal |
| preferredLabel | str | 0 | 0.0 | 359 | write Hungarian |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 2 | 0.6 | 357 | correspond in written Hungarian / show competency in written |
| description | str | 0 | 0.0 | 359 | Compose written texts in Hungarian. |
| broaderConceptUri | str | 0 | 0.0 | 75 | http://data.europa.eu/esco/skill/ddd3596a-43f3-402e-960a-5f7 |
| broaderConceptPT | str | 0 | 0.0 | 75 | Hungarian |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType   reuseLevel                   preferredLabel    status                                          altLabels                                   description                                  broaderConceptUri broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/01f10952-cb59...  skill/competence  transversal                  write Hungarian  released  correspond in written Hungarian | show compete...           Compose written texts in Hungarian.  http://data.europa.eu/esco/skill/ddd3596a-43f3...        Hungarian
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/021c8a09-6b8d...         knowledge  transversal  understand spoken Luxembourgish  released  understand Luxembourgish speech | interpret sp...    Comprehend orally expressed Luxembourgish.  http://data.europa.eu/esco/skill/7d16f1e4-1003...    Luxembourgish
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/02d68c2b-1722...  skill/competence  transversal        understand written Korean  released  read Korean | comprehend written Korean | make...  Read and comprehend written texts in Korean.  http://data.europa.eu/esco/skill/f9bc2890-d1f2...           Korean
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: skillSkillRelations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **5,818** | Columns: **5**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| originalSkillUri | str | 0 | 0.0 | 3,759 | http://data.europa.eu/esco/skill/00064735-8fad-454b-90c7-ed8 |
| originalSkillType | str | 0 | 0.0 | 2 | skill/competence |
| relationType | str | 0 | 0.0 | 2 | optional |
| relatedSkillType | str | 0 | 0.0 | 2 | knowledge |
| relatedSkillUri | str | 0 | 0.0 | 1,953 | http://data.europa.eu/esco/skill/d4a0744a-508b-4a5e-97a5-ad1 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)
- relationType values: {'optional': 5629, 'essential': 189}

Sample rows:

```
                                    originalSkillUri originalSkillType relationType relatedSkillType                                    relatedSkillUri
0  http://data.europa.eu/esco/skill/00064735-8fad...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/d4a0744a-508b...
1  http://data.europa.eu/esco/skill/000bb1e4-89f0...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/b70ab677-5781...
2  http://data.europa.eu/esco/skill/0023e7a5-43da...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/5753e2ca-8934...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: conceptSchemes_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **20** | Columns: **7**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | ConceptScheme |
| conceptSchemeUri | str | 0 | 0.0 | 20 | http://data.europa.eu/esco/concept-scheme/6c930acd-c104-4ece |
| preferredLabel | str | 0 | 0.0 | 20 | Digital |
| title | str | 17 | 85.0 | 3 | ESCO relationship types |
| status | str | 6 | 30.0 | 1 | released |
| description | str | 16 | 80.0 | 4 | A taxonomy of the different label roles in ESCO |
| hasTopConcept | str | 0 | 0.0 | 20 | http://data.europa.eu/esco/skill/6c80d53c-d8c9-41fe-998f-091 |

- Candidate single-column keys: `conceptSchemeUri`, `preferredLabel`, `hasTopConcept`
- Looks like ESCO (URI columns present)

Sample rows:

```
     conceptType                                   conceptSchemeUri        preferredLabel title    status description                                      hasTopConcept
0  ConceptScheme  http://data.europa.eu/esco/concept-scheme/6c93...               Digital   NaN  released         NaN  http://data.europa.eu/esco/skill/6c80d53c-d8c9...
1  ConceptScheme  http://data.europa.eu/esco/concept-scheme/8ae4...  Research occupations   NaN  released         NaN  http://data.europa.eu/esco/occupation/d7d986e1...
2  ConceptScheme  http://data.europa.eu/esco/concept-scheme/digcomp               DigComp   NaN  released         NaN  http://data.europa.eu/esco/skill/21d2f96d-35f7...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: digCompSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **25** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 25 | http://data.europa.eu/esco/skill/14832d87-2f2f-4895-b290-e47 |
| preferredLabel | str | 0 | 0.0 | 25 | solve technical problems |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 5 | 20.0 | 2 | skill/competence |
| reuseLevel | str | 5 | 20.0 | 2 | cross-sector |
| altLabels | str | 2 | 8.0 | 23 | resolve technical issues / diagnose technical problems |
| description | str | 0 | 0.0 | 25 | Identify technical problems when operating devices and using |
| broaderConceptUri | str | 0 | 0.0 | 19 | http://data.europa.eu/esco/skill/7e5147d1-60b1-4a68-804b-1f5 |
| broaderConceptPT | str | 0 | 0.0 | 19 | problem-solving with digital tools / identify problems / res |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                       preferredLabel    status         skillType    reuseLevel                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/14832d87-2f2f...             solve technical problems  released  skill/competence  cross-sector  resolve technical issues | diagnose technical ...  Identify technical problems when operating dev...  http://data.europa.eu/esco/skill/7e5147d1-60b1...  problem-solving with digital tools | identify ...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/16a00c69-9c74...                       use e-services  released  skill/competence  cross-sector  use online payment solutions | make use of e-s...  Participate in society through the use of publ...  http://data.europa.eu/esco/skill/574257ea-7b64...  digital communication and collaboration | usin...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/1a4cc54f-1e53...  creatively use digital technologies  released  skill/competence  cross-sector  use digital technologies for cognitive tasks |...  Use digital tools and technologies to create k...  http://data.europa.eu/esco/skill/7e5147d1-60b1...  problem-solving with digital tools | using dig...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: greenSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **629** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 629 | http://data.europa.eu/esco/skill/001d46db-035e-4b92-83a3-ed8 |
| preferredLabel | str | 0 | 0.0 | 629 | train staff to reduce food waste |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 4 | sector-specific |
| altLabels | str | 1 | 0.2 | 628 | teach students food waste reduction practices / educate staf |
| description | str | 0 | 0.0 | 629 | Establish new trainings and staff development provisions to  |
| broaderConceptUri | str | 0 | 0.0 | 314 | http://data.europa.eu/esco/skill/6c4fa8c8-e9e1-49b5-897f-6b6 |
| broaderConceptPT | str | 0 | 0.0 | 311 | training on operational procedures |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                    preferredLabel    status         skillType       reuseLevel                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/001d46db-035e...  train staff to reduce food waste  released  skill/competence  sector-specific  teach students food waste reduction practices ...  Establish new trainings and staff development ...  http://data.europa.eu/esco/skill/6c4fa8c8-e9e1...                 training on operational procedures
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0037c821-2898...    develop energy saving concepts  released  skill/competence     cross-sector  develop concepts for energy saving | create en...  Use current research results and collaborate w...  http://data.europa.eu/esco/skill/c2a0c52c-0b4b...  think innovatively | developing operational po...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00735755-adc6...                 install heat pump  released  skill/competence     cross-sector  installation of heat pumps | commissioning hea...  Install heat pumps, which use the physical pro...  http://data.europa.eu/esco/skill/b85caa4a-f04b...  installing heating, ventilation and air condit...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: researchSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **40** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 40 | http://data.europa.eu/esco/skill/00b9a3aa-7070-4bb5-8020-f22 |
| preferredLabel | str | 0 | 0.0 | 40 | draft scientific or academic papers and technical documentat |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 1 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 3 | cross-sector |
| altLabels | str | 0 | 0.0 | 40 | create technical documentation / create technical documentat |
| description | str | 0 | 0.0 | 40 | Draft and edit scientific, academic or technical texts on di |
| broaderConceptUri | str | 0 | 0.0 | 34 | http://data.europa.eu/esco/skill/6e62e776-fbfa-486c-a6df-58c |
| broaderConceptPT | str | 0 | 0.0 | 34 | technical or academic writing |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                                     preferredLabel    status         skillType    reuseLevel                                          altLabels                                        description                                  broaderConceptUri               broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00b9a3aa-7070...  draft scientific or academic papers and techni...  released  skill/competence  cross-sector  create technical documentation | create techni...  Draft and edit scientific, academic or technic...  http://data.europa.eu/esco/skill/6e62e776-fbfa...  technical or academic writing
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/08b04e53-ed25...                               manage research data  released  skill/competence  cross-sector  oversee scientific data | handle research data...  Produce and analyse scientific data originatin...  http://data.europa.eu/esco/skill/32c017fd-28ab...           managing information
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/20a8fe89-d4eb...  interact professionally in research and profes...  released  skill/competence  cross-sector  give feedback in a professional setting | inte...  Show consideration to others as well as colleg...  http://data.europa.eu/esco/skill/91b0b918-942e...            working with others
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: digitalSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **1,284** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 1,284 | http://data.europa.eu/esco/skill/000f1d3d-220f-4789-9c0a-cc7 |
| preferredLabel | str | 0 | 0.0 | 1,284 | Haskell |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 2 | knowledge |
| reuseLevel | str | 0 | 0.0 | 4 | sector-specific |
| altLabels | str | 12 | 0.9 | 1,272 | Haskell techniques |
| description | str | 0 | 0.0 | 1,284 | The techniques and principles of software development, such  |
| broaderConceptUri | str | 0 | 0.0 | 478 | http://data.europa.eu/esco/skill/21d2f96d-35f7-4e3f-9745-c53 |
| broaderConceptPT | str | 0 | 0.0 | 475 | computer programming / software and applications development |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri           preferredLabel    status  skillType       reuseLevel                         altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/000f1d3d-220f...                  Haskell  released  knowledge  sector-specific                Haskell techniques  The techniques and principles of software deve...  http://data.europa.eu/esco/skill/21d2f96d-35f7...  computer programming | software and applicatio...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00c04e40-35ea...  incremental development  released  knowledge  sector-specific               gradual development  The incremental development model is a methodo...  http://data.europa.eu/esco/skill/bec4359e-cb92...  ICT project management methodologies | softwar...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/013441c1-1f13...                 KDevelop  released  knowledge  sector-specific  kdevplatform | KDevelop platform  The computer program KDevelop is a suite of so...  http://data.europa.eu/esco/skill/925463a7-d51f...  integrated development environment software | ...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: researchOccupationsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **122** | Columns: **8**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | Occupation |
| conceptUri | str | 0 | 0.0 | 122 | http://data.europa.eu/esco/occupation/01ffb917-98dc-48c1-91a |
| preferredLabel | str | 0 | 0.0 | 122 | biomedical engineer |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 0 | 0.0 | 122 | biomedical technology engineering specialist / biomedical te |
| description | str | 0 | 0.0 | 122 | Biomedical engineers combine knowledge of engineering princi |
| broaderConceptUri | str | 0 | 0.0 | 43 | http://data.europa.eu/esco/occupation/f9433fdb-dde1-46cf-9e9 |
| broaderConceptPT | str | 0 | 0.0 | 43 | bioengineer |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                                         conceptUri       preferredLabel    status                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  Occupation  http://data.europa.eu/esco/occupation/01ffb917...  biomedical engineer  released  biomedical technology engineering specialist |...  Biomedical engineers combine knowledge of engi...  http://data.europa.eu/esco/occupation/f9433fdb...                                        bioengineer
1  Occupation  http://data.europa.eu/esco/occupation/0611f232...        criminologist  released  criminology scientist | criminology research s...  Criminologists study conditions pertaining to ...              http://data.europa.eu/esco/isco/C2632  Sociologists, anthropologists and related prof...
2  Occupation  http://data.europa.eu/esco/occupation/0959cd1d...   economics lecturer  released  economics professor | university lecturer in e...  Economics lecturers are subject professors, as...  http://data.europa.eu/esco/occupation/684fd8d5...                          higher education lecturer
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: skillsHierarchy_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **640** | Columns: **14**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| Level 0 URI | str | 0 | 0.0 | 4 | http://data.europa.eu/esco/skill/e35a5936-091d-4e87-bafe-f26 |
| Level 0 preferred term | str | 0 | 0.0 | 4 | language skills and knowledge |
| Level 1 URI | str | 4 | 0.6 | 28 | http://data.europa.eu/esco/skill/43f425aa-f45d-4bb4-a200-6f8 |
| Level 1 preferred term | str | 4 | 0.6 | 28 | languages |
| Level 2 URI | str | 32 | 5.0 | 156 | http://data.europa.eu/esco/skill/15dfca7a-5dde-4199-bad3-c00 |
| Level 2 preferred term | str | 32 | 5.0 | 156 | handling and disposing of waste and hazardous materials |
| Level 3 URI | str | 188 | 29.4 | 452 | http://data.europa.eu/esco/skill/61d1dab2-6007-4b7c-9380-cd8 |
| Level 3 preferred term | str | 188 | 29.4 | 452 | disposing of non-hazardous waste or debris |
| Description | str | 133 | 20.8 | 425 | Ability to communicate through reading, writing, speaking an |
| Scope note | str | 316 | 49.4 | 281 | Excludes:
- all languages that are actively used as a mother |
| Level 0 code | str | 0 | 0.0 | 4 | L |
| Level 1 code | str | 4 | 0.6 | 28 | L1 |
| Level 2 code | str | 32 | 5.0 | 156 | S6.13 |
| Level 3 code | str | 188 | 29.4 | 452 | S6.13.2 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
                                         Level 0 URI         Level 0 preferred term                                        Level 1 URI Level 1 preferred term Level 2 URI Level 2 preferred term Level 3 URI Level 3 preferred term                                        Description                                         Scope note Level 0 code Level 1 code Level 2 code Level 3 code
0  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge                                                NaN                    NaN         NaN                    NaN         NaN                    NaN                                                NaN                                                NaN            L          NaN          NaN          NaN
1  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge  http://data.europa.eu/esco/skill/43f425aa-f45d...              languages         NaN                    NaN         NaN                    NaN  Ability to communicate through reading, writin...                                                NaN            L           L1          NaN          NaN
2  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge  http://data.europa.eu/esco/skill/e434e71a-f068...    classical languages         NaN                    NaN         NaN                    NaN  All dead languages, no longer actively used, o...  Excludes:\n- all languages that are actively u...            L           L2          NaN          NaN
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: greenShareOcc_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,590** | Columns: **5**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 3 | ISCO level 3 |
| conceptUri | str | 0 | 0.0 | 3,590 | http://data.europa.eu/esco/isco/C011 |
| code | str | 0 | 0.0 | 3,590 | 011 |
| preferredLabel | str | 0 | 0.0 | 3,566 | Commissioned armed forces officers |
| greenShare | float64 | 0 | 0.0 | 747 | 0.00575396825396825 |

- Candidate single-column keys: `conceptUri`, `code`
- Looks like ESCO (URI columns present)

Sample rows:

```
    conceptType                                         conceptUri    code                      preferredLabel  greenShare
0  ISCO level 3               http://data.europa.eu/esco/isco/C011     011  Commissioned armed forces officers    0.005754
1  ISCO level 4              http://data.europa.eu/esco/isco/C0110    0110  Commissioned armed forces officers    0.005754
2    Occupation  http://data.europa.eu/esco/occupation/f2cc5978...  0110.1                   air force officer    0.000000
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: content_model_reference_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,006** | Columns: **3**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| Element ID | str | 0 | 0.0 | 3,006 | 1 |
| Element Name | str | 0 | 0.0 | 2,945 | Worker Characteristics |
| Description | str | 2,419 | 80.5 | 587 | Personal traits and abilities that affect how people learn a |

- Candidate single-column keys: `Element ID`
- Looks like O*NET (columns found: Element ID, Element Name)
- Distinct elements (skills/knowledge/activities): 2,945

Sample rows:

```
  Element ID            Element Name                                        Description
0          1  Worker Characteristics  Personal traits and abilities that affect how ...
1        1.A               Abilities  Natural talents and capabilities that affect h...
2      1.A.1     Cognitive Abilities  Abilities that influence the acquisition and a...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/broaderRelationsOccPillar_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,648** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 2 | ISCOGroup |
| conceptUri | str | 0 | 0.0 | 3,648 | http://data.europa.eu/esco/isco/C01 |
| conceptLabel | str | 0 | 0.0 | 3,611 | Commissioned armed forces officers |
| broaderType | str | 0 | 0.0 | 2 | ISCOGroup |
| broaderUri | str | 0 | 0.0 | 882 | http://data.europa.eu/esco/isco/C0 |
| broaderLabel | str | 0 | 0.0 | 850 | Armed forces occupations |

- Candidate single-column keys: `conceptUri`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                             conceptUri                        conceptLabel broaderType                            broaderUri                        broaderLabel
0   ISCOGroup    http://data.europa.eu/esco/isco/C01  Commissioned armed forces officers   ISCOGroup    http://data.europa.eu/esco/isco/C0            Armed forces occupations
1   ISCOGroup   http://data.europa.eu/esco/isco/C011  Commissioned armed forces officers   ISCOGroup   http://data.europa.eu/esco/isco/C01  Commissioned armed forces officers
2   ISCOGroup  http://data.europa.eu/esco/isco/C0110  Commissioned armed forces officers   ISCOGroup  http://data.europa.eu/esco/isco/C011  Commissioned armed forces officers
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/broaderRelationsSkillPillar_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **20,819** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 2 | SkillGroup |
| conceptUri | str | 0 | 0.0 | 14,575 | http://data.europa.eu/esco/isced-f/00 |
| conceptLabel | str | 0 | 0.0 | 14,444 | generic programmes and qualifications |
| broaderType | str | 0 | 0.0 | 2 | SkillGroup |
| broaderUri | str | 0 | 0.0 | 2,856 | http://data.europa.eu/esco/skill/c46fcb45-5c14-4ffa-abed-5a4 |
| broaderLabel | str | 0 | 0.0 | 2,756 | knowledge |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                               conceptUri                                       conceptLabel broaderType                                         broaderUri                                       broaderLabel
0  SkillGroup    http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications  SkillGroup  http://data.europa.eu/esco/skill/c46fcb45-5c14...                                          knowledge
1  SkillGroup   http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...  SkillGroup              http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications
2  SkillGroup  http://data.europa.eu/esco/isced-f/0000  generic programmes and qualifications not furt...  SkillGroup             http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/conceptSchemes_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **20** | Columns: **7**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | ConceptScheme |
| conceptSchemeUri | str | 0 | 0.0 | 20 | http://data.europa.eu/esco/concept-scheme/6c930acd-c104-4ece |
| preferredLabel | str | 0 | 0.0 | 20 | Digital |
| title | str | 17 | 85.0 | 3 | ESCO relationship types |
| status | str | 6 | 30.0 | 1 | released |
| description | str | 16 | 80.0 | 4 | A taxonomy of the different label roles in ESCO |
| hasTopConcept | str | 0 | 0.0 | 20 | http://data.europa.eu/esco/skill/6c80d53c-d8c9-41fe-998f-091 |

- Candidate single-column keys: `conceptSchemeUri`, `preferredLabel`, `hasTopConcept`
- Looks like ESCO (URI columns present)

Sample rows:

```
     conceptType                                   conceptSchemeUri        preferredLabel title    status description                                      hasTopConcept
0  ConceptScheme  http://data.europa.eu/esco/concept-scheme/6c93...               Digital   NaN  released         NaN  http://data.europa.eu/esco/skill/6c80d53c-d8c9...
1  ConceptScheme  http://data.europa.eu/esco/concept-scheme/8ae4...  Research occupations   NaN  released         NaN  http://data.europa.eu/esco/occupation/d7d986e1...
2  ConceptScheme  http://data.europa.eu/esco/concept-scheme/digcomp               DigComp   NaN  released         NaN  http://data.europa.eu/esco/skill/21d2f96d-35f7...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/dictionary_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **160** | Columns: **4**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| filename | str | 0 | 0.0 | 18 | occupations |
| data header | str | 0 | 0.0 | 50 | conceptType |
| property | str | 47 | 29.4 | 18 | http://www.w3.org/2004/02/skos/core#notation |
| description | str | 0 | 0.0 | 19 | No direct related property exists |

- Candidate single-column keys: none

Sample rows:

```
      filename  data header                                      property                                        description
0  occupations  conceptType                                           NaN                  No direct related property exists
1  occupations   conceptUri                                           NaN                  No direct related property exists
2  occupations    iscoGroup  http://www.w3.org/2004/02/skos/core#notation  A notation, also known as classification code,...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/digCompSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **25** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 25 | http://data.europa.eu/esco/skill/14832d87-2f2f-4895-b290-e47 |
| preferredLabel | str | 0 | 0.0 | 25 | solve technical problems |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 5 | 20.0 | 2 | skill/competence |
| reuseLevel | str | 5 | 20.0 | 2 | cross-sector |
| altLabels | str | 2 | 8.0 | 23 | resolve technical issues / diagnose technical problems |
| description | str | 0 | 0.0 | 25 | Identify technical problems when operating devices and using |
| broaderConceptUri | str | 0 | 0.0 | 19 | http://data.europa.eu/esco/skill/7e5147d1-60b1-4a68-804b-1f5 |
| broaderConceptPT | str | 0 | 0.0 | 19 | problem-solving with digital tools / identify problems / res |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                       preferredLabel    status         skillType    reuseLevel                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/14832d87-2f2f...             solve technical problems  released  skill/competence  cross-sector  resolve technical issues | diagnose technical ...  Identify technical problems when operating dev...  http://data.europa.eu/esco/skill/7e5147d1-60b1...  problem-solving with digital tools | identify ...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/16a00c69-9c74...                       use e-services  released  skill/competence  cross-sector  use online payment solutions | make use of e-s...  Participate in society through the use of publ...  http://data.europa.eu/esco/skill/574257ea-7b64...  digital communication and collaboration | usin...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/1a4cc54f-1e53...  creatively use digital technologies  released  skill/competence  cross-sector  use digital technologies for cognitive tasks |...  Use digital tools and technologies to create k...  http://data.europa.eu/esco/skill/7e5147d1-60b1...  problem-solving with digital tools | using dig...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/digitalSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **1,284** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 1,284 | http://data.europa.eu/esco/skill/000f1d3d-220f-4789-9c0a-cc7 |
| preferredLabel | str | 0 | 0.0 | 1,284 | Haskell |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 2 | knowledge |
| reuseLevel | str | 0 | 0.0 | 4 | sector-specific |
| altLabels | str | 12 | 0.9 | 1,272 | Haskell techniques |
| description | str | 0 | 0.0 | 1,284 | The techniques and principles of software development, such  |
| broaderConceptUri | str | 0 | 0.0 | 478 | http://data.europa.eu/esco/skill/21d2f96d-35f7-4e3f-9745-c53 |
| broaderConceptPT | str | 0 | 0.0 | 475 | computer programming / software and applications development |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri           preferredLabel    status  skillType       reuseLevel                         altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/000f1d3d-220f...                  Haskell  released  knowledge  sector-specific                Haskell techniques  The techniques and principles of software deve...  http://data.europa.eu/esco/skill/21d2f96d-35f7...  computer programming | software and applicatio...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00c04e40-35ea...  incremental development  released  knowledge  sector-specific               gradual development  The incremental development model is a methodo...  http://data.europa.eu/esco/skill/bec4359e-cb92...  ICT project management methodologies | softwar...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/013441c1-1f13...                 KDevelop  released  knowledge  sector-specific  kdevplatform | KDevelop platform  The computer program KDevelop is a suite of so...  http://data.europa.eu/esco/skill/925463a7-d51f...  integrated development environment software | ...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/greenShareOcc_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,590** | Columns: **5**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 3 | ISCO level 3 |
| conceptUri | str | 0 | 0.0 | 3,590 | http://data.europa.eu/esco/isco/C011 |
| code | str | 0 | 0.0 | 3,590 | 011 |
| preferredLabel | str | 0 | 0.0 | 3,566 | Commissioned armed forces officers |
| greenShare | float64 | 0 | 0.0 | 747 | 0.00575396825396825 |

- Candidate single-column keys: `conceptUri`, `code`
- Looks like ESCO (URI columns present)

Sample rows:

```
    conceptType                                         conceptUri    code                      preferredLabel  greenShare
0  ISCO level 3               http://data.europa.eu/esco/isco/C011     011  Commissioned armed forces officers    0.005754
1  ISCO level 4              http://data.europa.eu/esco/isco/C0110    0110  Commissioned armed forces officers    0.005754
2    Occupation  http://data.europa.eu/esco/occupation/f2cc5978...  0110.1                   air force officer    0.000000
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/greenSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **629** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 629 | http://data.europa.eu/esco/skill/001d46db-035e-4b92-83a3-ed8 |
| preferredLabel | str | 0 | 0.0 | 629 | train staff to reduce food waste |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 4 | sector-specific |
| altLabels | str | 1 | 0.2 | 628 | teach students food waste reduction practices / educate staf |
| description | str | 0 | 0.0 | 629 | Establish new trainings and staff development provisions to  |
| broaderConceptUri | str | 0 | 0.0 | 314 | http://data.europa.eu/esco/skill/6c4fa8c8-e9e1-49b5-897f-6b6 |
| broaderConceptPT | str | 0 | 0.0 | 311 | training on operational procedures |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                    preferredLabel    status         skillType       reuseLevel                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/001d46db-035e...  train staff to reduce food waste  released  skill/competence  sector-specific  teach students food waste reduction practices ...  Establish new trainings and staff development ...  http://data.europa.eu/esco/skill/6c4fa8c8-e9e1...                 training on operational procedures
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0037c821-2898...    develop energy saving concepts  released  skill/competence     cross-sector  develop concepts for energy saving | create en...  Use current research results and collaborate w...  http://data.europa.eu/esco/skill/c2a0c52c-0b4b...  think innovatively | developing operational po...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00735755-adc6...                 install heat pump  released  skill/competence     cross-sector  installation of heat pumps | commissioning hea...  Install heat pumps, which use the physical pro...  http://data.europa.eu/esco/skill/b85caa4a-f04b...  installing heating, ventilation and air condit...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/ISCOGroups_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **619** | Columns: **8**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | ISCOGroup |
| conceptUri | str | 0 | 0.0 | 619 | http://data.europa.eu/esco/isco/C0 |
| code | int64 | 0 | 0.0 | 613 | 0 |
| preferredLabel | str | 0 | 0.0 | 582 | Armed forces occupations |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | float64 | 619 | 100.0 | 0 |  |
| inScheme | str | 0 | 0.0 | 1 | http://data.europa.eu/esco/concept-scheme/occupations,
http: |
| description | str | 0 | 0.0 | 619 | Armed forces occupations include all jobs held by members of |

- Candidate single-column keys: `conceptUri`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                            conceptUri  code                      preferredLabel    status  altLabels                                           inScheme                                        description
0   ISCOGroup    http://data.europa.eu/esco/isco/C0     0            Armed forces occupations  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Armed forces occupations include all jobs held...
1   ISCOGroup   http://data.europa.eu/esco/isco/C01     1  Commissioned armed forces officers  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Commissioned armed forces officers provide lea...
2   ISCOGroup  http://data.europa.eu/esco/isco/C011    11  Commissioned armed forces officers  released        NaN  http://data.europa.eu/esco/concept-scheme/occu...  Commissioned armed forces officers provide lea...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/languageSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **359** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 359 | http://data.europa.eu/esco/skill/01f10952-cb59-4347-9aee-d4f |
| skillType | str | 0 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 2 | transversal |
| preferredLabel | str | 0 | 0.0 | 359 | write Hungarian |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 2 | 0.6 | 357 | correspond in written Hungarian / show competency in written |
| description | str | 0 | 0.0 | 359 | Compose written texts in Hungarian. |
| broaderConceptUri | str | 0 | 0.0 | 75 | http://data.europa.eu/esco/skill/ddd3596a-43f3-402e-960a-5f7 |
| broaderConceptPT | str | 0 | 0.0 | 75 | Hungarian |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType   reuseLevel                   preferredLabel    status                                          altLabels                                   description                                  broaderConceptUri broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/01f10952-cb59...  skill/competence  transversal                  write Hungarian  released  correspond in written Hungarian | show compete...           Compose written texts in Hungarian.  http://data.europa.eu/esco/skill/ddd3596a-43f3...        Hungarian
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/021c8a09-6b8d...         knowledge  transversal  understand spoken Luxembourgish  released  understand Luxembourgish speech | interpret sp...    Comprehend orally expressed Luxembourgish.  http://data.europa.eu/esco/skill/7d16f1e4-1003...    Luxembourgish
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/02d68c2b-1722...  skill/competence  transversal        understand written Korean  released  read Korean | comprehend written Korean | make...  Read and comprehend written texts in Korean.  http://data.europa.eu/esco/skill/f9bc2890-d1f2...           Korean
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/occupations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **3,043** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | Occupation |
| conceptUri | str | 0 | 0.0 | 3,039 | http://data.europa.eu/esco/occupation/00030d09-2b3a-4efd-87c |
| iscoGroup | int64 | 0 | 0.0 | 426 | 2654 |
| preferredLabel | str | 0 | 0.0 | 3,039 | technical director |
| altLabels | str | 0 | 0.0 | 3,039 | director of technical arts
technical supervisor
head of tech |
| hiddenLabels | str | 3,035 | 99.7 | 8 | sexual health consultant
youth policy manager
youth operator |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 0 | 0.0 | 2,902 | 2024-01-25T11:28:50.295Z |
| regulatedProfessionNote | str | 0 | 0.0 | 2 | http://data.europa.eu/esco/regulated-professions/unregulated |
| scopeNote | str | 2,733 | 89.8 | 274 | Excludes people performing analysis of blood samples, cell c |
| definition | str | 3,035 | 99.7 | 8 | Excludes choreologist. |
| inScheme | str | 0 | 0.0 | 2 | http://data.europa.eu/esco/concept-scheme/member-occupations |
| description | str | 0 | 0.0 | 3,039 | Technical directors realise the artistic visions of the crea |
| code | str | 0 | 0.0 | 3,039 | 2654.1.7 |
| naceCode | str | 0 | 0.0 | 1,121 | http://data.europa.eu/ux2/nace2.1/9031 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                                         conceptUri  iscoGroup                  preferredLabel                                          altLabels hiddenLabels    status              modifiedDate                            regulatedProfessionNote scopeNote definition                                           inScheme                                        description       code                                naceCode
0  Occupation  http://data.europa.eu/esco/occupation/00030d09...       2654              technical director  director of technical arts\ntechnical supervis...          NaN  released  2024-01-25T11:28:50.295Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Technical directors realise the artistic visio...   2654.1.7  http://data.europa.eu/ux2/nace2.1/9031
1  Occupation  http://data.europa.eu/esco/occupation/000e93a3...       8121  metal drawing machine operator  wire drawer\nforming machine operative\ndraw m...          NaN  released  2024-01-23T10:09:32.099Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Metal drawing machine operators set up and ope...     8121.4   http://data.europa.eu/ux2/nace2.1/242
2  Occupation  http://data.europa.eu/esco/occupation/0019b951...       7543      precision device inspector  precision device quality control supervisor\np...          NaN  released  2024-01-25T15:00:12.188Z  http://data.europa.eu/esco/regulated-professio...       NaN        NaN  http://data.europa.eu/esco/concept-scheme/memb...  Precision device inspectors make sure precisio...  7543.10.3  http://data.europa.eu/ux2/nace2.1/2651
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/occupationSkillRelations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **126,051** | Columns: **6**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| occupationUri | str | 0 | 0.0 | 3,039 | http://data.europa.eu/esco/occupation/00030d09-2b3a-4efd-87c |
| occupationLabel | str | 0 | 0.0 | 3,039 | technical director |
| relationType | str | 0 | 0.0 | 2 | essential |
| skillType | str | 59 | 0.0 | 2 | knowledge |
| skillUri | str | 0 | 0.0 | 13,475 | http://data.europa.eu/esco/skill/fed5b267-73fa-461d-9f69-827 |
| skillLabel | str | 0 | 0.0 | 13,475 | theatre techniques |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)
- relationType values: {'essential': 67600, 'optional': 58451}

Sample rows:

```
                                       occupationUri     occupationLabel relationType         skillType                                           skillUri                                         skillLabel
0  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential         knowledge  http://data.europa.eu/esco/skill/fed5b267-73fa...                                 theatre techniques
1  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential  skill/competence  http://data.europa.eu/esco/skill/05bc7677-5a64...                                organise rehearsals
2  http://data.europa.eu/esco/occupation/00030d09...  technical director    essential  skill/competence  http://data.europa.eu/esco/skill/271a36a0-bc7a...  write risk assessment on performing arts produ...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/researchOccupationsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **122** | Columns: **8**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | Occupation |
| conceptUri | str | 0 | 0.0 | 122 | http://data.europa.eu/esco/occupation/01ffb917-98dc-48c1-91a |
| preferredLabel | str | 0 | 0.0 | 122 | biomedical engineer |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 0 | 0.0 | 122 | biomedical technology engineering specialist / biomedical te |
| description | str | 0 | 0.0 | 122 | Biomedical engineers combine knowledge of engineering princi |
| broaderConceptUri | str | 0 | 0.0 | 43 | http://data.europa.eu/esco/occupation/f9433fdb-dde1-46cf-9e9 |
| broaderConceptPT | str | 0 | 0.0 | 43 | bioengineer |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                                         conceptUri       preferredLabel    status                                          altLabels                                        description                                  broaderConceptUri                                   broaderConceptPT
0  Occupation  http://data.europa.eu/esco/occupation/01ffb917...  biomedical engineer  released  biomedical technology engineering specialist |...  Biomedical engineers combine knowledge of engi...  http://data.europa.eu/esco/occupation/f9433fdb...                                        bioengineer
1  Occupation  http://data.europa.eu/esco/occupation/0611f232...        criminologist  released  criminology scientist | criminology research s...  Criminologists study conditions pertaining to ...              http://data.europa.eu/esco/isco/C2632  Sociologists, anthropologists and related prof...
2  Occupation  http://data.europa.eu/esco/occupation/0959cd1d...   economics lecturer  released  economics professor | university lecturer in e...  Economics lecturers are subject professors, as...  http://data.europa.eu/esco/occupation/684fd8d5...                          higher education lecturer
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/researchSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **40** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 40 | http://data.europa.eu/esco/skill/00b9a3aa-7070-4bb5-8020-f22 |
| preferredLabel | str | 0 | 0.0 | 40 | draft scientific or academic papers and technical documentat |
| status | str | 0 | 0.0 | 1 | released |
| skillType | str | 0 | 0.0 | 1 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 3 | cross-sector |
| altLabels | str | 0 | 0.0 | 40 | create technical documentation / create technical documentat |
| description | str | 0 | 0.0 | 40 | Draft and edit scientific, academic or technical texts on di |
| broaderConceptUri | str | 0 | 0.0 | 34 | http://data.europa.eu/esco/skill/6e62e776-fbfa-486c-a6df-58c |
| broaderConceptPT | str | 0 | 0.0 | 34 | technical or academic writing |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri                                     preferredLabel    status         skillType    reuseLevel                                          altLabels                                        description                                  broaderConceptUri               broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00b9a3aa-7070...  draft scientific or academic papers and techni...  released  skill/competence  cross-sector  create technical documentation | create techni...  Draft and edit scientific, academic or technic...  http://data.europa.eu/esco/skill/6e62e776-fbfa...  technical or academic writing
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/08b04e53-ed25...                               manage research data  released  skill/competence  cross-sector  oversee scientific data | handle research data...  Produce and analyse scientific data originatin...  http://data.europa.eu/esco/skill/32c017fd-28ab...           managing information
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/20a8fe89-d4eb...  interact professionally in research and profes...  released  skill/competence  cross-sector  give feedback in a professional setting | inte...  Show consideration to others as well as colleg...  http://data.europa.eu/esco/skill/91b0b918-942e...            working with others
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillGroups_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **640** | Columns: **11**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | SkillGroup |
| conceptUri | str | 0 | 0.0 | 640 | http://data.europa.eu/esco/isced-f/00 |
| preferredLabel | str | 0 | 0.0 | 518 | generic programmes and qualifications |
| altLabels | str | 528 | 82.5 | 70 | self-discipline
self-management
self-control
self-regulation |
| hiddenLabels | str | 623 | 97.3 | 17 | professional orientation and perfection
demonstrate self-man |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 301 | 47.0 | 319 | 2023-07-13T15:16:44.968Z |
| scopeNote | str | 316 | 49.4 | 281 | Examples:
- escort students on a field trip
- supervise spec |
| inScheme | str | 0 | 0.0 | 3 | http://data.europa.eu/esco/concept-scheme/skills
http://data |
| description | str | 133 | 20.8 | 425 | Generic programmes and qualifications are those providing fu |
| code | str | 0 | 0.0 | 640 | 00 |

- Candidate single-column keys: `conceptUri`, `code`
- Looks like ESCO (URI columns present)

Sample rows:

```
  conceptType                               conceptUri                                     preferredLabel altLabels hiddenLabels    status              modifiedDate scopeNote                                           inScheme                                        description  code
0  SkillGroup    http://data.europa.eu/esco/isced-f/00              generic programmes and qualifications       NaN          NaN  released                       NaN       NaN  http://data.europa.eu/esco/concept-scheme/skil...  Generic programmes and qualifications are thos...    00
1  SkillGroup   http://data.europa.eu/esco/isced-f/000  generic programmes and qualifications not furt...       NaN          NaN  released  2023-07-13T15:16:44.968Z       NaN  http://data.europa.eu/esco/concept-scheme/skil...                                                NaN   000
2  SkillGroup  http://data.europa.eu/esco/isced-f/0000  generic programmes and qualifications not furt...       NaN          NaN  released                       NaN       NaN  http://data.europa.eu/esco/concept-scheme/skil...                                                NaN  0000
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/skills_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **13,960** | Columns: **13**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 13,939 | http://data.europa.eu/esco/skill/0005c151-5b5a-4a66-8aac-60e |
| skillType | str | 5 | 0.0 | 2 | skill/competence |
| reuseLevel | str | 5 | 0.0 | 4 | sector-specific |
| preferredLabel | str | 0 | 0.0 | 13,939 | manage musical staff |
| altLabels | str | 18 | 0.1 | 13,918 | manage music staff
coordinate duties of musical staff
direct |
| hiddenLabels | str | 13,807 | 98.9 | 153 | active participation
activity
initiative
great initiative
se |
| status | str | 0 | 0.0 | 1 | released |
| modifiedDate | str | 0 | 0.0 | 2,669 | 2023-11-30T15:53:37.136Z |
| scopeNote | str | 13,724 | 98.3 | 224 | It includes building stone, sand, bricks, clay and gravel. |
| definition | str | 13,958 | 100.0 | 2 | Bilingual examination of target language content against sou |
| inScheme | str | 0 | 0.0 | 15 | http://data.europa.eu/esco/concept-scheme/skills,
http://dat |
| description | str | 0 | 0.0 | 13,935 | Assign and manage staff tasks in areas such as scoring, arra |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType           reuseLevel                     preferredLabel                                          altLabels hiddenLabels    status              modifiedDate scopeNote definition                                           inScheme                                        description
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0005c151-5b5a...  skill/competence      sector-specific               manage musical staff  manage music staff\ncoordinate duties of music...          NaN  released  2023-11-30T15:53:37.136Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Assign and manage staff tasks in areas such as...
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/00064735-8fad...  skill/competence  occupation-specific  supervise correctional procedures  manage prison procedures\nmonitor correctional...          NaN  released  2023-11-30T15:04:00.689Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Supervise the operations of a correctional fac...
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/000709ed-2be5...  skill/competence      sector-specific    apply anti-oppressive practices  make use of anti-oppressive practices\nuse ant...          NaN  released   2023-11-28T10:45:53.54Z       NaN        NaN  http://data.europa.eu/esco/concept-scheme/skil...  Identify oppression in societies, economies, c...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillsHierarchy_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **640** | Columns: **14**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| Level 0 URI | str | 0 | 0.0 | 4 | http://data.europa.eu/esco/skill/e35a5936-091d-4e87-bafe-f26 |
| Level 0 preferred term | str | 0 | 0.0 | 4 | language skills and knowledge |
| Level 1 URI | str | 4 | 0.6 | 28 | http://data.europa.eu/esco/skill/43f425aa-f45d-4bb4-a200-6f8 |
| Level 1 preferred term | str | 4 | 0.6 | 28 | languages |
| Level 2 URI | str | 32 | 5.0 | 156 | http://data.europa.eu/esco/skill/15dfca7a-5dde-4199-bad3-c00 |
| Level 2 preferred term | str | 32 | 5.0 | 156 | handling and disposing of waste and hazardous materials |
| Level 3 URI | str | 188 | 29.4 | 452 | http://data.europa.eu/esco/skill/61d1dab2-6007-4b7c-9380-cd8 |
| Level 3 preferred term | str | 188 | 29.4 | 452 | disposing of non-hazardous waste or debris |
| Description | str | 133 | 20.8 | 425 | Ability to communicate through reading, writing, speaking an |
| Scope note | str | 316 | 49.4 | 281 | Excludes:
- all languages that are actively used as a mother |
| Level 0 code | str | 0 | 0.0 | 4 | L |
| Level 1 code | str | 4 | 0.6 | 28 | L1 |
| Level 2 code | str | 32 | 5.0 | 156 | S6.13 |
| Level 3 code | str | 188 | 29.4 | 452 | S6.13.2 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)

Sample rows:

```
                                         Level 0 URI         Level 0 preferred term                                        Level 1 URI Level 1 preferred term Level 2 URI Level 2 preferred term Level 3 URI Level 3 preferred term                                        Description                                         Scope note Level 0 code Level 1 code Level 2 code Level 3 code
0  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge                                                NaN                    NaN         NaN                    NaN         NaN                    NaN                                                NaN                                                NaN            L          NaN          NaN          NaN
1  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge  http://data.europa.eu/esco/skill/43f425aa-f45d...              languages         NaN                    NaN         NaN                    NaN  Ability to communicate through reading, writin...                                                NaN            L           L1          NaN          NaN
2  http://data.europa.eu/esco/skill/e35a5936-091d...  language skills and knowledge  http://data.europa.eu/esco/skill/e434e71a-f068...    classical languages         NaN                    NaN         NaN                    NaN  All dead languages, no longer actively used, o...  Excludes:\n- all languages that are actively u...            L           L2          NaN          NaN
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/skillSkillRelations_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **5,818** | Columns: **5**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| originalSkillUri | str | 0 | 0.0 | 3,759 | http://data.europa.eu/esco/skill/00064735-8fad-454b-90c7-ed8 |
| originalSkillType | str | 0 | 0.0 | 2 | skill/competence |
| relationType | str | 0 | 0.0 | 2 | optional |
| relatedSkillType | str | 0 | 0.0 | 2 | knowledge |
| relatedSkillUri | str | 0 | 0.0 | 1,953 | http://data.europa.eu/esco/skill/d4a0744a-508b-4a5e-97a5-ad1 |

- Candidate single-column keys: none
- Looks like ESCO (URI columns present)
- relationType values: {'optional': 5629, 'essential': 189}

Sample rows:

```
                                    originalSkillUri originalSkillType relationType relatedSkillType                                    relatedSkillUri
0  http://data.europa.eu/esco/skill/00064735-8fad...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/d4a0744a-508b...
1  http://data.europa.eu/esco/skill/000bb1e4-89f0...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/b70ab677-5781...
2  http://data.europa.eu/esco/skill/0023e7a5-43da...  skill/competence     optional        knowledge  http://data.europa.eu/esco/skill/5753e2ca-8934...
```

## ESCO dataset - v1.2.1 - classification - en - csv_dbms.zip :: ESCO dataset - v1.2.1 - classification - en - csv_dbms/transversalSkillsCollection_en.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **95** | Columns: **10**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| conceptType | str | 0 | 0.0 | 1 | KnowledgeSkillCompetence |
| conceptUri | str | 0 | 0.0 | 95 | http://data.europa.eu/esco/skill/001115fb-569f-4ee6-8381-c68 |
| skillType | str | 0 | 0.0 | 1 | skill/competence |
| reuseLevel | str | 0 | 0.0 | 2 | transversal |
| preferredLabel | str | 0 | 0.0 | 95 | show initiative |
| status | str | 0 | 0.0 | 1 | released |
| altLabels | str | 0 | 0.0 | 95 | initiate action / be a driving force / give impetus / take t |
| description | str | 0 | 0.0 | 95 | Be proactive and take the first step in an action without wa |
| broaderConceptUri | str | 0 | 0.0 | 24 | http://data.europa.eu/esco/skill/91860993-1a8b-4473-91f3-600 |
| broaderConceptPT | str | 0 | 0.0 | 24 | taking a proactive approach |

- Candidate single-column keys: `conceptUri`, `preferredLabel`, `altLabels`, `description`
- Looks like ESCO (URI columns present)

Sample rows:

```
                conceptType                                         conceptUri         skillType   reuseLevel                                     preferredLabel    status                                          altLabels                                        description                                  broaderConceptUri                               broaderConceptPT
0  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/001115fb-569f...  skill/competence  transversal                                    show initiative  released  initiate action | be a driving force | give im...  Be proactive and take the first step in an act...  http://data.europa.eu/esco/skill/91860993-1a8b...                    taking a proactive approach
1  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/0171653e-c8e9...  skill/competence  transversal  adopt ways to foster biodiversity and animal w...  released  concretely support biodiversity and animal wel...  Engage in behaviours that help maintaining sta...  http://data.europa.eu/esco/skill/80cf002a-6586...  applying environmental skills and competences
2  KnowledgeSkillCompetence  http://data.europa.eu/esco/skill/045f71e6-0699...  skill/competence  transversal                                      advise others  released  mentor others | mentor individuals | counsel o...  Offer suggestions about the best course of act...  http://data.europa.eu/esco/skill/82463bb1-85d1...                              supporting others
```

## essential_skills_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **18,200** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 910 | 11-1011.00 |
| Title | str | 0 | 0.0 | 910 | Chief Executives |
| Element ID | str | 0 | 0.0 | 10 | 2.A.1.a |
| Element Name | str | 0 | 0.0 | 10 | Reading Comprehension |
| Scale ID | str | 0 | 0.0 | 2 | IM |
| Scale Name | str | 0 | 0.0 | 2 | Importance |
| Data Value | float64 | 0 | 0.0 | 49 | 4.12 |
| N | int64 | 0 | 0.0 | 1 | 8 |
| Standard Error | float64 | 0 | 0.0 | 41 | 0.125 |
| Lower CI Bound | float64 | 0 | 0.0 | 216 | 3.88 |
| Upper CI Bound | float64 | 0 | 0.0 | 234 | 4.37 |
| Recommend Suppress | str | 0 | 0.0 | 2 | N |
| Not Relevant | str | 9,100 | 50.0 | 2 | N |
| Date | str | 0 | 0.0 | 17 | 08/2023 |
| Domain Source | str | 0 | 0.0 | 1 | Analyst |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code, Element ID, Element Name, Scale ID, Data Value, Recommend Suppress, Not Relevant)
- Scale ID values: {'IM': 9100, 'LV': 9100}
- Data Value range per scale: {'IM': {'min': 1.0, 'max': 5.0}, 'LV': {'min': 0.0, 'max': 6.0}}
- Distinct occupations: 910
- Distinct elements (skills/knowledge/activities): 10

Sample rows:

```
  O*NET-SOC Code             Title Element ID           Element Name Scale ID  Scale Name  Data Value  N  Standard Error  Lower CI Bound  Upper CI Bound Recommend Suppress Not Relevant     Date Domain Source
0     11-1011.00  Chief Executives    2.A.1.a  Reading Comprehension       IM  Importance        4.12  8           0.125          3.8800          4.3700                  N          NaN  08/2023       Analyst
1     11-1011.00  Chief Executives    2.A.1.a  Reading Comprehension       LV       Level        4.62  8           0.183          4.2664          4.9836                  N            N  08/2023       Analyst
2     11-1011.00  Chief Executives    2.A.1.b       Active Listening       IM  Importance        4.00  8           0.000          4.0000          4.0000                  N          NaN  08/2023       Analyst
```

## job_titles_csv.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **54,269** | Columns: **5**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 1,016 | 11-1011.00 |
| Title | str | 0 | 0.0 | 1,016 | Chief Executives |
| Job Title | str | 0 | 0.0 | 44,779 | Aeronautics Commission Director |
| Short Title | str | 49,814 | 91.8 | 3,576 | BD Executive |
| Source(s) | str | 0 | 0.0 | 89 | 08 |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code)
- Distinct occupations: 1,016

Sample rows:

```
  O*NET-SOC Code             Title                        Job Title Short Title Source(s)
0     11-1011.00  Chief Executives  Aeronautics Commission Director         NaN        08
1     11-1011.00  Chief Executives                     Agency Owner         NaN        10
2     11-1011.00  Chief Executives   Agricultural Services Director         NaN        08
```

## knowledge_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **60,060** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 910 | 11-1011.00 |
| Title | str | 0 | 0.0 | 910 | Chief Executives |
| Element ID | str | 0 | 0.0 | 33 | 2.C.1.a |
| Element Name | str | 0 | 0.0 | 33 | Administration and Management |
| Scale ID | str | 0 | 0.0 | 2 | IM |
| Scale Name | str | 0 | 0.0 | 2 | Importance |
| Data Value | float64 | 0 | 0.0 | 679 | 4.78 |
| N | float64 | 594 | 1.0 | 80 | 28.0 |
| Standard Error | float64 | 16,962 | 28.2 | 8,322 | 0.1102 |
| Lower CI Bound | float64 | 17,698 | 29.5 | 21,204 | 4.5564 |
| Upper CI Bound | float64 | 17,698 | 29.5 | 28,329 | 5.0 |
| Recommend Suppress | str | 16,434 | 27.4 | 2 | N |
| Not Relevant | str | 30,030 | 50.0 | 2 | N |
| Date | str | 0 | 0.0 | 23 | 08/2023 |
| Domain Source | str | 0 | 0.0 | 3 | Incumbent |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code, Element ID, Element Name, Scale ID, Data Value, Recommend Suppress, Not Relevant)
- Scale ID values: {'IM': 30030, 'LV': 30030}
- Data Value range per scale: {'IM': {'min': 1.0, 'max': 5.0}, 'LV': {'min': 0.0, 'max': 6.97}}
- Distinct occupations: 910
- Distinct elements (skills/knowledge/activities): 33

Sample rows:

```
  O*NET-SOC Code             Title Element ID                   Element Name Scale ID  Scale Name  Data Value     N  Standard Error  Lower CI Bound  Upper CI Bound Recommend Suppress Not Relevant     Date Domain Source
0     11-1011.00  Chief Executives    2.C.1.a  Administration and Management       IM  Importance        4.78  28.0          0.1102          4.5564          5.0000                  N          NaN  08/2023     Incumbent
1     11-1011.00  Chief Executives    2.C.1.a  Administration and Management       LV       Level        6.50  28.0          0.2130          6.0666          6.9409                  N            N  08/2023     Incumbent
2     11-1011.00  Chief Executives    2.C.1.b                 Administrative       IM  Importance        2.42  28.0          0.4651          1.4662          3.3749                  N          NaN  08/2023     Incumbent
```

## occupation_data_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **1,016** | Columns: **3**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 1,016 | 11-1011.00 |
| Title | str | 0 | 0.0 | 1,016 | Chief Executives |
| Description | str | 0 | 0.0 | 1,016 | Determine and formulate policies and provide overall directi |

- Candidate single-column keys: `O*NET-SOC Code`, `Title`, `Description`
- Looks like O*NET (columns found: O*NET-SOC Code)
- Distinct occupations: 1,016

Sample rows:

```
  O*NET-SOC Code                            Title                                        Description
0     11-1011.00                 Chief Executives  Determine and formulate policies and provide o...
1     11-1011.03    Chief Sustainability Officers  Communicate and coordinate with management, sh...
2     11-1021.00  General and Operations Managers  Plan, direct, or coordinate the operations of ...
```

## scales_reference_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **33** | Columns: **4**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| Scale ID | str | 0 | 0.0 | 33 | AO |
| Scale Name | str | 0 | 0.0 | 30 | Automation |
| Minimum | int64 | 0 | 0.0 | 3 | 1 |
| Maximum | int64 | 0 | 0.0 | 6 | 5 |

- Candidate single-column keys: `Scale ID`
- Looks like O*NET (columns found: Scale ID)
- Scale ID values: {'AO': 1, 'CF': 1, 'CN': 1, 'CT': 1, 'CTP': 1, 'CX': 1, 'CXP': 1, 'DR': 1, 'DS': 1, 'EX': 1, 'FM': 1, 'FT': 1, 'HW': 1, 'IH': 1, 'IJ': 1, 'IM': 1, 'IP': 1, 'LC': 1, 'LV': 1, 'OI': 1, 'OJ': 1, 'PT': 1, 'PX': 1, 'RE': 1, 'RL': 1, 'RQ': 1, 'RT': 1, 'RW': 1, 'SR': 1, 'TI': 1, 'VH': 1, 'WI': 1, 'WS': 1}

Sample rows:

```
  Scale ID         Scale Name  Minimum  Maximum
0       AO         Automation        1        5
1       CF          Frequency        1        5
2       CN  Amount of Contact        1        5
```

## software_skills_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **31,821** | Columns: **7**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 923 | 11-1011.00 |
| Title | str | 0 | 0.0 | 923 | Chief Executives |
| Workplace Example | str | 0 | 0.0 | 8,753 | Adobe Acrobat |
| Element ID | str | 0 | 0.0 | 134 | 2.E.5.b |
| Element Name | str | 0 | 0.0 | 134 | Document management software |
| Hot Technology | str | 0 | 0.0 | 2 | Y |
| In Demand | str | 0 | 0.0 | 2 | N |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code, Element ID, Element Name, Hot Technology)
- Distinct occupations: 923
- Distinct elements (skills/knowledge/activities): 134

Sample rows:

```
  O*NET-SOC Code             Title Workplace Example Element ID                                 Element Name Hot Technology In Demand
0     11-1011.00  Chief Executives     Adobe Acrobat    2.E.5.b                 Document management software              Y         N
1     11-1011.00  Chief Executives   AdSense Tracker    2.E.6.f  Data base user interface and query software              N         N
2     11-1011.00  Chief Executives    Atlassian JIRA    2.E.5.a                    Content workflow software              Y         N
```

## test_dbms.json

- Records: **3,569**
- Keys (record count): {'idx': 3569, 'tokens': 3569, 'tags_skill': 3569, 'tags_knowledge': 3569, 'source': 3569}
- `tags_skill` vocabulary: {'O': 38560, 'I': 3136, 'B': 1090}
- `tags_knowledge` vocabulary: {'O': 40698, 'B': 1174, 'I': 914}
- `tokens` length: min 1, max 149, mean 12.0

Example record:

```json
{"idx": 1, "tokens": ["Full", "Stack", "Software", "Engineer", "-", "Java", "/", "JavaScript"], "tags_skill": ["O", "O", "O", "O", "O", "O", "O", "O"], "tags_knowledge": ["O", "O", "O", "O", "O", "O", "O", "O"], "source": "tech"}
```

## train_dbms.json

- Records: **4,800**
- Keys (record count): {'idx': 4800, 'tokens': 4800, 'tags_skill': 4800, 'tags_knowledge': 4800, 'source': 4800}
- `tags_skill` vocabulary: {'O': 83382, 'I': 7850, 'B': 2221}
- `tags_knowledge` vocabulary: {'O': 87888, 'B': 2969, 'I': 2596}
- `tokens` length: min 1, max 748, mean 19.5

Example record:

```json
{"idx": 1, "tokens": ["Senior", "QA", "Engineer", "(", "m/f/d", ")", "<ORGANIZATION>"], "tags_skill": ["O", "O", "O", "O", "O", "O", "O"], "tags_knowledge": ["O", "O", "O", "O", "O", "O", "O"], "source": "tech"}
```

## transferable_skills_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **45,500** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 910 | 11-1011.00 |
| Title | str | 0 | 0.0 | 910 | Chief Executives |
| Element ID | str | 0 | 0.0 | 25 | 2.B.1.a |
| Element Name | str | 0 | 0.0 | 25 | Social Perceptiveness |
| Scale ID | str | 0 | 0.0 | 2 | IM |
| Scale Name | str | 0 | 0.0 | 2 | Importance |
| Data Value | float64 | 0 | 0.0 | 46 | 4.12 |
| N | int64 | 0 | 0.0 | 1 | 8 |
| Standard Error | float64 | 0 | 0.0 | 55 | 0.125 |
| Lower CI Bound | float64 | 0 | 0.0 | 297 | 3.88 |
| Upper CI Bound | float64 | 0 | 0.0 | 322 | 4.37 |
| Recommend Suppress | str | 0 | 0.0 | 2 | N |
| Not Relevant | str | 22,750 | 50.0 | 2 | N |
| Date | str | 0 | 0.0 | 17 | 08/2023 |
| Domain Source | str | 0 | 0.0 | 1 | Analyst |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code, Element ID, Element Name, Scale ID, Data Value, Recommend Suppress, Not Relevant)
- Scale ID values: {'IM': 22750, 'LV': 22750}
- Data Value range per scale: {'IM': {'min': 1.0, 'max': 5.0}, 'LV': {'min': 0.0, 'max': 5.75}}
- Distinct occupations: 910
- Distinct elements (skills/knowledge/activities): 25

Sample rows:

```
  O*NET-SOC Code             Title Element ID           Element Name Scale ID  Scale Name  Data Value  N  Standard Error  Lower CI Bound  Upper CI Bound Recommend Suppress Not Relevant     Date Domain Source
0     11-1011.00  Chief Executives    2.B.1.a  Social Perceptiveness       IM  Importance        4.12  8          0.1250          3.8800          4.3700                  N          NaN  08/2023       Analyst
1     11-1011.00  Chief Executives    2.B.1.a  Social Perceptiveness       LV       Level        4.25  8          0.1637          3.9292          4.5708                  N            N  08/2023       Analyst
2     11-1011.00  Chief Executives    2.B.1.b           Coordination       IM  Importance        4.25  8          0.1637          3.9292          4.5708                  N          NaN  08/2023       Analyst
```

## work_activities_dbms.csv

- Encoding: `utf-8` | Delimiter: `','`
- Rows: **74,702** | Columns: **15**
- Fully duplicated rows: **0**

| Column | dtype | Nulls | Null % | Distinct | Example |
| --- | --- | --- | --- | --- | --- |
| O*NET-SOC Code | str | 0 | 0.0 | 911 | 11-1011.00 |
| Title | str | 0 | 0.0 | 911 | Chief Executives |
| Element ID | str | 0 | 0.0 | 41 | 4.A.1.a.1 |
| Element Name | str | 0 | 0.0 | 41 | Getting Information |
| Scale ID | str | 0 | 0.0 | 2 | IM |
| Scale Name | str | 0 | 0.0 | 2 | Importance |
| Data Value | float64 | 0 | 0.0 | 675 | 4.56 |
| N | float64 | 738 | 1.0 | 71 | 29.0 |
| Standard Error | float64 | 21,074 | 28.2 | 8,590 | 0.1559 |
| Lower CI Bound | float64 | 21,098 | 28.2 | 29,681 | 4.2369 |
| Upper CI Bound | float64 | 21,098 | 28.2 | 29,708 | 4.8756 |
| Recommend Suppress | str | 20,418 | 27.3 | 2 | N |
| Not Relevant | str | 37,351 | 50.0 | 2 | N |
| Date | str | 0 | 0.0 | 23 | 08/2023 |
| Domain Source | str | 0 | 0.0 | 3 | Incumbent |

- Candidate single-column keys: none
- Looks like O*NET (columns found: O*NET-SOC Code, Element ID, Element Name, Scale ID, Data Value, Recommend Suppress, Not Relevant)
- Scale ID values: {'IM': 37351, 'LV': 37351}
- Data Value range per scale: {'IM': {'min': 1.0, 'max': 5.0}, 'LV': {'min': 0.0, 'max': 6.94}}
- Distinct occupations: 911
- Distinct elements (skills/knowledge/activities): 41

Sample rows:

```
  O*NET-SOC Code             Title Element ID                                      Element Name Scale ID  Scale Name  Data Value     N  Standard Error  Lower CI Bound  Upper CI Bound Recommend Suppress Not Relevant     Date Domain Source
0     11-1011.00  Chief Executives  4.A.1.a.1                               Getting Information       IM  Importance        4.56  29.0          0.1559          4.2369          4.8756                  N          NaN  08/2023     Incumbent
1     11-1011.00  Chief Executives  4.A.1.a.1                               Getting Information       LV       Level        4.89  30.0          0.1727          4.5393          5.2458                  N            N  08/2023     Incumbent
2     11-1011.00  Chief Executives  4.A.1.a.2  Monitoring Processes, Materials, or Surroundings       IM  Importance        4.25  30.0          0.2125          3.8130          4.6823                  N          NaN  08/2023     Incumbent
```
