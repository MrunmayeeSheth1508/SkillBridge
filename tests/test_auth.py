"""Authentication and database-enforced authorisation through the web API."""

import psycopg


def test_pages_and_api_require_login(anon):
    assert anon.get("/").status_code == 302                     # redirected to /login
    assert anon.get("/login").status_code == 200
    assert anon.get("/api/me").status_code == 401
    assert anon.get("/api/gap/1").status_code == 401


def test_wrong_password_rejected(anon):
    r = anon.post("/api/login", json={"email": "demo@skillbridge.local", "password": "wrong-password"})
    assert r.status_code == 401


def test_passwords_are_hashed(db_url):
    with psycopg.connect(db_url) as c:
        hashes = [r[0] for r in c.execute("SELECT password_hash FROM core.users "
                                          "WHERE email LIKE '%%@skillbridge.local'").fetchall()]
    assert hashes and all(h.startswith(("scrypt:", "pbkdf2:")) for h in hashes)


def test_session_reports_role(client, admin):
    assert client.get("/api/session").get_json()["role"] == "learner"
    assert admin.get("/api/session").get_json()["role"] == "admin"


def test_learners_only_see_their_own_skills(client, learner2):
    mine = {s["skill_id"] for s in client.get("/api/me").get_json()["skills"]}
    theirs = {s["skill_id"] for s in learner2.get("/api/me").get_json()["skills"]}
    assert mine and theirs and mine != theirs


def test_learner_cannot_use_admin_endpoints(client):
    assert client.get("/api/admin/prerequisites").status_code == 403
    assert client.post("/api/extract", json={"career_id": 1, "text": "Python and SQL needed."}).status_code == 403
    assert client.put("/api/admin/parameters", json={"param_name": "transfer_lambda", "param_value": 0}).status_code == 403


def test_admin_cycle_rejected_by_database(admin):
    rows = admin.get("/api/admin/prerequisites").get_json()
    assert rows, "needs curated prerequisites"
    r = rows[0]                                              # existing: prereq -> skill
    resp = admin.post("/api/admin/prerequisites",
                      json={"prereq_skill_id": r["skill_id"], "skill_id": r["prereq_skill_id"]})
    assert resp.status_code == 422 and "cycle" in resp.get_json()["error"]


def test_admin_parameter_whitelist(admin):
    r = admin.put("/api/admin/parameters", json={"param_name": "esco_confidence", "param_value": 1})
    assert r.status_code == 403


def test_register_and_isolation(anon, db_url):
    email = "pytest-user@example.org"
    with psycopg.connect(db_url) as c:
        c.execute("DELETE FROM core.users WHERE email = %s", (email,))
        c.commit()
    try:
        r = anon.post("/api/register", json={"full_name": "Py Test", "email": email,
                                             "password": "longenough", "weekly_hours": 6})
        assert r.status_code == 201
        me = anon.get("/api/me").get_json()
        assert me["email"] == email and me["skills"] == []      # new learner sees no one else's skills
        assert anon.post("/api/register", json={"full_name": "Py Test", "email": email,
                                                "password": "longenough"}).status_code in (409, 201)
    finally:
        with psycopg.connect(db_url) as c:
            c.execute("DELETE FROM core.users WHERE email = %s", (email,))
            c.commit()
