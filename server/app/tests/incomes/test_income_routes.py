import jwt
import pytest
from decimal import Decimal, InvalidOperation

from datetime import datetime, timedelta, timezone

from app.features.auth.utils.jwt import (
    SECRET_KEY,
    ALGORITHM,
)


INCOME_URL = "/api/v1/income"


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_INCOME_PAYLOAD = {
    "icon": "salary",
    "amount": 100,
    "date": "2026-09-01",
    "source": "Salary",
    "description": "Monthly income",
}


EXPECTED_RESPONSE_KEYS = {
    "id",
    "icon",
    "amount",
    "date",
    "source",
    "description",
    "created_at",
    "updated_at",
}


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def create_user_and_get_token(
    client,
    email="income-test@example.com",
    full_name="Income Test User",
    password="password123",
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": full_name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    return {
        "user": data["user"],
        "token": data["token"],
        "headers": {
            "Authorization": (
                f"Bearer {data['token']}"
            ),
        },
    }


@pytest.fixture
def auth_user(client):
    return create_user_and_get_token(client)


@pytest.fixture
def second_auth_user(client):
    return create_user_and_get_token(
        client,
        email="income-second@example.com",
        full_name="Second Income User",
    )


def expired_headers(user_id: int):
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": (
                datetime.now(timezone.utc)
                - timedelta(minutes=1)
            ),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def invalid_token_headers():
    return {
        "Authorization": (
            "Bearer invalid.token.value"
        ),
    }


# ============================================================
# INCOME HELPERS
# ============================================================

def create_income(
    client,
    auth_user,
    **overrides,
):
    payload = DEFAULT_INCOME_PAYLOAD.copy()

    payload.update(overrides)

    response = client.post(
        INCOME_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text

    return response.json()


def get_income(
    client,
    auth_user,
    income_id,
):
    return client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )


def assert_income_response(
    data,
    *,
    expected_id=None,
    icon=None,
    amount=None,
    date=None,
    source=None,
    description=None,
):
    """
    Reusable helper for validating the public
    Income API response contract.
    """

    assert set(data.keys()) == EXPECTED_RESPONSE_KEYS

    assert isinstance(data["id"], int)
    assert isinstance(data["icon"], str)

    # Amount is serialized by the API as a decimal string.
    assert isinstance(data["amount"], (str, int, float))

    try:
        response_amount = Decimal(str(data["amount"]))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        pytest.fail(
            f"Invalid amount returned in response: "
            f"{data['amount']}"
        )

    assert response_amount > Decimal("0")

    assert isinstance(data["date"], str)
    assert isinstance(data["source"], str)
    assert isinstance(data["description"], str)

    # Audit timestamps are now exposed by the API.
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

    if expected_id is not None:
        assert data["id"] == expected_id

    if icon is not None:
        assert data["icon"] == icon

    if amount is not None:
        assert (
            response_amount
            == Decimal(str(amount))
        )

    if date is not None:
        assert data["date"] == date

    if source is not None:
        assert data["source"] == source

    if description is not None:
        assert data["description"] == description


# ============================================================
# POST /api/v1/income
# SUCCESS CASES
# ============================================================

def test_create_income_with_all_fields(
    client,
    auth_user,
):
    payload = {
        "icon": "salary",
        "amount": 50000,
        "date": "2026-09-01",
        "source": "Salary",
        "description": "Monthly salary",
    }

    response = client.post(
        INCOME_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert_income_response(
        data,
        icon="salary",
        amount=50000,
        date="2026-09-01",
        source="Salary",
        description="Monthly salary",
    )


def test_create_income_without_optional_icon_and_description(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 50000,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert_income_response(
        data,
        icon="",
        amount=50000,
        date="2026-09-01",
        source="Salary",
        description="",
    )


def test_create_income_with_empty_icon_and_description(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "icon": "",
            "amount": 50000,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert data["icon"] == ""
    assert data["description"] == ""


def test_create_income_with_two_decimal_amount(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "icon": "freelance",
            "amount": 100.50,
            "date": "2026-09-01",
            "source": "Freelancing",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("100.50")


def test_create_multiple_incomes_for_same_user(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
    )

    income_2 = create_income(
        client,
        auth_user,
        amount=200,
    )

    income_3 = create_income(
        client,
        auth_user,
        amount=300,
    )

    ids = {
        income_1["id"],
        income_2["id"],
        income_3["id"],
    }

    assert len(ids) == 3


# ============================================================
# POST
# AMOUNT VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100,
        -100.50,
        None,
        "abc",
        " ",
        "",
    ],
)
def test_create_income_rejects_invalid_amount(
    client,
    auth_user,
    amount,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_rejects_missing_amount(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "amount",
    [
        0.01,
        1,
        9999999999.99,
    ],
)
def test_create_income_amount_database_boundaries(
    client,
    auth_user,
    amount,
):
    """
    Numeric(12, 2) supports up to:
    9,999,999,999.99
    """

    response = client.post(
        INCOME_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "amount",
    [
        100.123,
        100.999,
        0.001,
    ],
)
def test_create_income_rejects_more_than_two_decimal_places(
    client,
    auth_user,
    amount,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# POST
# DATE VALIDATION
# ============================================================

def test_create_income_with_valid_date(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201


def test_create_income_date_is_trimmed(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": " 2026-09-01 ",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    assert (
        response.json()["date"]
        == "2026-09-01"
    )


@pytest.mark.parametrize(
    "date_value",
    [
        "01-09-2026",
        "2026-02-30",
        "",
        "     ",
        None,
        12345,
        True,
    ],
)
def test_create_income_rejects_invalid_date(
    client,
    auth_user,
    date_value,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": date_value,
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_rejects_missing_date(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# POST
# SOURCE VALIDATION
# ============================================================

def test_create_income_source_is_trimmed(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "   Salary   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    assert (
        response.json()["source"]
        == "Salary"
    )


@pytest.mark.parametrize(
    "source",
    [
        "",
        "     ",
        None,
        123,
        [],
        {},
    ],
)
def test_create_income_rejects_invalid_source(
    client,
    auth_user,
    source,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_rejects_missing_source(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "source, expected_status",
    [
        ("a" * 100, 201),
        ("a" * 101, 422),
        ("सैलरी", 201),
        ("收入 😀", 201),
        ("!@#$%^&*", 201),
        ("Freelancing & Consulting!", 201),
    ],
)
def test_create_income_source_boundaries_and_characters(
    client,
    auth_user,
    source,
    expected_status,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# POST
# DESCRIPTION VALIDATION
# ============================================================

def test_create_income_description_is_trimmed(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": (
                "   Monthly income   "
            ),
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    assert (
        response.json()["description"]
        == "Monthly income"
    )


def test_create_income_whitespace_only_description_becomes_empty(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "     ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    assert (
        response.json()["description"]
        == ""
    )


@pytest.mark.parametrize(
    "description, expected_status",
    [
        ("a" * 500, 201),
        ("a" * 501, 422),
        ("", 201),
        ("मासिक आय", 201),
        (None, 422),
        (123, 422),
        ([], 422),
    ],
)
def test_create_income_description_validation(
    client,
    auth_user,
    description,
    expected_status,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": description,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# POST
# ICON VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "icon, expected_status",
    [
        ("", 201),
        ("salary", 201),
        ("💰", 201),
        ("a" * 100, 201),
        ("a" * 101, 422),
        (None, 422),
        (123, 422),
        ([], 422),
    ],
)
def test_create_income_icon_validation(
    client,
    auth_user,
    icon,
    expected_status,
):
    response = client.post(
        INCOME_URL,
        json={
            "icon": icon,
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# POST
# EXTRA FIELDS / SECURITY
# ============================================================

@pytest.mark.parametrize(
    "extra_field",
    [
        {"invalidField": "test"},
        {"user_id": 999},
        {"id": 999},
        {"created_at": "2026-09-01T00:00:00Z"},
        {"updated_at": "2026-09-01T00:00:00Z"},
    ],
)
def test_create_income_rejects_extra_fields(
    client,
    auth_user,
    extra_field,
):
    payload = {
        "amount": 100,
        "date": "2026-09-01",
        "source": "Salary",
    }

    payload.update(extra_field)

    response = client.post(
        INCOME_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# POST
# AUTHENTICATION
# ============================================================

def test_create_income_without_token(
    client,
):
    response = client.post(
        INCOME_URL,
        json=DEFAULT_INCOME_PAYLOAD,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {
            "Authorization": (
                "Bearer invalid.token.value"
            ),
        },
        {
            "Authorization": "Basic token",
        },
        {
            "Authorization": "Token xyz",
        },
    ],
)
def test_create_income_with_invalid_authentication(
    client,
    headers,
):
    response = client.post(
        INCOME_URL,
        json=DEFAULT_INCOME_PAYLOAD,
        headers=headers,
    )

    assert response.status_code == 401


def test_create_income_with_expired_token(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json=DEFAULT_INCOME_PAYLOAD,
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/income
# SUCCESS
# ============================================================

def test_get_incomes_empty_collection(
    client,
    auth_user,
):
    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_one_income(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert_income_response(
        data[0],
        expected_id=income["id"],
    )


def test_get_multiple_incomes(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
    )

    income_2 = create_income(
        client,
        auth_user,
        amount=200,
    )

    income_3 = create_income(
        client,
        auth_user,
        amount=300,
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = {
        income["id"]
        for income in response.json()
    }

    assert ids == {
        income_1["id"],
        income_2["id"],
        income_3["id"],
    }


def test_get_incomes_response_contract(
    client,
    auth_user,
):
    create_income(
        client,
        auth_user,
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert_income_response(
        data[0],
    )


# ============================================================
# GET
# ORDERING
# ============================================================

def test_get_incomes_ordered_by_date_desc(
    client,
    auth_user,
):
    oldest = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Oldest",
    )

    middle = create_income(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
        source="Middle",
    )

    newest = create_income(
        client,
        auth_user,
        amount=300,
        date="2026-09-03",
        source="Newest",
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = [
        item["id"]
        for item in response.json()
    ]

    assert ids == [
        newest["id"],
        middle["id"],
        oldest["id"],
    ]


def test_get_same_date_incomes_use_created_at_desc_as_tie_breaker(
    client,
    auth_user,
):
    first = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="First",
    )

    second = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="Second",
    )

    third = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="Third",
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = [
        item["id"]
        for item in response.json()
    ]

    assert ids == [
        third["id"],
        second["id"],
        first["id"],
    ]


# ============================================================
# GET
# USER ISOLATION
# ============================================================

def test_get_incomes_user_isolation(
    client,
    auth_user,
    second_auth_user,
):
    income_a = create_income(
        client,
        auth_user,
        source="User A Income",
    )

    income_b = create_income(
        client,
        second_auth_user,
        source="User B Income",
    )

    response_a = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    response_b = client.get(
        INCOME_URL,
        headers=second_auth_user["headers"],
    )

    ids_a = {
        income["id"]
        for income in response_a.json()
    }

    ids_b = {
        income["id"]
        for income in response_b.json()
    }

    assert income_a["id"] in ids_a
    assert income_b["id"] not in ids_a

    assert income_b["id"] in ids_b
    assert income_a["id"] not in ids_b


# ============================================================
# GET
# AUTHENTICATION
# ============================================================

@pytest.mark.parametrize(
    "headers",
    [
        None,
        invalid_token_headers(),
        {"Authorization": "Basic token"},
        {"Authorization": "Token xyz"},
    ],
)
def test_get_incomes_rejects_invalid_authentication(
    client,
    headers,
):
    kwargs = {}

    if headers is not None:
        kwargs["headers"] = headers

    response = client.get(
        INCOME_URL,
        **kwargs,
    )

    assert response.status_code == 401


def test_get_incomes_with_expired_token(
    client,
    auth_user,
):
    response = client.get(
        INCOME_URL,
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/income/{income_id}
# SUCCESS
# ============================================================

def test_get_income_by_id(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert response.status_code == 200

    data = response.json()

    assert_income_response(
        data,
        expected_id=income["id"],
        icon=income["icon"],
        amount=income["amount"],
        date=income["date"],
        source=income["source"],
        description=income["description"],
    )


def test_get_correct_income_when_multiple_exist(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        source="Salary",
    )

    income_2 = create_income(
        client,
        auth_user,
        source="Bonus",
    )

    response = get_income(
        client,
        auth_user,
        income_2["id"],
    )

    assert response.status_code == 200

    assert (
        response.json()["id"]
        == income_2["id"]
    )

    assert (
        response.json()["id"]
        != income_1["id"]
    )


# ============================================================
# GET BY ID
# NOT FOUND / OWNERSHIP
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        999999,
        999999999,
        0,
        -1,
    ],
)
def test_get_income_by_id_not_found(
    client,
    auth_user,
    income_id,
):
    response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_get_another_users_income(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404


# ============================================================
# GET BY ID
# INVALID PATH
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        "abc",
        "1.5",
        "true",
    ],
)
def test_get_income_by_id_rejects_invalid_path_id(
    client,
    auth_user,
    income_id,
):
    response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# GET BY ID
# AUTHENTICATION
# ============================================================

def test_get_income_by_id_without_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        invalid_token_headers(),
        {"Authorization": "Basic token"},
        {"Authorization": "Token xyz"},
    ],
)
def test_get_income_by_id_invalid_authentication(
    client,
    auth_user,
    headers,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=headers,
    )

    assert response.status_code == 401


def test_get_income_by_id_with_expired_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# PATCH /api/v1/income/{income_id}
# SUCCESS
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"icon": "bonus"},
        {"amount": 500},
        {"date": "2026-09-05"},
        {"source": "Bonus"},
        {"description": "Updated description"},
    ],
)
def test_patch_each_field_individually(
    client,
    auth_user,
    payload,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    for key, value in payload.items():

        if key == "amount":
            assert Decimal(data[key]) == Decimal(value)

        else:
            assert data[key] == value


def test_patch_multiple_fields(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "icon": "bonus",
            "amount": 500,
            "date": "2026-09-10",
            "source": "Bonus",
            "description": "New description",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert_income_response(
        data,
        expected_id=income["id"],
        icon="bonus",
        amount=500,
        date="2026-09-10",
        source="Bonus",
        description="New description",
    )


def test_patch_partial_update_preserves_unspecified_fields(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["icon"] == "salary"
    assert Decimal(data["amount"]) == Decimal(100)
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Bonus"
    assert data["description"] == "Monthly"


def test_patch_persists_changes(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )

    update_response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 500,
            "source": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert Decimal(data["amount"]) == Decimal(500)
    assert data["source"] == "Bonus"


# ============================================================
# PATCH
# EMPTY BODY
# ============================================================

def test_patch_empty_json_body_returns_400(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == (
            "At least one field is required "
            "to update the income"
        )
    )


def test_patch_missing_body_returns_422(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH
# AMOUNT VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100,
        None,
        "abc",
        "",
        " ",
        100.123,
    ],
)
def test_patch_rejects_invalid_amount(
    client,
    auth_user,
    amount,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": amount,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_amount_with_two_decimal_places(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 100.50,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        Decimal(response.json()["amount"])
        == Decimal(100.50)
    )


# ============================================================
# PATCH
# DATE VALIDATION
# ============================================================

def test_patch_date_is_trimmed(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "date": " 2026-09-10 ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["date"]
        == "2026-09-10"
    )


@pytest.mark.parametrize(
    "date_value",
    [
        "",
        "   ",
        "01-09-2026",
        "2026-02-30",
        None,
        123,
    ],
)
def test_patch_rejects_invalid_date(
    client,
    auth_user,
    date_value,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "date": date_value,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH
# SOURCE VALIDATION
# ============================================================

def test_patch_source_is_trimmed(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "  Bonus  ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["source"]
        == "Bonus"
    )


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        None,
        123,
        "a" * 101,
    ],
)
def test_patch_rejects_invalid_source(
    client,
    auth_user,
    source,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "source",
    [
        "a" * 100,
        "收入 😀",
        "!@#$%^&*",
    ],
)
def test_patch_accepts_valid_source_boundaries_and_characters(
    client,
    auth_user,
    source,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["source"]
        == source
    )


# ============================================================
# PATCH
# DESCRIPTION VALIDATION
# ============================================================

def test_patch_empty_description(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "description": "",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["description"]
        == ""
    )


def test_patch_description_is_trimmed(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "description": (
                "   Updated description   "
            ),
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["description"]
        == "Updated description"
    )


def test_patch_whitespace_description_becomes_empty(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "description": "     ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    assert (
        response.json()["description"]
        == ""
    )


@pytest.mark.parametrize(
    "description, expected_status",
    [
        ("a" * 500, 200),
        ("a" * 501, 422),
        ("", 200),
        (None, 422),
        (123, 422),
        ("मासिक आय", 200),
    ],
)
def test_patch_description_validation(
    client,
    auth_user,
    description,
    expected_status,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "description": description,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# PATCH
# ICON VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "icon, expected_status",
    [
        ("", 200),
        ("salary", 200),
        ("💰", 200),
        ("a" * 100, 200),
        ("a" * 101, 422),
        (None, 422),
        (123, 422),
        ([], 422),
        ({}, 422),
        (True, 422),
    ]
)
def test_patch_icon_validation(
    client,
    auth_user,
    icon,
    expected_status,
):
    income = create_income(
        client,
        auth_user,
        icon="initial_icon",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "icon": icon,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# PATCH
# EXTRA FIELDS
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"unknown": "value"},
        {"user_id": 999},
        {"id": 999},
        {"created_at": "2026-09-01T00:00:00Z"},
        {"updated_at": "2026-09-01T00:00:00Z"},
    ],
)
def test_patch_rejects_extra_fields(
    client,
    auth_user,
    payload,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH
# NO CHANGE LOGIC
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"icon": "salary"},
        {"amount": 100},
        {"date": "2026-09-01"},
        {"source": "Salary"},
        {"description": "Monthly income"},
        {
            "icon": "salary",
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "Monthly income",
        },
    ],
)
def test_patch_same_value_returns_400(
    client,
    auth_user,
    payload,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly income",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "No changes detected in the income"
    )


def test_patch_trimmed_value_that_matches_existing_value_returns_400(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "   Salary   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


def test_patch_one_same_value_and_one_changed_value_succeeds(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 100,
            "source": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["amount"]) == Decimal(100)
    assert data["source"] == "Bonus"


# ============================================================
# PATCH
# NOT FOUND / OWNERSHIP
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        999999,
        0,
        -1,
    ],
)
def test_patch_non_existing_income_returns_404(
    client,
    auth_user,
    income_id,
):
    response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_update_another_users_income(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
        amount=500,
        source="Second User Salary",
        description="Original",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 999,
            "source": "Hacked",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert owner_response.status_code == 200

    data = owner_response.json()

    assert Decimal(data["amount"]) == Decimal(500)
    assert (
        data["source"]
        == "Second User Salary"
    )
    assert (
        data["description"]
        == "Original"
    )


# ============================================================
# PATCH
# INVALID PATH
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        "abc",
        "1.5",
        "true",
    ],
)
def test_patch_rejects_invalid_path_id(
    client,
    auth_user,
    income_id,
):
    response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH
# AUTHENTICATION
# ============================================================

def test_patch_without_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 200,
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        invalid_token_headers(),
        {"Authorization": "Basic token"},
        {"Authorization": "Token xyz"},
    ],
)
def test_patch_invalid_authentication(
    client,
    auth_user,
    headers,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 200,
        },
        headers=headers,
    )

    assert response.status_code == 401


def test_patch_with_expired_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 200,
        },
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# DELETE /api/v1/income/{income_id}
# SUCCESS
# ============================================================

def test_delete_income_returns_204(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_income_removes_record(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    delete_response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 404


def test_delete_one_income_does_not_affect_others(
    client,
    auth_user,
):
    income_a = create_income(
        client,
        auth_user,
        source="Income A",
    )

    income_b = create_income(
        client,
        auth_user,
        source="Income B",
    )

    income_c = create_income(
        client,
        auth_user,
        source="Income C",
    )

    response = client.delete(
        f"{INCOME_URL}/{income_b['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204

    assert get_income(
        client,
        auth_user,
        income_a["id"],
    ).status_code == 200

    assert get_income(
        client,
        auth_user,
        income_b["id"],
    ).status_code == 404

    assert get_income(
        client,
        auth_user,
        income_c["id"],
    ).status_code == 200


# ============================================================
# DELETE
# NOT FOUND / DOUBLE DELETE / OWNERSHIP
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        999999,
        0,
        -1,
    ],
)
def test_delete_non_existing_income_returns_404(
    client,
    auth_user,
    income_id,
):
    response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_same_income_twice(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    first_response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    second_response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert first_response.status_code == 204
    assert second_response.status_code == 404


def test_user_cannot_delete_another_users_income(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert owner_response.status_code == 200


# ============================================================
# DELETE
# INVALID PATH
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [
        "abc",
        "1.5",
        "true",
    ],
)
def test_delete_rejects_invalid_path_id(
    client,
    auth_user,
    income_id,
):
    response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# DELETE
# AUTHENTICATION
# ============================================================

def test_delete_without_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        invalid_token_headers(),
        {"Authorization": "Basic token"},
        {"Authorization": "Token xyz"},
    ],
)
def test_delete_invalid_authentication(
    client,
    auth_user,
    headers,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=headers,
    )

    assert response.status_code == 401


def test_delete_with_expired_token(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# DATABASE / STATE INTEGRITY
# ============================================================

def test_invalid_create_does_not_create_income(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": -100,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    get_response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_invalid_patch_does_not_modify_income(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": -500,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    get_response = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["icon"] == "salary"
    assert Decimal(data["amount"]) == Decimal(100)
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Monthly"


def test_failed_cross_user_update_does_not_modify_income(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
        amount=500,
        source="Original",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 999,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = get_income(
        client,
        second_auth_user,
        income["id"],
    )

    assert owner_response.status_code == 200

    assert (
        Decimal(owner_response.json()["amount"])
        == Decimal(500)
    )


def test_failed_cross_user_delete_does_not_delete_income(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
    )

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = get_income(
        client,
        second_auth_user,
        income["id"],
    )

    assert owner_response.status_code == 200


def test_updating_one_income_does_not_modify_another(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
        source="Income 1",
    )

    income_2 = create_income(
        client,
        auth_user,
        amount=200,
        source="Income 2",
    )

    update_response = client.patch(
        f"{INCOME_URL}/{income_1['id']}",
        json={
            "amount": 999,
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    income_2_response = get_income(
        client,
        auth_user,
        income_2["id"],
    )

    assert (
        Decimal(income_2_response.json()["amount"])
        == Decimal(200)
    )

    assert (
        income_2_response.json()["source"]
        == "Income 2"
    )


# ============================================================
# UPDATED MODEL REGRESSION TESTS
# ICON
# ============================================================

def test_icon_is_saved_and_returned_after_create(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="wallet",
    )

    response = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert response.status_code == 200

    assert (
        response.json()["icon"]
        == "wallet"
    )


def test_icon_update_is_persisted(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
    )

    update_response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "icon": "bonus",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert get_response.status_code == 200

    assert (
        get_response.json()["icon"]
        == "bonus"
    )


# ============================================================
# FULL CRUD LIFECYCLE
# ============================================================

def test_complete_income_crud_lifecycle(
    client,
    auth_user,
):
    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    create_response = client.post(
        INCOME_URL,
        json={
            "icon": "salary",
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "Initial",
        },
        headers=auth_user["headers"],
    )

    assert create_response.status_code == 201

    income = create_response.json()

    income_id = income["id"]

    assert_income_response(
        income,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Initial",
    )

    # --------------------------------------------------------
    # GET BY ID
    # --------------------------------------------------------

    get_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    assert (
        get_response.json()["description"]
        == "Initial"
    )

    # --------------------------------------------------------
    # GET ALL
    # --------------------------------------------------------

    get_all_response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert get_all_response.status_code == 200

    ids = {
        item["id"]
        for item in get_all_response.json()
    }

    assert income_id in ids

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    update_response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={
            "icon": "bonus",
            "amount": 500,
            "date": "2026-09-10",
            "source": "Bonus",
            "description": "Updated",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert_income_response(
        updated,
        expected_id=income_id,
        icon="bonus",
        amount=500,
        date="2026-09-10",
        source="Bonus",
        description="Updated",
    )

    # --------------------------------------------------------
    # VERIFY PERSISTENCE
    # --------------------------------------------------------

    verify_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert verify_response.status_code == 200

    assert (
        Decimal(verify_response.json()["amount"])
        == Decimal(500)
    )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    delete_response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    # --------------------------------------------------------
    # VERIFY DELETION
    # --------------------------------------------------------

    final_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert final_response.status_code == 404


# ============================================================
# UPDATED INCOME SCHEMA REGRESSION COVERAGE
# IMPORTANT:
# These tests are intentionally additive. The complete original
# Income route suite above is preserved without removing any
# existing test. The cases below cover additional edge cases for
# the updated required `source` field and its update semantics.
# ============================================================


@pytest.mark.parametrize(
    "source",
    [
        True,
        False,
        12.5,
        0.0,
    ],
)
def test_create_income_rejects_additional_invalid_source_types(
    client,
    auth_user,
    source,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_source_exactly_100_characters_is_returned_unchanged(
    client,
    auth_user,
):
    source = "a" * 100

    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text
    assert response.json()["source"] == source


def test_create_income_source_trimming_is_persisted(
    client,
    auth_user,
):
    created = create_income(
        client,
        auth_user,
        source="   Salary   ",
    )

    response = get_income(
        client,
        auth_user,
        created["id"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Salary"


def test_create_income_source_is_returned_in_list_response(
    client,
    auth_user,
):
    created = create_income(
        client,
        auth_user,
        source="Freelancing",
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    income = next(
        item
        for item in response.json()
        if item["id"] == created["id"]
    )

    assert "source" in income
    assert income["source"] == "Freelancing"


@pytest.mark.parametrize(
    "source",
    [
        [],
        {},
        True,
        False,
        12.5,
    ],
)
def test_patch_income_rejects_additional_invalid_source_types(
    client,
    auth_user,
    source,
):
    income = create_income(
        client,
        auth_user,
        source="Original",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": source,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    persisted = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert persisted.status_code == 200
    assert persisted.json()["source"] == "Original"


def test_patch_income_source_trimming_is_persisted(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "   Bonus   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Bonus"

    persisted = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert persisted.status_code == 200
    assert persisted.json()["source"] == "Bonus"


def test_patch_source_to_trimmed_existing_value_returns_no_changes(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "   Salary   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No changes detected in the income"
    )


def test_patch_source_only_preserves_all_other_income_fields(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=1234.50,
        date="2026-09-01",
        source="Salary",
        description="Original description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == income["id"]
    assert data["icon"] == "salary"
    assert Decimal(data["amount"]) == Decimal(1234.5)
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Bonus"
    assert data["description"] == "Original description"


def test_invalid_source_patch_does_not_change_any_other_field(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        icon="salary",
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Original",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "   ",
            "description": "Changed",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    persisted = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert persisted.status_code == 200

    data = persisted.json()
    assert data["icon"] == "salary"
    assert Decimal(data["amount"]) == Decimal(100)
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Original"


def test_cross_user_source_update_does_not_modify_owner_record(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        auth_user,
        source="Owner Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "Hacked Source",
        },
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = get_income(
        client,
        auth_user,
        income["id"],
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["source"] == "Owner Salary"


def test_updated_source_survives_complete_create_get_update_get_lifecycle(
    client,
    auth_user,
):
    create_response = client.post(
        INCOME_URL,
        json={
            "icon": "salary",
            "amount": "1000.50",
            "date": "2026-09-01",
            "source": "Salary",
            "description": "Monthly income",
        },
        headers=auth_user["headers"],
    )

    assert create_response.status_code == 201, create_response.text

    created = create_response.json()
    assert created["source"] == "Salary"

    first_get = get_income(
        client,
        auth_user,
        created["id"],
    )

    assert first_get.status_code == 200
    assert first_get.json()["source"] == "Salary"

    update_response = client.patch(
        f"{INCOME_URL}/{created['id']}",
        json={
            "source": "   Bonus   ",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200
    assert update_response.json()["source"] == "Bonus"

    second_get = get_income(
        client,
        auth_user,
        created["id"],
    )

    assert second_get.status_code == 200
    assert second_get.json()["source"] == "Bonus"

# ============================================================
# 1 & 2. AUDIT TIMESTAMPS
# Verify updated_at changes and created_at remains unchanged
# ============================================================

def test_income_updated_at_changes_and_created_at_remains_same_after_update(
    client,
    auth_user,
    db,
):
    from app.features.income.models.income import Income

    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    income_db = (
        db.query(Income)
        .filter(Income.id == income["id"])
        .first()
    )

    assert income_db is not None

    original_created_at = income_db.created_at
    original_updated_at = income_db.updated_at

    assert original_created_at is not None
    assert original_updated_at is not None

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "source": "Freelancing",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    # Force SQLAlchemy to reload the latest database values.
    db.expire_all()

    updated_income_db = (
        db.query(Income)
        .filter(Income.id == income["id"])
        .first()
    )

    assert updated_income_db is not None

    # created_at must remain unchanged.
    assert (
        updated_income_db.created_at
        == original_created_at
    )

    # updated_at must change after a real update.
    assert (
        updated_income_db.updated_at
        > original_updated_at
    )


# ============================================================
# 3. PATCH ICON VALIDATION
# Includes missing invalid types
# ============================================================

@pytest.mark.parametrize(
    "icon, expected_status",
    [
        ("", 200),
        ("salary", 200),
        ("💰", 200),
        ("a" * 100, 200),
        ("a" * 101, 422),
        (None, 422),
        (123, 422),
        ([], 422),
        ({}, 422),
        (True, 422),
    ],
)
def test_patch_icon_validation(
    client,
    auth_user,
    icon,
    expected_status,
):
    income = create_income(
        client,
        auth_user,
        icon="initial_icon",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "icon": icon,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# 4. NEW INCOME HAS AUTOMATIC AUDIT TIMESTAMPS
# ============================================================

def test_new_income_has_created_and_updated_timestamps(
    client,
    auth_user,
    db,
):
    from app.features.income.models.income import Income

    income = create_income(
        client,
        auth_user,
        source="Salary",
    )

    income_db = (
        db.query(Income)
        .filter(Income.id == income["id"])
        .first()
    )

    assert income_db is not None

    assert income_db.created_at is not None
    assert income_db.updated_at is not None

    assert (
        income_db.updated_at
        >= income_db.created_at
    )

# ============================================================
# 5. SAME-DATE ORDERING WITH CREATED_AT TIE BREAKER
# More deterministic database-level test
# ============================================================

def test_get_same_date_incomes_use_created_at_desc_as_tie_breaker(
    client,
    auth_user,
    db,
):
    from datetime import datetime, timedelta, timezone

    from app.features.income.models.income import Income

    base_time = datetime(
        2026,
        9,
        10,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    first = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="First",
    )

    second = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="Second",
    )

    third = create_income(
        client,
        auth_user,
        date="2026-09-10",
        source="Third",
    )

    first_db = (
        db.query(Income)
        .filter(Income.id == first["id"])
        .first()
    )

    second_db = (
        db.query(Income)
        .filter(Income.id == second["id"])
        .first()
    )

    third_db = (
        db.query(Income)
        .filter(Income.id == third["id"])
        .first()
    )

    assert first_db is not None
    assert second_db is not None
    assert third_db is not None

    # Explicit timestamps make the ordering test deterministic.
    first_db.created_at = base_time
    second_db.created_at = (
        base_time
        + timedelta(seconds=1)
    )
    third_db.created_at = (
        base_time
        + timedelta(seconds=2)
    )

    db.commit()

    # Clear SQLAlchemy's cached objects.
    db.expire_all()

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    # Only check the three incomes created by this test because
    # other test data may also exist in the test database.
    test_income_ids = {
        first["id"],
        second["id"],
        third["id"],
    }

    matching_incomes = [
        income
        for income in data
        if income["id"] in test_income_ids
    ]

    assert [
        income["id"]
        for income in matching_incomes
    ] == [
        third["id"],
        second["id"],
        first["id"],
    ]