from fastapi.testclient import TestClient

from app.backend.core.app import create_app


def test_healthcheck_and_frontend(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_DB_PATH", str(tmp_path / "bookings.db"))
    with TestClient(create_app()) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}
        assert health.headers["x-content-type-options"] == "nosniff"

        page = client.get("/")
        assert page.status_code == 200
        assert "Mesa Viva" in page.text
        assert client.get("/css/main.css").status_code == 200


def test_booking_payloads_are_bounded(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_DB_PATH", str(tmp_path / "bookings.db"))
    with TestClient(create_app()) as client:
        response = client.post(
            "/booking/cancel",
            json={"booking_uuid": "not-an-id", "contact": "person@example.com"},
        )
    assert response.status_code == 422


def test_empty_optional_changes_are_accepted_by_the_api(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_DB_PATH", str(tmp_path / "bookings.db"))
    with TestClient(create_app()) as client:
        response = client.post(
            "/booking/modify",
            json={
                "booking_uuid": "ABC12345",
                "contact": "person@example.com",
                "new_date": "",
                "new_time": "",
                "new_party_size": "",
                "new_notes": "",
            },
        )
    assert response.status_code == 400


def test_unknown_booking_does_not_disclose_id_existence(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_DB_PATH", str(tmp_path / "bookings.db"))
    with TestClient(create_app()) as client:
        response = client.post(
            "/booking/cancel",
            json={"booking_uuid": "ABC12345", "contact": "person@example.com"},
        )
    assert response.status_code == 400
    assert "esos datos" in response.json()["detail"]


def test_import_does_not_create_database(tmp_path, monkeypatch):
    database = tmp_path / "import.db"
    monkeypatch.setenv("BOOKINGS_DB_PATH", str(database))
    __import__("app.backend.main")
    assert not database.exists()
