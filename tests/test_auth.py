import pytest
from tests.conftest import ADMIN_PAYLOAD, register_and_login, auth_headers


# ══════════════════════════════════════════════════════════════════════════════
#  SIGNUP
# ══════════════════════════════════════════════════════════════════════════════

class TestSignup:
    def test_signup_success(self, client):
        resp = client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "success"
        assert body["data"]["email"] == ADMIN_PAYLOAD["email"]

    def test_signup_missing_field(self, client):
        payload = {**ADMIN_PAYLOAD}
        del payload["full_name"]
        resp = client.post("/api/auth/signup", json=payload)
        assert resp.status_code == 422

    def test_signup_invalid_email(self, client):
        resp = client.post("/api/auth/signup", json={**ADMIN_PAYLOAD, "email": "not-an-email"})
        assert resp.status_code == 422

    def test_signup_short_password(self, client):
        resp = client.post("/api/auth/signup", json={
            **ADMIN_PAYLOAD, "password": "short", "confirm_password": "short"
        })
        assert resp.status_code == 422

    def test_signup_password_mismatch(self, client):
        resp = client.post("/api/auth/signup", json={
            **ADMIN_PAYLOAD, "confirm_password": "WrongPass999"
        })
        assert resp.status_code == 422

    def test_signup_duplicate_email(self, client):
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        resp = client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        assert resp.status_code == 409

    def test_password_not_stored_in_plain_text(self, client):
        from models import Admin
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        admin = Admin.query.filter_by(email=ADMIN_PAYLOAD["email"]).first()
        assert admin is not None
        assert admin.password_hash != ADMIN_PAYLOAD["password"]
        assert admin.password_hash.startswith("$2b$") or admin.password_hash.startswith("$2a$")


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class TestLogin:
    def test_login_success(self, client):
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        resp = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"],
            "password": ADMIN_PAYLOAD["password"],
        })
        assert resp.status_code == 200
        body = resp.get_json()
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "Bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        resp = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"],
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401
        assert resp.get_json()["message"] == "Invalid email or password."

    def test_login_nonexistent_email(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "Password123",
        })
        assert resp.status_code == 401
        # Generic message — must not reveal which field is wrong
        assert resp.get_json()["message"] == "Invalid email or password."

    def test_login_missing_fields(self, client):
        resp = client.post("/api/auth/login", json={"email": ADMIN_PAYLOAD["email"]})
        assert resp.status_code == 422

    def test_login_remember_me_longer_expiry(self, client):
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)

        normal = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"],
            "remember_me": False,
        }).get_json()["data"]["expires_in"]

        remembered = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"],
            "remember_me": True,
        }).get_json()["data"]["expires_in"]

        assert remembered > normal


# ══════════════════════════════════════════════════════════════════════════════
#  FORGOT / RESET PASSWORD
# ══════════════════════════════════════════════════════════════════════════════

class TestPasswordReset:
    def test_forgot_password_always_returns_success(self, client):
        # Unknown email — still 200
        resp = client.post("/api/auth/forgot-password", json={"email": "ghost@example.com"})
        assert resp.status_code == 200

    def test_forgot_password_known_email_creates_token(self, client):
        from models import PasswordResetToken
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        client.post("/api/auth/forgot-password", json={"email": ADMIN_PAYLOAD["email"]})
        token = PasswordResetToken.query.first()
        assert token is not None
        assert token.is_valid

    def test_reset_password_success(self, client):
        from models import PasswordResetToken
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        client.post("/api/auth/forgot-password", json={"email": ADMIN_PAYLOAD["email"]})
        token = PasswordResetToken.query.first().token

        resp = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "NewPassword@456",
            "confirm_password": "NewPassword@456",
        })
        assert resp.status_code == 200

        # Old password should no longer work
        login_resp = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"], "password": ADMIN_PAYLOAD["password"],
        })
        assert login_resp.status_code == 401

        # New password should work
        login_resp2 = client.post("/api/auth/login", json={
            "email": ADMIN_PAYLOAD["email"], "password": "NewPassword@456",
        })
        assert login_resp2.status_code == 200

    def test_reset_password_invalid_token(self, client):
        resp = client.post("/api/auth/reset-password", json={
            "token": "totally-fake-token",
            "new_password": "NewPassword@456",
            "confirm_password": "NewPassword@456",
        })
        assert resp.status_code == 400

    def test_reset_password_token_single_use(self, client):
        from models import PasswordResetToken
        client.post("/api/auth/signup", json=ADMIN_PAYLOAD)
        client.post("/api/auth/forgot-password", json={"email": ADMIN_PAYLOAD["email"]})
        token = PasswordResetToken.query.first().token

        client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "NewPass@111", "confirm_password": "NewPass@111",
        })
        # Reuse the same token
        resp = client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "AnotherPass@222", "confirm_password": "AnotherPass@222",
        })
        assert resp.status_code == 400

    def test_reset_password_short_password(self, client):
        resp = client.post("/api/auth/reset-password", json={
            "token": "sometoken", "new_password": "short", "confirm_password": "short",
        })
        assert resp.status_code == 422

    def test_reset_password_mismatch(self, client):
        resp = client.post("/api/auth/reset-password", json={
            "token": "sometoken", "new_password": "ValidPass@1", "confirm_password": "DiffPass@2",
        })
        assert resp.status_code == 422
