# How to fill `data/curated/learning_resources.csv`

One row per course, book, tutorial or project. The build loads this file on every run
(`python scripts/build_database.py data/raw`), so the CSV is the source of truth.

| Column | What to write | Example |
| --- | --- | --- |
| title | The resource's real title | Python for Everybody |
| provider | Who publishes it | University of Michigan / Coursera |
| url | The real link (must be unique) | https://www.py4e.com |
| resource_type | course, book, tutorial, project, video, certification | course |
| effort_hours | Total hours **as stated by the provider** (round sensibly) | 40 |
| difficulty | beginner, intermediate, advanced | beginner |
| is_free | true / false | true |
| skills | Skill names separated by `;` - use the names shown in the dashboard's skill search | Python;Programming |

Rules
- Only real resources with the provider's own hour estimate; note the source of the hours if it is not on the page.
- Skill names are matched exactly (case-insensitive), preferring O*NET tools, then O*NET skills/knowledge, then ESCO.
  Unmatched names are listed in `reports/core_build.md` under *Build notes* - fix the spelling and rebuild.
- Rows whose title starts with `EXAMPLE` are ignored. Delete the example row when you add real ones.
- Aim for 150-300 resources across the 4 domains, with several alternatives per important skill
  (that is what makes the greedy vs optimal comparison meaningful).
- Split the work by domain; each person checks another person's rows (title, URL, hours, skills).

## About the shipped list
`data/curated/learning_resources.csv` ships with 45 real, publicly available courses, books and tutorials (Harvard CS50, Kaggle Learn, fast.ai, MIT OCW, Microsoft Learn and others). `effort_hours` are **approximate estimates** based on each provider's stated length (for example, weeks × suggested hours per week), rounded. Report them as estimates in the paper, and check the providers' pages before relying on exact figures.
