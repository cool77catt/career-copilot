def test_login_success(client):
    payload = {"email": "chris77carl@gmail.com", "password": "default"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_failure(client):
    payload = {"email": "chris77carl@gmail.com", "password": "wrong"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_me_with_token(client):
    login_payload = {"email": "chris77carl@gmail.com", "password": "default"}
    login_response = client.post("/auth/login", json=login_payload)
    token = login_response.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "chris77carl@gmail.com"
    assert body["name"] == "Chris Carl"


def test_get_me_requires_auth(client):
    response = client.get("/me")
    assert response.status_code == 401
