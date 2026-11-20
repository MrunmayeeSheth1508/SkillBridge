"""REST API tests through Flask's test client (read-only endpoints + input validation)."""


def first_target(client) -> int:
    careers = client.get("/api/careers").get_json()
    assert careers, "no target careers"
    pref = [c for c in careers if c["title"] == "Data Scientists"]
    return (pref or careers)[0]["career_id"]


def test_dashboard_page_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"SkillBridge" in r.data


def test_overview(client):
    d = client.get("/api/overview").get_json()
    assert d["skills"] > 0 and d["evidence"] > 0


def test_careers_grouped_by_domain(client):
    careers = client.get("/api/careers").get_json()
    assert {c["domain"] for c in careers} <= {
        "Data & AI", "Software engineering",
        "Mechanical & manufacturing engineering", "Business & finance analytics"}


def test_skill_search(client):
    rows = client.get("/api/skills/search?q=math").get_json()
    assert any("Math" in r["name"] for r in rows)


def test_gap_analysis_endpoint(client):
    d = client.get(f"/api/gap/{first_target(client)}").get_json()
    assert 0 <= d["readiness"]["baseline"] <= d["readiness"]["transfer"] <= 1
    assert all("gap_baseline" in g and g["gap"] <= g["gap_baseline"] + 1e-9 for g in d["gaps"])


def test_explain_endpoint(client):
    cid = first_target(client)
    gap = client.get(f"/api/gap/{cid}").get_json()["gaps"][0]
    d = client.get(f"/api/explain/{cid}/{gap['skill_id']}").get_json()
    assert d["evidence"], "every gap must be backed by at least one evidence record"


def test_rank_endpoint(client):
    rows = client.get("/api/rank").get_json()
    values = [r["transfer"] for r in rows if r["transfer"] is not None]
    assert values == sorted(values, reverse=True)


def test_unknown_career_is_404(client):
    assert client.get("/api/gap/999999999").status_code == 404


def test_roadmap_rejects_bad_budget(client):
    r = client.post(f"/api/roadmap/{first_target(client)}", json={"weekly_hours": 500})
    assert r.status_code == 400


def test_extract_rejects_empty_text(client):
    r = client.post("/api/extract", json={"career_id": first_target(client), "text": "hi"})
    assert r.status_code == 400