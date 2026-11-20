# SkillBridge skill extraction - SkillSpan evaluation

- Split: **test**, sentences: **3,569**
- Matching: **exact**, lexicon `core.mv_skill_lexicon`: 101,512 O*NET + ESCO labels, 56 pruned using the train split
- Runtime: **4.1 s** inside PostgreSQL (1.2 ms per sentence), PostgreSQL 16.16

Strict = identical span boundaries; Loose = at least one token overlap.

## Overall and per SkillSpan subset

| Subset | Gold spans | Predicted | Strict P | Strict R | Strict F1 | Loose P | Loose R | Loose F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All spans | 2,265 | 1,066 | 0.356 | 0.168 | **0.228** | 0.609 | 0.281 | **0.384** |
| house | 1,019 | 436 | 0.248 | 0.106 | **0.148** | 0.511 | 0.214 | **0.302** |
| tech | 1,246 | 630 | 0.432 | 0.218 | **0.290** | 0.676 | 0.335 | **0.448** |

## Per span type

Technologies from O*NET are counted as *knowledge*, matching SkillSpan's guidelines.

| Type | Gold spans | Predicted | Strict P | Strict R | Strict F1 | Loose P | Loose R | Loose F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill | 1,091 | 112 | 0.080 | 0.008 | **0.015** | 0.366 | 0.037 | **0.067** |
| knowledge | 1,174 | 954 | 0.367 | 0.298 | **0.329** | 0.512 | 0.405 | **0.452** |

## Most frequent correct matches

| Match | Count |
| --- | --- |
| English -> English | 30 |
| design -> Design | 29 |
| communication -> communication | 21 |
| java -> Java (computer programming) | 19 |
| Java -> Oracle Java | 17 |
| Azure -> Microsoft Azure software | 15 |
| agile -> ICT project management methodologies | 13 |
| Python -> Python | 10 |
| python -> Python | 10 |
| SQL -> Structured query language SQL | 9 |
| NET -> Visual Basic | 9 |
| net -> Visual Basic | 8 |
| React -> React | 7 |
| DevOps -> DevOps | 7 |
| javascript -> JavaScript | 6 |

## Most frequent false positives (no overlap with any gold span)

| Prediction | Count |
| --- | --- |
| design -> Design | 13 |
| English -> English | 13 |
| energy -> energy | 12 |
| Java -> Oracle Java | 9 |
| DevOps -> DevOps | 9 |
| lead -> lead others | 8 |
| agile -> ICT project management methodologies | 8 |
| communication -> communication | 8 |
| programming languages -> Programming languages | 6 |
| Android -> Google Android | 6 |
| science -> Science | 6 |
| wind turbines -> types of wind turbines | 6 |
| machine learning -> machine learning | 5 |
| source -> Source (digital game creation systems) | 5 |
| UX -> SugarCRM Sugar UX | 5 |

## Most frequent missed gold spans

| Gold span | Count |
| --- | --- |
| Financial Services | 13 |
| automation | 11 |
| reactjs | 9 |
| development | 9 |
| C# | 9 |
| testing | 9 |
| Financial Technology | 8 |
| cloud | 8 |
| c# | 8 |
| qa | 8 |
| teaching | 8 |
| solving business problems | 7 |
| apply your depth of knowledge and expertise | 7 |
| partner continuously with your many stakeholders | 7 |
| achieve organizational goals | 7 |

## Reading these results

This is a lexicon baseline: it can only find skills whose wording (or a close spelling) exists in O*NET/ESCO. SkillSpan annotates long, free-form spans such as *"work independently in a fast-paced environment"*, so strict recall is expected to be low and loose scores higher. The trained span tagger (Phase 5b) is compared against this baseline in the paper.