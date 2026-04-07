"""Auth endpoint tests."""
import pytest


class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "email": "newuser@example.com", "username": "newuser",
            "password": "Password123!", "role": "viewer"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        assert "viewer" in data["roles"]

    def test_register_duplicate_email(self, client):
        client.post("/auth/register", json={
            "email": "dup@example.com", "username": "dup1",
            "password": "Password123!", "role": "viewer"
        })
        resp = client.post("/auth/register", json={
            "email": "dup@example.com", "username": "dup2",
            "password": "Password123!", "role": "viewer"
        })
        assert resp.status_code == 400

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "email": "logintest@example.com", "username": "logintest",
            "password": "Password123!", "role": "viewer"
        })
        resp = client.post("/auth/login", json={
            "email": "logintest@example.com", "password": "Password123!"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/auth/register", json={
            "email": "badpwd@example.com", "username": "badpwd",
            "password": "Password123!", "role": "viewer"
        })
        resp = client.post("/auth/login", json={
            "email": "badpwd@example.com", "password": "wrongpass"
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, admin_headers):
        resp = client.get("/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test_admin@example.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 403  # HTTPBearer returns 403 when no creds

    def test_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_invalid_role(self, client):
        resp = client.post("/auth/register", json={
            "email": "badrole@example.com", "username": "badrole",
            "password": "Password123!", "role": "superuser"
        })
        assert resp.status_code == 422

    def test_audit_requires_admin(self, client, pm_headers):
        resp = client.get("/audit", headers=pm_headers)
        assert resp.status_code == 403

    def test_audit_accessible_by_admin(self, client, admin_headers):
        resp = client.get("/audit", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
