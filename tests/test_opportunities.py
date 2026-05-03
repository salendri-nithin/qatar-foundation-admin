import pytest
from tests.conftest import (
    ADMIN_PAYLOAD, OPP_PAYLOAD, register_and_login, auth_headers
)

ADMIN_B = {
    "full_name": "Admin B",
    "email": "adminb@example.com",
    "password": "Password123",
    "confirm_password": "Password123",
}


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH GUARD
# ══════════════════════════════════════════════════════════════════════════════

class TestOpportunityAuthGuard:
    def test_get_all_requires_auth(self, client):
        resp = client.get("/api/opportunities")
        assert resp.status_code == 401

    def test_create_requires_auth(self, client):
        resp = client.post("/api/opportunities", json=OPP_PAYLOAD)
        assert resp.status_code == 401

    def test_get_one_requires_auth(self, client):
        resp = client.get("/api/opportunities/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, client):
        resp = client.put("/api/opportunities/1", json=OPP_PAYLOAD)
        assert resp.status_code == 401

    def test_delete_requires_auth(self, client):
        resp = client.delete("/api/opportunities/1")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
#  CREATE
# ══════════════════════════════════════════════════════════════════════════════

class TestCreateOpportunity:
    def test_create_success(self, client):
        token = register_and_login(client)
        resp = client.post("/api/opportunities", json=OPP_PAYLOAD, headers=auth_headers(token))
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["status"] == "success"
        assert body["data"]["name"] == OPP_PAYLOAD["name"]
        assert body["data"]["category"] == OPP_PAYLOAD["category"]
        assert "id" in body["data"]

    def test_create_missing_required_field(self, client):
        token = register_and_login(client)
        payload = {**OPP_PAYLOAD}
        del payload["name"]
        resp = client.post("/api/opportunities", json=payload, headers=auth_headers(token))
        assert resp.status_code == 422

    def test_create_invalid_category(self, client):
        token = register_and_login(client)
        resp = client.post("/api/opportunities",
                           json={**OPP_PAYLOAD, "category": "InvalidCat"},
                           headers=auth_headers(token))
        assert resp.status_code == 422

    def test_create_invalid_max_applicants(self, client):
        token = register_and_login(client)
        resp = client.post("/api/opportunities",
                           json={**OPP_PAYLOAD, "max_applicants": -5},
                           headers=auth_headers(token))
        assert resp.status_code == 422

    def test_create_without_optional_fields(self, client):
        token = register_and_login(client)
        payload = {k: v for k, v in OPP_PAYLOAD.items()
                   if k not in ("future_opportunities", "max_applicants")}
        resp = client.post("/api/opportunities", json=payload, headers=auth_headers(token))
        assert resp.status_code == 201

    def test_create_all_valid_categories(self, client):
        token = register_and_login(client)
        for cat in ["Technology", "Business", "Design", "Marketing", "Data Science", "Other"]:
            resp = client.post("/api/opportunities",
                               json={**OPP_PAYLOAD, "category": cat},
                               headers=auth_headers(token))
            assert resp.status_code == 201, f"Category '{cat}' should be valid"


# ══════════════════════════════════════════════════════════════════════════════
#  READ
# ══════════════════════════════════════════════════════════════════════════════

class TestGetOpportunities:
    def test_get_all_empty(self, client):
        token = register_and_login(client)
        resp = client.get("/api/opportunities", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_get_all_returns_only_own(self, client):
        token_a = register_and_login(client, ADMIN_PAYLOAD)
        token_b = register_and_login(client, ADMIN_B)

        # Admin A creates 2 opportunities
        client.post("/api/opportunities", json=OPP_PAYLOAD, headers=auth_headers(token_a))
        client.post("/api/opportunities", json={**OPP_PAYLOAD, "name": "Second Opp"},
                    headers=auth_headers(token_a))

        # Admin B creates 1 opportunity
        client.post("/api/opportunities", json={**OPP_PAYLOAD, "name": "B Opp"},
                    headers=auth_headers(token_b))

        resp_a = client.get("/api/opportunities", headers=auth_headers(token_a))
        resp_b = client.get("/api/opportunities", headers=auth_headers(token_b))

        assert len(resp_a.get_json()["data"]) == 2
        assert len(resp_b.get_json()["data"]) == 1

    def test_get_one_success(self, client):
        token = register_and_login(client)
        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token)).get_json()["data"]
        opp_id = created["id"]

        resp = client.get(f"/api/opportunities/{opp_id}", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["id"] == opp_id

    def test_get_one_not_found(self, client):
        token = register_and_login(client)
        resp = client.get("/api/opportunities/99999", headers=auth_headers(token))
        assert resp.status_code == 404

    def test_get_one_cross_admin_blocked(self, client):
        """Admin B must not be able to read Admin A's opportunity."""
        token_a = register_and_login(client, ADMIN_PAYLOAD)
        token_b = register_and_login(client, ADMIN_B)

        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token_a)).get_json()["data"]
        opp_id = created["id"]

        resp = client.get(f"/api/opportunities/{opp_id}", headers=auth_headers(token_b))
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
#  UPDATE
# ══════════════════════════════════════════════════════════════════════════════

class TestUpdateOpportunity:
    def test_update_success(self, client):
        token = register_and_login(client)
        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token)).get_json()["data"]
        opp_id = created["id"]

        updated_payload = {**OPP_PAYLOAD, "name": "Updated Name", "duration": "6 months"}
        resp = client.put(f"/api/opportunities/{opp_id}",
                          json=updated_payload, headers=auth_headers(token))
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["data"]["name"] == "Updated Name"
        assert body["data"]["duration"] == "6 months"

    def test_update_not_found(self, client):
        token = register_and_login(client)
        resp = client.put("/api/opportunities/99999", json=OPP_PAYLOAD,
                          headers=auth_headers(token))
        assert resp.status_code == 404

    def test_update_cross_admin_blocked(self, client):
        token_a = register_and_login(client, ADMIN_PAYLOAD)
        token_b = register_and_login(client, ADMIN_B)

        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token_a)).get_json()["data"]
        opp_id = created["id"]

        resp = client.put(f"/api/opportunities/{opp_id}",
                          json={**OPP_PAYLOAD, "name": "Hijacked"},
                          headers=auth_headers(token_b))
        assert resp.status_code == 404

        # Original should be unchanged
        original = client.get(f"/api/opportunities/{opp_id}",
                              headers=auth_headers(token_a)).get_json()["data"]
        assert original["name"] == OPP_PAYLOAD["name"]

    def test_update_validation_enforced(self, client):
        token = register_and_login(client)
        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token)).get_json()["data"]
        opp_id = created["id"]

        resp = client.put(f"/api/opportunities/{opp_id}",
                          json={**OPP_PAYLOAD, "category": "BadCategory"},
                          headers=auth_headers(token))
        assert resp.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
#  DELETE
# ══════════════════════════════════════════════════════════════════════════════

class TestDeleteOpportunity:
    def test_delete_success(self, client):
        token = register_and_login(client)
        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token)).get_json()["data"]
        opp_id = created["id"]

        resp = client.delete(f"/api/opportunities/{opp_id}", headers=auth_headers(token))
        assert resp.status_code == 200

        # Should be gone
        resp2 = client.get(f"/api/opportunities/{opp_id}", headers=auth_headers(token))
        assert resp2.status_code == 404

    def test_delete_not_found(self, client):
        token = register_and_login(client)
        resp = client.delete("/api/opportunities/99999", headers=auth_headers(token))
        assert resp.status_code == 404

    def test_delete_cross_admin_blocked(self, client):
        token_a = register_and_login(client, ADMIN_PAYLOAD)
        token_b = register_and_login(client, ADMIN_B)

        created = client.post("/api/opportunities", json=OPP_PAYLOAD,
                              headers=auth_headers(token_a)).get_json()["data"]
        opp_id = created["id"]

        # Admin B cannot delete Admin A's opportunity
        resp = client.delete(f"/api/opportunities/{opp_id}", headers=auth_headers(token_b))
        assert resp.status_code == 404

        # It still exists for Admin A
        resp2 = client.get(f"/api/opportunities/{opp_id}", headers=auth_headers(token_a))
        assert resp2.status_code == 200
