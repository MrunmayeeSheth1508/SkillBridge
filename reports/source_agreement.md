# RQ1 - Evidence-aware requirements: O*NET vs ESCO

Target careers only. Work activities excluded. ESCO evidence reaches O*NET careers through the official crosswalk (default: exact + close matches; section 4 compares with broad/narrow).

Tiers make the sources comparable: **core** = O*NET importance >= 3.5/5, ESCO *essential*, or an O*NET In-Demand tool; **supporting** = O*NET 2.5-3.5, ESCO *optional*, other tools; **peripheral** = O*NET < 2.5.

## 1. Coverage: who requires what

| Domain | Career | O*NET only | ESCO only | Both |
| --- | --- | --- | --- | --- |
| Business & finance analytics | Actuaries | 104 | 35 | 0 |
| Business & finance analytics | Credit Analysts | 103 | 85 | 0 |
| Business & finance analytics | Financial Quantitative Analysts | 99 | 43 | 0 |
| Business & finance analytics | Logistics Analysts | 116 | 0 | 0 |
| Business & finance analytics | Management Analysts | 281 | 84 | 0 |
| Business & finance analytics | Market Research Analysts and Marketing Specialists | 210 | 113 | 0 |
| Data & AI | Computer and Information Research Scientists | 229 | 102 | 2 |
| Data & AI | Data Scientists | 142 | 223 | 10 |
| Data & AI | Database Administrators | 348 | 60 | 7 |
| Data & AI | Database Architects | 390 | 0 | 0 |
| Data & AI | Operations Research Analysts | 175 | 163 | 2 |
| Data & AI | Statisticians | 129 | 140 | 2 |
| Mechanical & manufacturing engineering | Automotive Engineers | 150 | 129 | 2 |
| Mechanical & manufacturing engineering | Industrial Engineers | 165 | 101 | 2 |
| Mechanical & manufacturing engineering | Manufacturing Engineers | 97 | 147 | 4 |
| Mechanical & manufacturing engineering | Mechanical Engineering Technologists and Technicians | 109 | 161 | 3 |
| Mechanical & manufacturing engineering | Mechanical Engineers | 159 | 92 | 0 |
| Mechanical & manufacturing engineering | Robotics Engineers | 133 | 159 | 2 |
| Software engineering | Computer Systems Analysts | 355 | 175 | 22 |
| Software engineering | Network and Computer Systems Administrators | 315 | 86 | 12 |
| Software engineering | Software Developers | 496 | 0 | 0 |
| Software engineering | Software Quality Assurance Analysts and Testers | 468 | 124 | 28 |
| Software engineering | Web and Digital Interface Designers | 273 | 132 | 25 |
| Software engineering | Web Developers | 290 | 114 | 25 |

Across 24 target careers: **5,336** career-skill requirements come from O*NET only, **2,468** from ESCO only and **148** from both (1.9% overlap). Each source alone would miss the other's requirements; most of the non-overlap is vocabulary (O*NET's 35 broad skills and named tools vs ESCO's fine-grained skills).

## 2. Agreement on skills both sources require

|  | ESCO peripheral | ESCO supporting (optional) | ESCO core (essential) |
| --- | --- | --- | --- |
| O*NET core | 0 | 26 | 14 |
| O*NET supporting | 0 | 102 | 5 |
| O*NET peripheral | 0 | 0 | 1 |

- Shared career-skill pairs: **148**
- Same tier: **78.4%**
- Cohen's kappa (O*NET tier vs ESCO tier): **0.361**
- knowledge: 13 pairs, same tier 84.6%, kappa 0.567
- skill: 5 pairs, same tier 60.0%, kappa 0.333
- technology: 130 pairs, same tier 78.5%, kappa 0.109

Kappa near 0 means the two taxonomies' judgements of *how* important a shared skill is are close to independent - a merged list would hide this.

## 3. Impact on what the learner is told (demo learner, transfer credit on)

| Career | Requirements (aggregated) | ...with O*NET evidence | Added by ESCO only (essential) | Readiness: O*NET only | Readiness: O*NET + ESCO |
| --- | --- | --- | --- | --- | --- |
| Actuaries | 59 | 45 | 14 | 0.279 | 0.200 |
| Automotive Engineers | 132 | 62 | 70 | 0.303 | 0.122 |
| Computer and Information Research Scientists | 140 | 86 | 54 | 0.140 | 0.080 |
| Computer Systems Analysts | 143 | 79 | 64 | 0.167 | 0.085 |
| Credit Analysts | 91 | 40 | 51 | 0.356 | 0.122 |
| Data Scientists | 173 | 57 | 116 | 0.197 | 0.059 |
| Database Administrators | 114 | 87 | 27 | 0.119 | 0.088 |
| Database Architects | 53 | 53 | 0 | 0.262 | 0.262 |
| Financial Quantitative Analysts | 70 | 49 | 21 | 0.283 | 0.179 |
| Industrial Engineers | 97 | 59 | 38 | 0.321 | 0.166 |
| Logistics Analysts | 54 | 54 | 0 | 0.259 | 0.259 |
| Management Analysts | 102 | 60 | 42 | 0.229 | 0.120 |
| Manufacturing Engineers | 101 | 63 | 38 | 0.299 | 0.162 |
| Market Research Analysts and Marketing Specialists | 94 | 46 | 48 | 0.283 | 0.117 |
| Mechanical Engineering Technologists and Technicians | 105 | 55 | 50 | 0.314 | 0.133 |
| Mechanical Engineers | 106 | 66 | 40 | 0.294 | 0.160 |
| Network and Computer Systems Administrators | 98 | 76 | 22 | 0.159 | 0.121 |
| Operations Research Analysts | 136 | 49 | 87 | 0.329 | 0.100 |
| Robotics Engineers | 130 | 66 | 64 | 0.246 | 0.109 |
| Software Developers | 75 | 75 | 0 | 0.133 | 0.133 |
| Software Quality Assurance Analysts and Testers | 120 | 85 | 35 | 0.140 | 0.099 |
| Statisticians | 126 | 50 | 76 | 0.279 | 0.093 |
| Web and Digital Interface Designers | 121 | 77 | 44 | 0.121 | 0.073 |
| Web Developers | 131 | 96 | 35 | 0.096 | 0.071 |

ESCO adds **40.3%** of the requirements shown to the learner. Readiness changes by **10.4 points** on average (max 23.4) when ESCO evidence is kept alongside O*NET.

## 4. Sensitivity: which crosswalk links to trust

Broad and narrow links import requirements of *related* occupations. Re-running with exact + close links only (computed in a rolled-back transaction):

| Crosswalk links used | Overlap (both sources) | Cohen's kappa | Requirements added by ESCO | Mean readiness change |
| --- | --- | --- | --- | --- |
| exact + close + broad + narrow | 2.6% | 0.307 | 51.9% | 13.5 pts |
| exact + close only | 1.9% | 0.361 | 40.3% | 10.4 pts |

Readiness is also pessimistic for a structural reason: the learner's skills are O*NET skills and transfer edges do not cross into ESCO's vocabulary, so ESCO-only requirements count as fully missing. Cross-taxonomy alignment (embeddings) addresses this.

## 5. Strongest disagreements (tier gap 2 first)

| Career | Skill | O*NET evidence | O*NET tier | ESCO evidence | ESCO tier |
| --- | --- | --- | --- | --- | --- |
| Industrial Engineers | Troubleshooting | scored | peripheral | essential | core |
| Computer Systems Analysts | Git | present | supporting | essential | core |
| Computer Systems Analysts | Python | present | core | optional | supporting |
| Data Scientists | Apache Hadoop | present | core | optional | supporting |
| Data Scientists | C++ | present | core | optional | supporting |
| Data Scientists | R | present | core | optional | supporting |
| Database Administrators | Microsoft Access | present | core | optional | supporting |
| Database Administrators | MySQL | present | core | optional | supporting |
| Database Administrators | PostgreSQL | present | core | optional | supporting |
| Manufacturing Engineers | Mathematics | scored | core | optional | supporting |
| Mechanical Engineering Technologists and Technicians | Physics | scored | supporting | essential | core |
| Mechanical Engineering Technologists and Technicians | Troubleshooting | scored | supporting | essential | core |
| Network and Computer Systems Administrators | Python | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | Ada | present | supporting | essential | core |
| Software Quality Assurance Analysts and Testers | C# | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | C++ | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | JavaScript | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | Jenkins CI | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | Python | present | core | optional | supporting |
| Software Quality Assurance Analysts and Testers | Selenium | present | core | optional | supporting |
| Web and Digital Interface Designers | Adobe Illustrator | present | core | optional | supporting |
| Web and Digital Interface Designers | Adobe Photoshop | present | core | optional | supporting |
| Web and Digital Interface Designers | Git | present | supporting | essential | core |
| Web and Digital Interface Designers | JavaScript | present | core | optional | supporting |
| Web and Digital Interface Designers | TypeScript | present | core | optional | supporting |
