from app.features.auth.utils.jwt import decode_access_token


def create_test_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_login_success(client):
    registered_user = create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "user" in data
    assert "token" in data

    assert (
        data["user"]["id"]
        == registered_user["user"]["id"]
    )

    assert data["user"]["fullName"] == "Balpreet Singh"

    assert (
        data["user"]["email"]
        == "balpreet@example.com"
    )

    assert data["token"]

    assert "password" not in data["user"]


def test_login_token_is_valid(client):
    registered_user = create_test_user(client)

    user_id = registered_user["user"]["id"]

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["token"]

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)


def test_login_wrong_password(client):
    create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"


def test_login_nonexistent_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"


def test_login_invalid_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_missing_password(client):
    create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
        },
    )

    assert response.status_code == 422


def test_login_missing_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_empty_request_body(client):
    response = client.post(
        "/api/v1/auth/login",
        json={},
    )

    assert response.status_code == 422


def test_login_malformed_json(client):
    response = client.post(
        "/api/v1/auth/login",
        content='{"email": "test@example.com", "password": }',
        headers={
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 422


def test_login_empty_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422


def test_login_response_contains_expected_user_fields(client):
    create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    user = response.json()["user"]

    assert "id" in user
    assert "fullName" in user
    assert "email" in user
    assert "profileImageUrl" in user
    assert "createdAt" in user
    assert "updatedAt" in user

    assert "password" not in user


def test_login_response_uses_camel_case_fields(client):
    create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    user = response.json()["user"]

    assert "fullName" in user
    assert "profileImageUrl" in user
    assert "createdAt" in user
    assert "updatedAt" in user

    assert "full_name" not in user
    assert "profile_image_url" not in user
    assert "created_at" not in user
    assert "updated_at" not in user