import pytest

def register(client, email="test@example.com", password="secret123", org="TestOrg"):
    return client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User",
        "org_name": org,
    })

def test_register_returns_user(client):
    resp = register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_email(client):
    register(client, email="dup@example.com")
    resp = register(client, email="dup@example.com")
    assert resp.status_code == 409

def test_login_valid(client):
    register(client, email="login@example.com")
    resp = client.post("/api/v1/auth/login", data={
        "username": "login@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_invalid_password(client):
    register(client, email="bad@example.com")
    resp = client.post("/api/v1/auth/login", data={
        "username": "bad@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401

def test_protected_route_without_token(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401
