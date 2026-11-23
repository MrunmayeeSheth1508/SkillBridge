"""Shared pytest fixtures for SkillBridge.

Every test runs inside a transaction that is rolled back, so the test suite
never changes the database. Run the build first:
    python scripts/build_database.py data/raw
    python -m pytest
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))

import load_staging as ls  # noqa: E402  (also fixes the Windows libpq PATH)

import psycopg  # noqa: E402


@pytest.fixture(scope="session")
def db_url() -> str:
    return ls.get_database_url()


@pytest.fixture()
def cur(db_url):
    """A cursor inside a transaction that is always rolled back."""
    conn = psycopg.connect(db_url)
    try:
        c = conn.cursor()
        c.execute("SET search_path = core, staging, public")
        yield c
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture()
def demo_user(cur) -> int:
    cur.execute("SELECT user_id FROM core.users WHERE email = 'demo@skillbridge.local'")
    row = cur.fetchone()
    assert row, "demo learner missing - run scripts/build_database.py first"
    return row[0]


@pytest.fixture()
def target_career(cur) -> int:
    cur.execute("""SELECT career_id FROM core.careers
                   WHERE is_target ORDER BY (title = 'Data Scientists') DESC, career_id LIMIT 1""")
    return cur.fetchone()[0]


@pytest.fixture()
def three_skills(cur) -> tuple[int, int, int]:
    cur.execute("SELECT skill_id FROM core.skills WHERE taxonomy = 'onet_skill' ORDER BY skill_id LIMIT 3")
    a, b, c = (r[0] for r in cur.fetchall())
    cur.execute("DELETE FROM core.skill_prerequisites WHERE skill_id IN (%s,%s,%s) OR prereq_skill_id IN (%s,%s,%s)",
                (a, b, c, a, b, c))
    return a, b, c


def _client(email=None, password=None):
    import app as dashboard
    dashboard.app.testing = True
    c = dashboard.app.test_client()
    if email:
        r = c.post("/api/login", json={"email": email, "password": password})
        assert r.status_code == 200, f"login failed for {email}: {r.get_json()}"
    return c


@pytest.fixture(scope="session")
def client():
    """Logged in as the demo learner (talks to the real database)."""
    return _client("demo@skillbridge.local", "demo1234")


@pytest.fixture(scope="session")
def learner2():
    return _client("learner2@skillbridge.local", "learner1234")


@pytest.fixture(scope="session")
def admin():
    return _client("admin@skillbridge.local", "admin1234")


@pytest.fixture()
def anon():
    return _client()
