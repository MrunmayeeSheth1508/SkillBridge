# RQ4 - Greedy resource selection vs the exact optimum (weighted set cover)

- Solver for the optimum: HiGHS (integer linear program)
- Greedy rule = core.fn_assign_resources: lowest hours per newly covered skill

## A. Curated instances (data/curated/learning_resources.csv)

48 learner x career instances, 45 curated resources.

| Learner | Career | Skills to cover | Candidate resources | Greedy picks | Greedy hours | Optimal picks | Optimal hours | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Demo Learner | Actuaries | 13 | 25 | 11 | 209.0 | 11 | 209.0 | 1.000 |
| Demo Learner | Automotive Engineers | 13 | 22 | 10 | 168.0 | 10 | 168.0 | 1.000 |
| Demo Learner | Computer and Information Research Scientists | 18 | 37 | 16 | 295.0 | 15 | 292.0 | 1.010 |
| Demo Learner | Computer Systems Analysts | 16 | 34 | 14 | 312.0 | 13 | 309.0 | 1.010 |
| Demo Learner | Credit Analysts | 9 | 13 | 6 | 122.0 | 6 | 122.0 | 1.000 |
| Demo Learner | Data Scientists | 22 | 42 | 20 | 330.0 | 19 | 327.0 | 1.009 |
| Demo Learner | Database Administrators | 12 | 27 | 12 | 186.0 | 11 | 183.0 | 1.016 |
| Demo Learner | Database Architects | 13 | 26 | 12 | 193.0 | 12 | 193.0 | 1.000 |
| Demo Learner | Financial Quantitative Analysts | 15 | 27 | 13 | 281.0 | 13 | 281.0 | 1.000 |
| Demo Learner | Industrial Engineers | 11 | 18 | 9 | 165.0 | 9 | 165.0 | 1.000 |
| Demo Learner | Logistics Analysts | 12 | 19 | 10 | 185.0 | 10 | 185.0 | 1.000 |
| Demo Learner | Management Analysts | 12 | 24 | 10 | 169.0 | 10 | 169.0 | 1.000 |
| Demo Learner | Manufacturing Engineers | 11 | 15 | 8 | 162.0 | 8 | 162.0 | 1.000 |
| Demo Learner | Market Research Analysts and Marketing Specialists | 7 | 13 | 6 | 122.0 | 6 | 122.0 | 1.000 |
| Demo Learner | Mechanical Engineering Technologists and Technicians | 8 | 14 | 7 | 142.0 | 7 | 142.0 | 1.000 |
| Demo Learner | Mechanical Engineers | 12 | 21 | 9 | 166.0 | 9 | 166.0 | 1.000 |
| Demo Learner | Network and Computer Systems Administrators | 11 | 31 | 11 | 222.0 | 10 | 219.0 | 1.014 |
| Demo Learner | Operations Research Analysts | 12 | 25 | 11 | 189.0 | 11 | 189.0 | 1.000 |
| Demo Learner | Robotics Engineers | 13 | 23 | 11 | 241.0 | 10 | 238.0 | 1.013 |
| Demo Learner | Software Developers | 15 | 30 | 13 | 307.0 | 12 | 304.0 | 1.010 |
| Demo Learner | Software Quality Assurance Analysts and Testers | 12 | 32 | 12 | 262.0 | 11 | 259.0 | 1.012 |
| Demo Learner | Statisticians | 10 | 24 | 10 | 179.0 | 10 | 179.0 | 1.000 |
| Demo Learner | Web and Digital Interface Designers | 14 | 27 | 11 | 314.0 | 10 | 311.0 | 1.010 |
| Demo Learner | Web Developers | 15 | 30 | 13 | 327.0 | 12 | 324.0 | 1.009 |
| Second Learner | Actuaries | 13 | 25 | 11 | 209.0 | 11 | 209.0 | 1.000 |
| Second Learner | Automotive Engineers | 13 | 22 | 10 | 168.0 | 10 | 168.0 | 1.000 |
| Second Learner | Computer and Information Research Scientists | 18 | 37 | 16 | 295.0 | 15 | 292.0 | 1.010 |
| Second Learner | Computer Systems Analysts | 16 | 34 | 14 | 312.0 | 13 | 309.0 | 1.010 |
| Second Learner | Credit Analysts | 9 | 13 | 6 | 122.0 | 6 | 122.0 | 1.000 |
| Second Learner | Data Scientists | 22 | 42 | 20 | 330.0 | 19 | 327.0 | 1.009 |
| Second Learner | Database Administrators | 12 | 27 | 12 | 186.0 | 11 | 183.0 | 1.016 |
| Second Learner | Database Architects | 13 | 26 | 12 | 193.0 | 12 | 193.0 | 1.000 |
| Second Learner | Financial Quantitative Analysts | 15 | 27 | 13 | 281.0 | 13 | 281.0 | 1.000 |
| Second Learner | Industrial Engineers | 11 | 18 | 9 | 165.0 | 9 | 165.0 | 1.000 |
| Second Learner | Logistics Analysts | 12 | 19 | 10 | 185.0 | 10 | 185.0 | 1.000 |
| Second Learner | Management Analysts | 13 | 25 | 11 | 189.0 | 11 | 189.0 | 1.000 |
| Second Learner | Manufacturing Engineers | 11 | 15 | 8 | 162.0 | 8 | 162.0 | 1.000 |
| Second Learner | Market Research Analysts and Marketing Specialists | 7 | 13 | 6 | 122.0 | 6 | 122.0 | 1.000 |
| Second Learner | Mechanical Engineering Technologists and Technicians | 8 | 14 | 7 | 142.0 | 7 | 142.0 | 1.000 |
| Second Learner | Mechanical Engineers | 12 | 21 | 9 | 166.0 | 9 | 166.0 | 1.000 |
| Second Learner | Network and Computer Systems Administrators | 11 | 31 | 11 | 222.0 | 10 | 219.0 | 1.014 |
| Second Learner | Operations Research Analysts | 12 | 25 | 11 | 189.0 | 11 | 189.0 | 1.000 |
| Second Learner | Robotics Engineers | 13 | 23 | 11 | 241.0 | 10 | 238.0 | 1.013 |
| Second Learner | Software Developers | 15 | 30 | 13 | 307.0 | 12 | 304.0 | 1.010 |
| Second Learner | Software Quality Assurance Analysts and Testers | 12 | 32 | 12 | 262.0 | 11 | 259.0 | 1.012 |
| Second Learner | Statisticians | 11 | 25 | 11 | 199.0 | 11 | 199.0 | 1.000 |
| Second Learner | Web and Digital Interface Designers | 15 | 28 | 12 | 334.0 | 11 | 331.0 | 1.009 |
| Second Learner | Web Developers | 15 | 30 | 13 | 327.0 | 12 | 324.0 | 1.009 |

- Mean greedy/optimal hours ratio: **1.005**, worst: **1.016**; greedy optimal in 28/48 instances
- SQL implementation matches the reference greedy on 48/48 roadmaps

## B. Synthetic set-cover instances

Random instances: n skills, 3n resources, each covering 1-5 skills, hours ~ lognormal and growing with the number of skills covered; every skill is coverable. 30 instances per size, seed 7.

| Skills (n) | Resources | Mean ratio | Worst ratio | Greedy optimal | Bound H(5) | Greedy ms | ILP ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 30 | 1.100 | 1.422 | 7/30 | 2.28 | 0.03 | 9.0 |
| 20 | 60 | 1.105 | 1.448 | 2/30 | 2.28 | 0.09 | 10.5 |
| 40 | 120 | 1.118 | 1.208 | 0/30 | 2.28 | 0.30 | 13.5 |
| 80 | 240 | 1.118 | 1.200 | 0/30 | 2.28 | 1.16 | 112.7 |
| 160 | 480 | 1.119 | 1.186 | 0/30 | 2.28 | 4.81 | 1310.3 |

## Reading the result

- The ratio is greedy hours / optimal hours (1.000 = optimal). The theoretical worst case is H(5) = 2.28 when a resource covers at most 5 skills; observed ratios are far below it.
- Greedy runs in milliseconds inside the database for every roadmap request; the exact ILP needs an external solver and grows quickly with instance size, which is why the greedy rule is used online.

Runtime 58 s