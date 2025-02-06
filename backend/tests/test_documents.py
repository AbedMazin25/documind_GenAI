import io
import pytest

def get_token(client, email="doctest@example.com"):
    client.post("/api/v1/auth/register", json={
        "email": email, "password": "secret123",
        "full_name": "Doc User", "org_name": "DocOrg"
    })
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": "secret123"})
    return resp.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_upload_and_list_documents(client):
    token = get_token(client, "upload@example.com")
    hdrs = auth_headers(token)
    file_content = b"Revenue: 100M\nNet Income: 20M"
    resp = client.post(
        "/api/v1/documents/",
        files={"file": ("report.txt", io.BytesIO(file_content), "text/plain")},
        headers=hdrs,
    )
    assert resp.status_code == 201
    doc_id = resp.json()["id"]
    list_resp = client.get("/api/v1/documents/", headers=hdrs)
    assert list_resp.status_code == 200
    ids = [d["id"] for d in list_resp.json()]
    assert doc_id in ids

def test_documents_org_isolation(client):
    token_a = get_token(client, "org_a@example.com")
    token_b = get_token(client, "org_b@example.com")
    file_content = b"Private content for org A"
    client.post(
        "/api/v1/documents/",
        files={"file": ("private.txt", io.BytesIO(file_content), "text/plain")},
        headers=auth_headers(token_a),
    )
    resp = client.get("/api/v1/documents/", headers=auth_headers(token_b))
    assert resp.status_code == 200
    # Org B should not see Org A's documents
    assert resp.json() == []
