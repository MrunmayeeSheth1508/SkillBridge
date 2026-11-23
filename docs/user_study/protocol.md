# SkillBridge user study: protocol

**Goal:** check that learners can use SkillBridge to find their gaps and plan their learning, and measure usability with the System Usability Scale (SUS).

**Participants:** 8–15 students (5 already finds most usability problems; 10+ gives a usable SUS average).
**Duration:** about 20 minutes per person. **Setting:** a laptop running the dashboard (`python app/app.py`), with one observer and a stopwatch.

## Before the session
1. Rebuild the database so everyone starts from the same state: `python scripts/build_database.py data/raw`
2. Create one account per participant on the sign-in page (Register) and use the codes P01, P02, … as names. Never record real names in the results file.
3. Print `consent_form.md` and `sus_questionnaire.md`, and open `results_template.csv` (save a copy as `results.csv`).

## Procedure
1. Consent (2 min): the participant reads and signs the consent form.
2. Briefing (1 min): read this aloud: *"SkillBridge compares the skills you have with what a career needs and plans what to learn next. We are testing the system, not you. Please think aloud."*
3. Tasks (about 12 min): give the tasks one at a time and start the stopwatch when the participant starts reading. A task counts as **success** if it is completed without help, **partial** after one hint, and **fail** if the participant gives up or exceeds the time limit. Write down the time, the outcome and any notable comments.
4. SUS questionnaire (3 min).
5. Two open questions (2 min): "What was most useful?" and "What was confusing or missing?"

## Tasks
| # | Task (read to the participant) | Success criterion | Limit |
| --- | --- | --- | --- |
| T1 | "Add three skills you have and rate how well you know each." | 3 skills saved in *My profile* | 3 min |
| T2 | "Pick a career you are interested in and find out how ready you are for it." | Target career selected; readiness visible | 2 min |
| T3 | "Which skill is your biggest gap for that career, and why does the system think it matters?" | Names the top gap and points to its evidence (sources/tier) | 3 min |
| T4 | "Find a skill where something you already know gives you a head start." | Points to a gap row showing "↳ +… transfer credit from …" | 3 min |
| T5 | "Make an 8-week learning plan. What do you learn first, and which course is suggested?" | Roadmap built; names week-1 skill and a course (if courses are loaded) | 3 min |
| T6 | "Compare your readiness for two careers." | Uses "Compare careers" and states which career is closer | 2 min |

## Afterwards
Copy each participant's row into `results.csv`, then run:
```
python scripts/analyze_user_study.py docs/user_study/results.csv
```
This writes `reports/user_study.md` with the SUS score (mean ± SD, 95% CI, adjective grade), success rate and median time per task, and the comments.

**Reporting in the paper:** give N, how participants were recruited, the SUS mean with its CI, and the task success table. Also state the main limitation: a small convenience sample of students.
