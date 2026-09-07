from app.features.auth.models.user import User
from app.features.auth.utils.password import verify_password
from app.features.auth.utils.jwt import decode_access_token

def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "user" in data
    assert "token" in data

    assert data["user"]["fullName"] == "Balpreet Singh"
    assert data["user"]["email"] == "balpreet@example.com"
    assert data["user"]["profileImageUrl"] == ""

    assert "id" in data["user"]
    assert "createdAt" in data["user"]
    assert "updatedAt" in data["user"]

    assert data["token"]
    assert "password" not in data["user"]


def test_register_user_with_profile_image(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
            "profileImageUrl": "https://example.com/image.jpg",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert (
        data["user"]["profileImageUrl"]
        == "https://example.com/image.jpg"
    )

    assert data["token"]


def test_register_duplicate_email(client):
    user_data = {
        "fullName": "Balpreet Singh",
        "email": "balpreet@example.com",
        "password": "password123",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "1234567",
        },
    )

    assert response.status_code == 422


def test_register_missing_full_name(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_empty_full_name(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_long_full_name(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "a" * 101,
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_password_exactly_8_characters(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 201


def test_register_missing_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_missing_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
        },
    )

    assert response.status_code == 422


def test_register_empty_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_empty_request_body(client):
    response = client.post(
        "/api/v1/auth/register",
        json={},
    )

    assert response.status_code == 422


def test_register_malformed_json(client):
    response = client.post(
        "/api/v1/auth/register",
        content='{"fullName": "Balpreet"',
        headers={
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 422


def test_register_profile_image_url_too_long(client):
    long_url = "a" * 501

    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
            "profileImageUrl": long_url,
        },
    )

    assert response.status_code == 422


def test_register_profile_image_url_exactly_500_characters(client):
    profile_image_url = "a" * 500

    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
            "profileImageUrl": profile_image_url,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user"]["profileImageUrl"] == profile_image_url


def test_registered_user_password_is_hashed(client, db):
    password = "password123"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": password,
        },
    )

    assert response.status_code == 201

    user = (
        db.query(User)
        .filter(User.email == "balpreet@example.com")
        .first()
    )

    assert user is not None

    # Plain password should never be stored.
    assert user.password != password

    # Stored password hash should verify correctly.
    assert verify_password(
        password,
        user.password,
    )


def test_duplicate_registration_does_not_create_another_user(
    client,
    db,
):
    user_data = {
        "fullName": "Balpreet Singh",
        "email": "balpreet@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert second_response.status_code == 400

    assert second_response.json() == {
        "detail": "User already exists",
    }

    user_count = db.query(User).count()

    assert user_count == 1


def test_register_token_belongs_to_registered_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    token = data["token"]
    user_id = data["user"]["id"]

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)


def test_register_full_name_with_one_character(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "A",
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201


def test_register_full_name_with_exactly_100_characters(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "A" * 100,
            "email": "balpreet@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201


def test_register_response_uses_camel_case_fields(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Balpreet Singh",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    user = response.json()["user"]

    assert "fullName" in user
    assert "profileImageUrl" in user
    assert "createdAt" in user
    assert "updatedAt" in user

    assert "full_name" not in user
    assert "profile_image_url" not in user
    assert "created_at" not in user
    assert "updated_at" not in user