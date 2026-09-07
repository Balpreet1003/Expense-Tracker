from app.features.auth.utils.password import (
    hash_password,
    verify_password,
)


def test_hash_password():
    password = "password123"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_verify_correct_password():
    password = "password123"

    hashed_password = hash_password(password)

    result = verify_password(
        password,
        hashed_password,
    )

    assert result is True


def test_verify_incorrect_password():
    password = "password123"

    hashed_password = hash_password(password)

    result = verify_password(
        "wrongpassword",
        hashed_password,
    )

    assert result is False


def test_same_password_generates_different_hashes():
    password = "password123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2

    assert verify_password(
        password,
        hash1,
    )

    assert verify_password(
        password,
        hash2,
    )


def test_different_passwords_generate_different_hashes():
    password_one = "password123"
    password_two = "password456"

    hash_one = hash_password(password_one)
    hash_two = hash_password(password_two)

    assert hash_one != hash_two

    assert verify_password(
        password_one,
        hash_one,
    )

    assert verify_password(
        password_two,
        hash_two,
    )