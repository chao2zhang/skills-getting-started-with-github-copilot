import copy
import pytest

from fastapi.testclient import TestClient
import src.app as appmodule


@pytest.fixture(autouse=True)
def reset_activities():
    # preserve activities between tests
    backup = copy.deepcopy(appmodule.activities)
    yield
    appmodule.activities.clear()
    appmodule.activities.update(backup)


def test_get_activities():
    client = TestClient(appmodule.app)

    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    client = TestClient(appmodule.app)
    activity = "Basketball"
    email = "tester@example.com"

    # signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # unregister
    res = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_nonexistent_returns_400():
    client = TestClient(appmodule.app)
    activity = "Tennis Club"
    email = "not-signed-up@example.com"

    res = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 400


def test_signup_duplicate_returns_400():
    client = TestClient(appmodule.app)
    activity = "Basketball"
    existing = appmodule.activities[activity]["participants"][0]

    res = client.post(f"/activities/{activity}/signup?email={existing}")
    assert res.status_code == 400
