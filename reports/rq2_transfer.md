# RQ2 - Does directional transfer credit make readiness more realistic?

- Ground truth: O*NET Related Occupations; 182 held-out occupations as pseudo-learners (seed 42, 20% of 910); candidates: all 910 rated occupations
- Transfer edges re-fitted without the held-out occupations: 8,319 edges
- Readiness uses O*NET skills + knowledge only (no priors, no ESCO); learner proficiency = O*NET level
- Full profiles leave little for transfer to infer; partial profiles (a learner lists only their strongest skills) are the realistic case transfer credit is designed for.
- Runtime 310 s

## Summary (lambda = 0.8)

| Profile | MRR none | MRR directional | MRR symmetric | Directional - none [CI] | Directional - symmetric [CI] |
| --- | --- | --- | --- | --- | --- |
| full | 0.3161 | 0.3145 | 0.3068 | -0.0016 [-0.0052, +0.0018] | +0.0077 [+0.0036, +0.0124] * |
| top 10 | 0.2771 | 0.2199 | 0.2568 | -0.0572 [-0.0828, -0.0331] * | -0.0369 [-0.0591, -0.0158] * |

\* = 95% bootstrap CI excludes 0.

## Profile: full O*NET profile (all 68 skills + knowledge)

### Ranking of related occupations

| Method | MRR | nDCG@10 | Recall@10 | Recall@20 |
| --- | --- | --- | --- | --- |
| none (exact skills only) | 0.3161 | 0.1602 | 0.0824 | 0.1509 |
| directional, lambda=0.4 | 0.3154 | 0.1603 | 0.0827 | 0.1512 |
| directional, lambda=0.6 | 0.3149 | 0.1597 | 0.0824 | 0.1512 |
| directional, lambda=0.8 | 0.3145 | 0.1593 | 0.0821 | 0.1511 |
| directional, lambda=1.0 | 0.3125 | 0.1573 | 0.0810 | 0.1515 |
| symmetric, lambda=0.8 (H2b) | 0.3068 | 0.1592 | 0.0832 | 0.1523 |

Difference to *none* (95% bootstrap CI over learners; * = CI excludes 0):

| Method | Delta MRR [CI] | Delta nDCG@10 [CI] |
| --- | --- | --- |
| directional, lambda=0.4 | -0.0007 [-0.0016, +0.0002] | +0.0001 [-0.0011, +0.0014] |
| directional, lambda=0.6 | -0.0012 [-0.0029, +0.0005] | -0.0005 [-0.0023, +0.0013] |
| directional, lambda=0.8 | -0.0016 [-0.0052, +0.0018] | -0.0010 [-0.0030, +0.0010] |
| directional, lambda=1.0 | -0.0035 [-0.0092, +0.0024] | -0.0029 [-0.0064, +0.0002] |
| symmetric, lambda=0.8 (H2b) | -0.0093 [-0.0138, -0.0047] * | -0.0010 [-0.0041, +0.0024] |

Primary related occupations only:

| Method | MRR | nDCG@10 | Recall@10 | Recall@20 |
| --- | --- | --- | --- | --- |
| none (exact skills only) | 0.2204 | 0.0969 | 0.0982 | 0.1831 |
| directional, lambda=0.4 | 0.2199 | 0.0978 | 0.0998 | 0.1831 |
| directional, lambda=0.6 | 0.2202 | 0.0982 | 0.1004 | 0.1831 |
| directional, lambda=0.8 | 0.2204 | 0.0978 | 0.0998 | 0.1830 |
| directional, lambda=1.0 | 0.2187 | 0.0972 | 0.0993 | 0.1820 |
| symmetric, lambda=0.8 (H2b) | 0.2157 | 0.0972 | 0.0999 | 0.1836 |

### Credit targeting: do related occupations receive more of the transfer credit?

| Method | Lift related (pts) | Lift unrelated (pts) | Raw difference [CI] | Gap closed, related - unrelated (pts) [CI] |
| --- | --- | --- | --- | --- |
| directional, lambda=0.4 | 0.04 | 0.15 | -0.11 [-0.12, -0.10] * | -0.17 [-0.19, -0.15] * |
| directional, lambda=0.6 | 0.07 | 0.24 | -0.17 [-0.19, -0.15] * | -0.26 [-0.29, -0.23] * |
| directional, lambda=0.8 | 0.12 | 0.35 | -0.23 [-0.26, -0.20] * | -0.35 [-0.40, -0.31] * |
| directional, lambda=1.0 | 0.29 | 0.59 | -0.30 [-0.34, -0.27] * | -0.44 [-0.50, -0.39] * |
| symmetric, lambda=0.8 (H2b) | 0.24 | 0.72 | -0.48 [-0.52, -0.44] * | -0.73 [-0.79, -0.66] * |

## Profile: partial profile: learner's 10 strongest skills only

### Ranking of related occupations

| Method | MRR | nDCG@10 | Recall@10 | Recall@20 |
| --- | --- | --- | --- | --- |
| none (exact skills only) | 0.2771 | 0.1457 | 0.0754 | 0.1614 |
| directional, lambda=0.4 | 0.2470 | 0.1215 | 0.0628 | 0.1374 |
| directional, lambda=0.6 | 0.2391 | 0.1098 | 0.0561 | 0.1272 |
| directional, lambda=0.8 | 0.2199 | 0.1011 | 0.0530 | 0.1152 |
| directional, lambda=1.0 | 0.1995 | 0.0875 | 0.0462 | 0.1032 |
| symmetric, lambda=0.8 (H2b) | 0.2568 | 0.1273 | 0.0665 | 0.1329 |

Difference to *none* (95% bootstrap CI over learners; * = CI excludes 0):

| Method | Delta MRR [CI] | Delta nDCG@10 [CI] |
| --- | --- | --- |
| directional, lambda=0.4 | -0.0301 [-0.0487, -0.0129] * | -0.0242 [-0.0320, -0.0174] * |
| directional, lambda=0.6 | -0.0380 [-0.0600, -0.0183] * | -0.0358 [-0.0461, -0.0269] * |
| directional, lambda=0.8 | -0.0572 [-0.0828, -0.0331] * | -0.0446 [-0.0570, -0.0341] * |
| directional, lambda=1.0 | -0.0776 [-0.1084, -0.0480] * | -0.0581 [-0.0735, -0.0447] * |
| symmetric, lambda=0.8 (H2b) | -0.0203 [-0.0465, +0.0054] | -0.0183 [-0.0303, -0.0063] * |

Primary related occupations only:

| Method | MRR | nDCG@10 | Recall@10 | Recall@20 |
| --- | --- | --- | --- | --- |
| none (exact skills only) | 0.1878 | 0.0870 | 0.0927 | 0.1928 |
| directional, lambda=0.4 | 0.1641 | 0.0703 | 0.0742 | 0.1626 |
| directional, lambda=0.6 | 0.1543 | 0.0618 | 0.0643 | 0.1494 |
| directional, lambda=0.8 | 0.1361 | 0.0558 | 0.0608 | 0.1376 |
| directional, lambda=1.0 | 0.1235 | 0.0472 | 0.0515 | 0.1201 |
| symmetric, lambda=0.8 (H2b) | 0.1764 | 0.0746 | 0.0777 | 0.1572 |

### Credit targeting: do related occupations receive more of the transfer credit?

| Method | Lift related (pts) | Lift unrelated (pts) | Raw difference [CI] | Gap closed, related - unrelated (pts) [CI] |
| --- | --- | --- | --- | --- |
| directional, lambda=0.4 | 4.65 | 4.60 | +0.05 [+0.00, +0.10] * | +0.32 [+0.25, +0.39] * |
| directional, lambda=0.6 | 6.97 | 6.89 | +0.08 [+0.00, +0.15] * | +0.48 [+0.38, +0.58] * |
| directional, lambda=0.8 | 9.29 | 9.19 | +0.10 [+0.00, +0.19] * | +0.64 [+0.51, +0.77] * |
| directional, lambda=1.0 | 11.63 | 11.51 | +0.13 [+0.01, +0.25] * | +0.80 [+0.64, +0.97] * |
| symmetric, lambda=0.8 (H2b) | 14.39 | 14.51 | -0.12 [-0.28, +0.04] | +0.68 [+0.48, +0.89] * |
