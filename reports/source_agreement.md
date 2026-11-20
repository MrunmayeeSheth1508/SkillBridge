# RQ1 - Evidence-aware requirements: O*NET vs ESCO

Target careers only. Work activities excluded. ESCO evidence reaches O*NET careers through the official crosswalk (exact / close / narrow / broad matches).

Tiers make the sources comparable: **core** = O*NET importance >= 3.5/5, ESCO *essential*, or an O*NET In-Demand tool; **supporting** = O*NET 2.5-3.5, ESCO *optional*, other tools; **peripheral** = O*NET < 2.5.

## 1. Coverage: who requires what

| Domain | Career | O*NET only | ESCO only | Both |
| --- | --- | --- | --- | --- |
| Business & finance analytics | Actuaries | 104 | 66 | 0 |
| Business & finance analytics | Credit Analysts | 103 | 123 | 0 |
| Business & finance analytics | Financial Quantitative Analysts | 99 | 110 | 0 |
| Business & finance analytics | Logistics Analysts | 114 | 80 | 2 |
| Business & finance analytics | Management Analysts | 281 | 84 | 0 |
| Business & finance analytics | Market Research Analysts and Marketing Specialists | 208 | 281 | 2 |
| Data & AI | Computer and Information Research Scientists | 229 | 102 | 2 |
| Data & AI | Data Scientists | 140 | 235 | 12 |
| Data & AI | Database Administrators | 333 | 175 | 22 |
| Data & AI | Database Architects | 364 | 149 | 26 |
| Data & AI | Operations Research Analysts | 175 | 163 | 2 |
| Data & AI | Statisticians | 128 | 156 | 3 |
| Mechanical & manufacturing engineering | Automotive Engineers | 150 | 261 | 2 |
| Mechanical & manufacturing engineering | Industrial Engineers | 163 | 169 | 4 |
| Mechanical & manufacturing engineering | Manufacturing Engineers | 97 | 193 | 4 |
| Mechanical & manufacturing engineering | Mechanical Engineering Technologists and Technicians | 109 | 169 | 3 |
| Mechanical & manufacturing engineering | Mechanical Engineers | 157 | 169 | 2 |
| Mechanical & manufacturing engineering | Robotics Engineers | 133 | 159 | 2 |
| Software engineering | Computer Systems Analysts | 355 | 198 | 22 |
| Software engineering | Network and Computer Systems Administrators | 312 | 151 | 15 |
| Software engineering | Software Developers | 454 | 297 | 42 |
| Software engineering | Software Quality Assurance Analysts and Testers | 468 | 160 | 28 |
| Software engineering | Web and Digital Interface Designers | 273 | 132 | 25 |
| Software engineering | Web Developers | 290 | 114 | 25 |

Across 24 target careers: **5,239** career-skill requirements come from O*NET only, **3,896** from ESCO only and **245** from both (2.6% overlap). Each source alone would miss the other's requirements; most of the non-overlap is vocabulary (O*NET's 35 broad skills and named tools vs ESCO's fine-grained skills).

## 2. Agreement on skills both sources require

|  | ESCO peripheral | ESCO supporting (optional) | ESCO core (essential) |
| --- | --- | --- | --- |
| O*NET core | 0 | 37 | 17 |
| O*NET supporting | 0 | 177 | 9 |
| O*NET peripheral | 0 | 4 | 1 |

- Shared career-skill pairs: **245**
- Same tier: **79.2%**
- Cohen's kappa (O*NET tier vs ESCO tier): **0.307**
- knowledge: 20 pairs, same tier 80.0%, kappa 0.615
- skill: 8 pairs, same tier 37.5%, kappa 0.111
- technology: 217 pairs, same tier 80.6%, kappa 0.093

Kappa near 0 means the two taxonomies' judgements of *how* important a shared skill is are close to independent - a merged list would hide this.

## 3. Impact on what the learner is told (demo learner, transfer credit on)

| Career | Requirements (aggregated) | ...with O*NET evidence | Added by ESCO only (essential) | Readiness: O*NET only | Readiness: O*NET + ESCO |
| --- | --- | --- | --- | --- | --- |
| Actuaries | 80 | 45 | 35 | 0.279 | 0.141 |
| Automotive Engineers | 219 | 62 | 157 | 0.303 | 0.070 |
| Computer and Information Research Scientists | 140 | 86 | 54 | 0.140 | 0.080 |
| Computer Systems Analysts | 157 | 79 | 78 | 0.167 | 0.076 |
| Credit Analysts | 119 | 40 | 79 | 0.356 | 0.090 |
| Data Scientists | 183 | 59 | 124 | 0.195 | 0.057 |
| Database Administrators | 163 | 100 | 63 | 0.103 | 0.061 |
| Database Architects | 135 | 78 | 57 | 0.169 | 0.091 |
| Financial Quantitative Analysts | 107 | 49 | 58 | 0.283 | 0.109 |
| Industrial Engineers | 114 | 59 | 55 | 0.321 | 0.136 |
| Logistics Analysts | 97 | 54 | 43 | 0.259 | 0.126 |
| Management Analysts | 102 | 60 | 42 | 0.229 | 0.120 |
| Manufacturing Engineers | 137 | 63 | 74 | 0.299 | 0.114 |
| Market Research Analysts and Marketing Specialists | 180 | 46 | 134 | 0.283 | 0.057 |
| Mechanical Engineering Technologists and Technicians | 109 | 55 | 54 | 0.314 | 0.127 |
| Mechanical Engineers | 148 | 66 | 82 | 0.294 | 0.109 |
| Network and Computer Systems Administrators | 144 | 79 | 65 | 0.153 | 0.078 |
| Operations Research Analysts | 136 | 49 | 87 | 0.329 | 0.100 |
| Robotics Engineers | 130 | 66 | 64 | 0.246 | 0.109 |
| Software Developers | 222 | 108 | 114 | 0.091 | 0.042 |
| Software Quality Assurance Analysts and Testers | 143 | 85 | 58 | 0.140 | 0.080 |
| Statisticians | 133 | 50 | 83 | 0.279 | 0.087 |
| Web and Digital Interface Designers | 121 | 77 | 44 | 0.121 | 0.073 |
| Web Developers | 131 | 96 | 35 | 0.096 | 0.071 |

ESCO adds **51.9%** of the requirements shown to the learner. Readiness changes by **13.5 points** on average (max 26.6) when ESCO evidence is kept alongside O*NET.

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
| Data Scientists | Operations Analysis | scored | peripheral | optional | supporting |
| Data Scientists | R | present | core | optional | supporting |
| Database Administrators | Microsoft Access | present | core | optional | supporting |
| Database Administrators | MySQL | present | core | optional | supporting |
| Database Administrators | PostgreSQL | present | core | optional | supporting |
| Database Administrators | Python | present | core | optional | supporting |
| Database Administrators | Scala | present | core | optional | supporting |
| Database Architects | CloverETL | present | supporting | essential | core |
| Database Architects | Database management systems | present | supporting | essential | core |
| Database Architects | Python | present | core | optional | supporting |
| Logistics Analysts | Operations Analysis | scored | peripheral | optional | supporting |
| Manufacturing Engineers | Mathematics | scored | core | optional | supporting |
| Market Research Analysts and Marketing Specialists | Geography | scored | peripheral | optional | supporting |
| Mechanical Engineering Technologists and Technicians | Physics | scored | supporting | essential | core |
| Mechanical Engineering Technologists and Technicians | Troubleshooting | scored | supporting | essential | core |
| Mechanical Engineers | Troubleshooting | scored | supporting | essential | core |
| Network and Computer Systems Administrators | Python | present | core | optional | supporting |
| Software Developers | Ada | present | supporting | essential | core |
| Software Developers | C# | present | core | optional | supporting |
| Software Developers | C++ | present | core | optional | supporting |
