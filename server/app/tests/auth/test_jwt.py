from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.features.auth.utils.jwt import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
)


def test_create_access_token():
    user_id = 1

    token = create_access_token(
        user_id=user_id,
    )

    assert token is not None
    assert isinstance(token, str)


def test_decode_access_token():
    user_id = 1

    token = create_access_token(
        user_id=user_id,
    )

    payload = decode_access_token(token)

    assert payload is not None

    assert payload["sub"] == str(user_id)


def test_access_token_contains_expiration():
    token = create_access_token(
        user_id=1,
    )

    payload = decode_access_token(token)

    assert "exp" in payload


def test_access_token_expiration_is_in_future():
    token = create_access_token(
        user_id=1,
    )

    payload = decode_access_token(token)

    current_timestamp = (
        datetime.now(timezone.utc)
        .timestamp()
    )

    assert payload["exp"] > current_timestamp


def test_invalid_access_token():
    invalid_token = "this.is.not.a.valid.jwt"

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(
            invalid_token,
        )


def test_expired_access_token():
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(
            expired_token,
        )


def test_tampered_access_token():
    token = create_access_token(
        user_id=1,
    )

    parts = token.split(".")

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

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(
            tampered_token,
        )


def test_access_token_contains_correct_user_id():
    user_id = 123

    token = create_access_token(
        user_id=user_id,
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "123"


def test_different_users_get_different_tokens():
    token_one = create_access_token(
        user_id=1,
    )

    token_two = create_access_token(
        user_id=2,
    )

    assert token_one != token_two

    payload_one = decode_access_token(
        token_one,
    )

    payload_two = decode_access_token(
        token_two,
    )

    assert payload_one["sub"] == "1"

    assert payload_two["sub"] == "2"


def test_token_with_wrong_secret_is_invalid():
    wrong_secret = "this-is-a-long-wrong-secret-key-for-testing-12345"

    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        wrong_secret,
        algorithm=ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)