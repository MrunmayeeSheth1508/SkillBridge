# SkillBridge skill extraction - SkillSpan evaluation

- Split: **test**, sentences: **3,569**
- Matching: **exact**, lexicon `core.mv_skill_lexicon` (O*NET + ESCO aliases)
- Runtime: **3.6 s** inside PostgreSQL (1.0 ms per sentence), PostgreSQL 16.16

Strict = identical span boundaries; Loose = at least one token overlap.

## Overall and per SkillSpan subset

| Subset | Gold spans | Predicted | Strict P | Strict R | Strict F1 | Loose P | Loose R | Loose F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All spans | 2,265 | 1,279 | 0.309 | 0.174 | **0.223** | 0.532 | 0.293 | **0.378** |
| house | 1,019 | 548 | 0.212 | 0.114 | **0.148** | 0.436 | 0.227 | **0.298** |
| tech | 1,246 | 731 | 0.382 | 0.224 | **0.282** | 0.603 | 0.348 | **0.441** |

## Per span type

Technologies from O*NET are counted as *knowledge*, matching SkillSpan's guidelines.

| Type | Gold spans | Predicted | Strict P | Strict R | Strict F1 | Loose P | Loose R | Loose F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill | 1,091 | 169 | 0.053 | 0.008 | **0.014** | 0.302 | 0.046 | **0.080** |
| knowledge | 1,174 | 1,110 | 0.329 | 0.311 | **0.320** | 0.455 | 0.419 | **0.436** |

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
| NET -> LabOne NET | 9 |
| SQL -> SoftRisk Technologies SoftRisk SQL | 9 |
| C# -> C# | 9 |
| net -> Visual Basic | 8 |
| stay focused -> stay alert | 7 |
| React -> React | 7 |

## Most frequent false positives (no overlap with any gold span)

| Prediction | Count |
| --- | --- |
| Danish -> Danish | 23 |
| design -> Design | 13 |
| English -> English | 13 |
| energy -> energy | 12 |
| pregnancy -> pregnancy | 10 |
| Plan -> plan | 10 |
| Java -> Oracle Java | 9 |
| DevOps -> DevOps | 9 |
| creative solutions -> design thinking | 8 |
| plan -> plan | 8 |
| lead -> lead others | 8 |
| agile -> ICT project management methodologies | 8 |
| communication -> communication | 8 |
| email -> electronic communication | 8 |
| transport -> logistics | 7 |

## Most frequent missed gold spans

| Gold span | Count |
| --- | --- |
| Financial Services | 13 |
| automation | 11 |
| reactjs | 9 |
| development | 9 |
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
| building an innovative culture | 7 |

## Reading these results

This is a lexicon baseline: it can only find skills whose wording (or a close spelling) exists in O*NET/ESCO. SkillSpan annotates long, free-form spans such as *"work independently in a fast-paced environment"*, so strict recall is expected to be low and loose scores higher. The trained span tagger (Phase 5b) is compared against this baseline in the paper.