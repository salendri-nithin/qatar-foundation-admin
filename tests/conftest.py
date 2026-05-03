import pytest
from app import create_app
from extensions import db as _db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"
    SECRET_KEY = "test-secret"


@pytest.fixture(scope="session")
def app():
    flask_app = create_app(TestConfig)
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        yield
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


ADMIN_PAYLOAD = {
    "full_name": "Test Admin",
    "email": "test@example.com",
    "password": "Password123",
    "confirm_password": "Password123",
}

OPP_PAYLOAD = {
    "name": "Test Opportunity",
    "duration": "2 months",
    "start_date": "2025-09-01",
    "description": "A test opportunity description.",
    "skills": "Python, Flask",
    "category": "Technology",
    "future_opportunities": "Possible full-time.",
    "max_applicants": 10,
}


def register_and_login(client, payload=None):
    payload = payload or ADMIN_PAYLOAD
    client.post("/api/auth/signup", json=payload)
    resp = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    token = resp.get_json()["data"]["access_token"]
    return token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}