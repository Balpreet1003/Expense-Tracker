from datetime import datetime, timedelta, timezone

import jwt

from app.features.auth.utils.jwt import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


REGISTER_URL = "/api/v1/auth/register"
PROFILE_URL = "/api/v1/auth/profile"


def create_test_user_and_get_token(client):
    """
    Helper function to register a user
    and return the authentication token.
    """

    response = client.post(
        REGISTER_URL,
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    return data["token"], data["user"]


def test_get_profile_success(client):
    token, registered_user = create_test_user_and_get_token(
        client
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == registered_user["id"]
    assert data["fullName"] == "Balpreet Singh"
    assert data["email"] == "balpreet@example.com"

    assert "profileImageUrl" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_get_profile_without_token(client):
    response = client.get(
        PROFILE_URL,
    )

    # HTTPBearer() with default configuration
    # returns 403 when Authorization header is missing.
    assert response.status_code == 401


def test_get_profile_invalid_token(client):
    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )


def test_get_profile_with_expired_token(client):
    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc)
        - timedelta(minutes=1),
    }

    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )


def test_get_profile_with_tampered_token(client):
    token, _ = create_test_user_and_get_token(
        client
    )

    # JWT structure:
    # header.payload.signature
    parts = token.split(".")

    # Modify the signature safely.
    original_signature = parts[2]

    if original_signature[0] == "a":
        modified_signature = (
            "b" + original_signature[1:]
        )
    else:
        modified_signature = (
            "a" + original_signature[1:]
        )

    tampered_token = (
        f"{parts[0]}."
        f"{parts[1]}."
        f"{modified_signature}"
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {tampered_token}",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )


def test_get_profile_token_without_subject(client):
    token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )


def test_get_profile_with_invalid_subject(client):
    token = jwt.encode(
        {
            "sub": "abc",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )


def test_get_profile_user_not_found(client):
    token = create_access_token(
        user_id=999999,
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == "User not found"


def test_get_profile_with_wrong_auth_scheme(client):
    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": "Basic abc123",
        },
    )

    # Default HTTPBearer() behavior.
    assert response.status_code == 401


def test_get_profile_with_empty_bearer_token(client):
    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": "Bearer",
        },
    )

    # Default HTTPBearer() behavior.
    assert response.status_code == 401


def test_profile_does_not_return_password(client):
    token, _ = create_test_user_and_get_token(
        client
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "password" not in data


def test_profile_uses_camel_case_fields(client):
    token, _ = create_test_user_and_get_token(
        client
    )

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Expected camelCase fields
    assert "fullName" in data
    assert "profileImageUrl" in data
    assert "createdAt" in data
    assert "updatedAt" in data

    # SQLAlchemy snake_case fields should not appear.
    assert "full_name" not in data
    assert "profile_image_url" not in data
    assert "created_at" not in data
    assert "updated_at" not in data


def test_profile_returns_authenticated_user(client):
    first_response = client.post(
        REGISTER_URL,
        json={
            "fullName": "User One",
            "email": "user1@example.com",
            "password": "password123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        REGISTER_URL,
        json={
            "fullName": "User Two",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    assert second_response.status_code == 201

    second_token = second_response.json()["token"]
    second_user = second_response.json()["user"]

    response = client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == second_user["id"]
    assert data["email"] == "user2@example.com"
    assert data["fullName"] == "User Two"