import pytest
import jwt
from datetime import datetime, timedelta, timezone

from app.features.auth.models.user import User
from app.features.auth.utils.jwt import SECRET_KEY, ALGORITHM


INCOME_URL = "/api/v1/income"


# ============================================================
# Authentication Helpers
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

    assert response.status_code == 201

    data = response.json()

    return {
        "user": data["user"],
        "token": data["token"],
        "headers": {
            "Authorization": f"Bearer {data['token']}",
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


def expired_headers(user_id):
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {"Authorization": f"Bearer {token}"}


# ============================================================
# Income Helper
# ============================================================

def create_income(client, auth_user, **overrides):
    payload = {
        "amount": 100.0,
        "date": "2026-09-01",
        "source": "Salary",
        "description": "Monthly income",
    }

    payload.update(overrides)

    response = client.post(
        INCOME_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text

    return response.json()


# ============================================================
# POST /api/v1/income - Success Cases
# ============================================================

def test_create_income_with_all_fields(client, auth_user):
    payload = {
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

    assert set(data.keys()) == {
        "id",
        "amount",
        "date",
        "source",
        "description",
    }
    assert isinstance(data["id"], int)
    assert data["amount"] == 50000
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Monthly salary"


def test_create_income_without_description(client, auth_user):
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
    assert response.json()["description"] == ""


def test_create_income_with_empty_description(client, auth_user):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 50000,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_income_with_decimal_amount(client, auth_user):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100.50,
            "date": "2026-09-01",
            "source": "Freelancing",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["amount"] == 100.50


def test_create_multiple_incomes_for_same_user(client, auth_user):
    income_1 = create_income(client, auth_user, amount=100)
    income_2 = create_income(client, auth_user, amount=200)
    income_3 = create_income(client, auth_user, amount=300)

    ids = {
        income_1["id"],
        income_2["id"],
        income_3["id"],
    }

    assert len(ids) == 3

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) == 3


# ============================================================
# POST - Amount Validation
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [0, -100, -100.50, None, "abc", "   "],
)
def test_create_income_invalid_amount(client, auth_user, amount):
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


def test_create_income_missing_amount(client, auth_user):
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
    [999999999999999, 100.123456789],
)
def test_create_income_large_and_high_precision_amount(client, auth_user, amount):
    response = client.post(
        INCOME_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code in (201, 422)


# ============================================================
# POST - Date Validation
# ============================================================

def test_create_income_valid_date(client, auth_user):
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


def test_create_income_date_is_trimmed(client, auth_user):
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
    assert response.json()["date"] == "2026-09-01"


@pytest.mark.parametrize(
    "date_value",
    ["01-09-2026", "2026-02-30", "", "     ", None, 12345],
)
def test_create_income_invalid_date(client, auth_user, date_value):
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


def test_create_income_missing_date(client, auth_user):
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
# POST - Source Validation
# ============================================================

def test_create_income_source_is_trimmed(client, auth_user):
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
    assert response.json()["source"] == "Salary"


@pytest.mark.parametrize(
    "source",
    ["", "     ", None, 123],
)
def test_create_income_invalid_source(client, auth_user, source):
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


def test_create_income_missing_source(client, auth_user):
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
# POST - Description Validation
# ============================================================

def test_create_income_description_is_trimmed(client, auth_user):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "   Monthly Salary   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == "Monthly Salary"


def test_create_income_whitespace_description_becomes_empty(client, auth_user):
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
    assert response.json()["description"] == ""


@pytest.mark.parametrize(
    "description, expected_status",
    [
        ("a" * 500, 201),
        ("a" * 501, 422),
        (None, 422),
        (123, 422),
        ("मासिक आय", 201),
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
# POST - Request Security
# ============================================================

@pytest.mark.parametrize(
    "extra_field",
    [
        {"invalidField": "test"},
        {"user_id": 999},
        {"id": 999},
    ],
)
def test_create_income_rejects_extra_fields(
    client,
    auth_user,
    extra_field,
):
    payload = {
        "amount": 5000,
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
# Authentication Tests
# ============================================================

def test_create_income_without_token(client):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": "Bearer invalid.token.value"},
        {"Authorization": "Basic token"},
        {"Authorization": "Token xyz"},
    ],
)
def test_create_income_with_invalid_or_wrong_auth_scheme(client, headers):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=headers,
    )

    assert response.status_code == 401


def test_create_income_with_expired_token(client, auth_user):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
        },
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


def test_token_for_non_existing_user_is_rejected(client):
    # A correctly signed token for a user ID that does not exist.
    token = jwt.encode(
        {
            "sub": "99999999",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        INCOME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/income
# ============================================================

def test_get_incomes_empty_collection(client, auth_user):
    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_one_income(client, auth_user):
    income = create_income(client, auth_user)

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == income["id"]


def test_get_multiple_incomes(client, auth_user):
    income_1 = create_income(client, auth_user, amount=100)
    income_2 = create_income(client, auth_user, amount=200)

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = {income["id"] for income in response.json()}

    assert ids == {income_1["id"], income_2["id"]}


def test_get_incomes_response_contract(client, auth_user):
    create_income(client, auth_user)

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    income = response.json()[0]

    assert set(income.keys()) == {
        "id",
        "amount",
        "date",
        "source",
        "description",
    }
    assert isinstance(income["id"], int)
    assert isinstance(income["amount"], (int, float))
    assert isinstance(income["source"], str)
    assert isinstance(income["description"], str)

    assert "user_id" not in income
    assert "password" not in income
    assert "hashed_password" not in income
    assert "token" not in income


def test_get_incomes_ordered_by_date_desc_and_id_desc(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
    )
    income_2 = create_income(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
    )
    income_3 = create_income(
        client,
        auth_user,
        amount=300,
        date="2026-09-02",
    )

    response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = [income["id"] for income in response.json()]

    assert ids == [
        income_3["id"],
        income_2["id"],
        income_1["id"],
    ]


def test_get_all_user_isolation(client, auth_user, second_auth_user):
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

    ids_a = {income["id"] for income in response_a.json()}
    ids_b = {income["id"] for income in response_b.json()}

    assert income_a["id"] in ids_a
    assert income_b["id"] not in ids_a

    assert income_b["id"] in ids_b
    assert income_a["id"] not in ids_b


def test_get_incomes_without_token(client):
    response = client.get(INCOME_URL)

    assert response.status_code == 401


def test_get_incomes_with_invalid_token(client):
    response = client.get(
        INCOME_URL,
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_get_incomes_with_expired_token(client, auth_user):
    response = client.get(
        INCOME_URL,
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/income/{income_id}
# ============================================================

def test_get_income_by_id(client, auth_user):
    income = create_income(client, auth_user)

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data == income


def test_get_correct_income_when_multiple_exist(client, auth_user):
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

    response = client.get(
        f"{INCOME_URL}/{income_2['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["id"] == income_2["id"]
    assert response.json()["id"] != income_1["id"]


@pytest.mark.parametrize(
    "income_id",
    [999999, 999999999],
)
def test_get_non_existing_income(client, auth_user, income_id):
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
    income = create_income(client, auth_user)

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404


def test_owner_can_get_own_income(client, auth_user):
    income = create_income(client, auth_user)

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "income_id",
    ["abc", "1.5"],
)
def test_get_income_invalid_path_id(client, auth_user, income_id):
    response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "income_id",
    [-1, 0],
)
def test_get_income_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    income_id,
):
    # Current route has no Path(gt=0), so service lookup returns 404.
    response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_get_income_by_id_without_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.get(f"{INCOME_URL}/{income['id']}")

    assert response.status_code == 401


# ============================================================
# PATCH /api/v1/income/{income_id} - Success Cases
# ============================================================

def test_patch_amount_only(client, auth_user):
    income = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 500},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 500
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Monthly"


def test_patch_date_only(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"date": "2026-09-05"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-09-05"


def test_patch_source_only(client, auth_user):
    income = create_income(client, auth_user, source="Salary")

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"source": "Bonus"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Bonus"


def test_patch_description_only(client, auth_user):
    income = create_income(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"description": "New description"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "New description"


def test_patch_amount_and_date(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 500,
            "date": "2026-09-10",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert data["amount"] == 500
    assert data["date"] == "2026-09-10"


def test_patch_amount_and_source(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 500,
            "source": "Freelancing",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert data["amount"] == 500
    assert data["source"] == "Freelancing"


def test_patch_all_fields(client, auth_user):
    income = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Old",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 500,
            "date": "2026-09-10",
            "source": "Bonus",
            "description": "New",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == income["id"]
    assert data["amount"] == 500
    assert data["date"] == "2026-09-10"
    assert data["source"] == "Bonus"
    assert data["description"] == "New"


def test_patch_partial_update_preserves_unspecified_fields(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"source": "Bonus"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 100
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Bonus"
    assert data["description"] == "Monthly"


# ============================================================
# PATCH - Empty Request
# ============================================================

def test_patch_empty_body(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "At least one field is required to update the income"
    )


def test_patch_missing_body(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Amount Validation
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [0, -100, -10.5, None, "abc", "   "],
)
def test_patch_invalid_amount(client, auth_user, amount):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": amount},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "amount",
    [999999999999999, 100.123456789],
)
def test_patch_large_and_high_precision_amount(
    client,
    auth_user,
    amount,
):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": amount},
        headers=auth_user["headers"],
    )

    assert response.status_code in (200, 422)


# ============================================================
# PATCH - Date Validation
# ============================================================

def test_patch_date_is_trimmed(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"date": " 2026-09-10 "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-09-10"


@pytest.mark.parametrize(
    "date_value",
    ["", "   ", "01-09-2026", "2026-02-30", None, 123],
)
def test_patch_invalid_date(client, auth_user, date_value):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"date": date_value},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Source Validation
# ============================================================

def test_patch_source_is_trimmed(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"source": "  Bonus  "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Bonus"


@pytest.mark.parametrize(
    "source",
    ["", "   ", None, 123, "a" * 101],
)
def test_patch_invalid_source(client, auth_user, source):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"source": source},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_source_exactly_100_characters(client, auth_user):
    income = create_income(client, auth_user)

    source = "a" * 100

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"source": source},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == source


# ============================================================
# PATCH - Description Validation
# ============================================================

def test_patch_empty_description(client, auth_user):
    income = create_income(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"description": ""},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == ""


def test_patch_whitespace_description_is_trimmed(client, auth_user):
    income = create_income(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"description": "   New description   "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "New description"


def test_patch_whitespace_only_description_becomes_empty(
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
        json={"description": "     "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == ""


@pytest.mark.parametrize(
    "description, expected_status",
    [
        ("a" * 500, 200),
        ("a" * 501, 422),
        (None, 422),
        (123, 422),
    ],
)
def test_patch_description_validation(
    client,
    auth_user,
    description,
    expected_status,
):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
        json={"description": description},
    )

    assert response.status_code == expected_status


# ============================================================
# PATCH - Extra Fields / Security
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"unknown": "value"},
        {"user_id": 999},
        {"id": 999},
    ],
)
def test_patch_rejects_extra_fields(client, auth_user, payload):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH - No Actual Change Logic
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"amount": 100},
        {"date": "2026-09-01"},
        {"source": "Salary"},
        {"description": "Monthly income"},
        {
            "amount": 100,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "Monthly income",
        },
    ],
)
def test_patch_no_actual_change_returns_400(
    client,
    auth_user,
    payload,
):
    income = create_income(
        client,
        auth_user,
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


def test_patch_some_unchanged_and_one_changed_succeeds(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=5000,
        source="Salary",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 5000,
            "source": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert data["amount"] == 5000
    assert data["source"] == "Bonus"


def test_patch_whitespace_normalized_same_value_returns_400(
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
        json={"source": " Salary "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


# ============================================================
# PATCH - Resource / Authorization / Authentication
# ============================================================

@pytest.mark.parametrize(
    "income_id",
    [999999, 999999999],
)
def test_patch_non_existing_income(client, auth_user, income_id):
    response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={"amount": 500},
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
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 999},
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    get_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json()["amount"] == 100
    assert get_response.json()["date"] == "2026-09-01"
    assert get_response.json()["source"] == "Salary"
    assert get_response.json()["description"] == "Monthly"


def test_owner_can_update_own_income(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200


def test_patch_invalid_id(client, auth_user):
    response = client.patch(
        f"{INCOME_URL}/abc",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_without_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 200},
    )

    assert response.status_code == 401


def test_patch_with_invalid_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 200},
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_patch_with_expired_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 200},
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# DELETE /api/v1/income/{income_id}
# ============================================================

def test_delete_income(client, auth_user):
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_income_verifies_deletion(client, auth_user):
    income = create_income(client, auth_user)

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


def test_delete_one_income_does_not_affect_others(client, auth_user):
    income_a = create_income(client, auth_user, source="A")
    income_b = create_income(client, auth_user, source="B")
    income_c = create_income(client, auth_user, source="C")

    response = client.delete(
        f"{INCOME_URL}/{income_b['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204

    assert client.get(
        f"{INCOME_URL}/{income_a['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{INCOME_URL}/{income_b['id']}",
        headers=auth_user["headers"],
    ).status_code == 404

    assert client.get(
        f"{INCOME_URL}/{income_c['id']}",
        headers=auth_user["headers"],
    ).status_code == 200


@pytest.mark.parametrize(
    "income_id",
    [999999, 999999999],
)
def test_delete_non_existing_income(client, auth_user, income_id):
    response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_same_income_twice(client, auth_user):
    income = create_income(client, auth_user)

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
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert owner_response.status_code == 200


def test_owner_can_delete_own_income(client, auth_user):
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "income_id",
    ["abc", "1.5"],
)
def test_delete_invalid_path_id(client, auth_user, income_id):
    response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "income_id",
    [-1, 0],
)
def test_delete_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    income_id,
):
    response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_without_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
    )

    assert response.status_code == 401


def test_delete_with_invalid_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_delete_with_expired_token(client, auth_user):
    income = create_income(client, auth_user)

    response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# Database Integrity / Regression
# ============================================================

def test_invalid_create_does_not_create_income(client, auth_user):
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


def test_invalid_patch_does_not_modify_income(client, auth_user):
    income = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
        description="Monthly",
    )

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": -500},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    get_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    data = get_response.json()

    assert data["amount"] == 100
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Monthly"


def test_failed_delete_does_not_delete_other_incomes(
    client,
    auth_user,
):
    income_1 = create_income(client, auth_user, source="Income 1")
    income_2 = create_income(client, auth_user, source="Income 2")

    response = client.delete(
        f"{INCOME_URL}/999999",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    assert client.get(
        f"{INCOME_URL}/{income_1['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{INCOME_URL}/{income_2['id']}",
        headers=auth_user["headers"],
    ).status_code == 200


def test_updating_one_income_does_not_modify_another(
    client,
    auth_user,
):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )
    income_2 = create_income(
        client,
        auth_user,
        amount=200,
        source="Bonus",
    )

    update_response = client.patch(
        f"{INCOME_URL}/{income_1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_income_2 = client.get(
        f"{INCOME_URL}/{income_2['id']}",
        headers=auth_user["headers"],
    )

    assert get_income_2.status_code == 200
    assert get_income_2.json()["amount"] == 200
    assert get_income_2.json()["source"] == "Bonus"


# ============================================================
# Full CRUD Lifecycle
# ============================================================

def test_complete_income_crud_lifecycle(client, auth_user):
    # CREATE
    create_response = client.post(
        INCOME_URL,
        json={
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

    # GET BY ID
    get_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Initial"

    # GET ALL
    get_all_response = client.get(
        INCOME_URL,
        headers=auth_user["headers"],
    )

    assert get_all_response.status_code == 200
    assert income_id in {
        item["id"]
        for item in get_all_response.json()
    }

    # UPDATE
    update_response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={
            "amount": 500,
            "description": "Updated",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200
    assert update_response.json()["amount"] == 500
    assert update_response.json()["description"] == "Updated"

    # GET UPDATED
    get_updated_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert get_updated_response.status_code == 200
    assert get_updated_response.json()["amount"] == 500

    # DELETE
    delete_response = client.delete(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    # FINAL GET
    final_get_response = client.get(
        f"{INCOME_URL}/{income_id}",
        headers=auth_user["headers"],
    )

    assert final_get_response.status_code == 404


# ============================================================
# Multi-User Integration
# ============================================================

def test_complete_multi_user_income_isolation(
    client,
    auth_user,
    second_auth_user,
):
    income_a1 = create_income(
        client,
        auth_user,
        source="A1",
    )
    income_a2 = create_income(
        client,
        auth_user,
        source="A2",
    )

    income_b1 = create_income(
        client,
        second_auth_user,
        source="B1",
    )
    income_b2 = create_income(
        client,
        second_auth_user,
        source="B2",
    )

    # Owners can access their own records.
    assert client.get(
        f"{INCOME_URL}/{income_a1['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{INCOME_URL}/{income_b1['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 200

    # Cross-user GET is blocked.
    assert client.get(
        f"{INCOME_URL}/{income_b1['id']}",
        headers=auth_user["headers"],
    ).status_code == 404

    assert client.get(
        f"{INCOME_URL}/{income_a1['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 404

    # Cross-user UPDATE is blocked.
    assert client.patch(
        f"{INCOME_URL}/{income_b1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    ).status_code == 404

    # Cross-user DELETE is blocked.
    assert client.delete(
        f"{INCOME_URL}/{income_a2['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 404

    # Verify records remain accessible to owners.
    assert client.get(
        f"{INCOME_URL}/{income_a2['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{INCOME_URL}/{income_b2['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 200


# ============================================================
# Regression Scenarios
# ============================================================

def test_multiple_sequential_creates_have_unique_ids(
    client,
    auth_user,
):
    incomes = [
        create_income(
            client,
            auth_user,
            amount=100 + index,
        )
        for index in range(5)
    ]

    ids = [income["id"] for income in incomes]

    assert len(ids) == len(set(ids))


def test_update_income_multiple_times(client, auth_user):
    income = create_income(
        client,
        auth_user,
        amount=100,
    )

    for amount in [200, 300]:
        response = client.patch(
            f"{INCOME_URL}/{income['id']}",
            json={"amount": amount},
            headers=auth_user["headers"],
        )

        assert response.status_code == 200

    final_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert final_response.status_code == 200
    assert final_response.json()["amount"] == 300


def test_delete_after_update(client, auth_user):
    income = create_income(client, auth_user)

    update_response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 500},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    delete_response = client.delete(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204


def test_valid_update_after_failed_update(client, auth_user):
    income = create_income(
        client,
        auth_user,
        amount=100,
    )

    invalid_response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": -100},
        headers=auth_user["headers"],
    )

    assert invalid_response.status_code == 422

    valid_response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert valid_response.status_code == 200
    assert valid_response.json()["amount"] == 200


def test_same_date_records_remain_independent(client, auth_user):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        source="Salary",
    )
    income_2 = create_income(
        client,
        auth_user,
        amount=200,
        date="2026-09-01",
        source="Bonus",
    )

    update_response = client.patch(
        f"{INCOME_URL}/{income_1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    income_2_response = client.get(
        f"{INCOME_URL}/{income_2['id']}",
        headers=auth_user["headers"],
    )

    assert income_2_response.status_code == 200
    assert income_2_response.json()["amount"] == 200


def test_same_source_records_remain_independent(client, auth_user):
    income_1 = create_income(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )
    income_2 = create_income(
        client,
        auth_user,
        amount=200,
        source="Salary",
    )

    delete_response = client.delete(
        f"{INCOME_URL}/{income_1['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    remaining_response = client.get(
        f"{INCOME_URL}/{income_2['id']}",
        headers=auth_user["headers"],
    )

    assert remaining_response.status_code == 200
    assert remaining_response.json()["amount"] == 200


# ============================================================
# MISSING GET INCOME BY ID AUTHENTICATION TESTS
# ============================================================


def test_get_income_by_id_with_invalid_token(
    client,
    auth_user,
):
    income = create_income(client, auth_user)

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers={
            "Authorization": "Bearer invalid.token.value",
        },
    )

    assert response.status_code == 401


def test_get_income_by_id_with_expired_token(
    client,
    auth_user,
):
    income = create_income(client, auth_user)

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# GET INCOME BY ID RESPONSE CONTRACT
# ============================================================


def test_get_income_by_id_response_contract(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
    )

    response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "amount",
        "date",
        "source",
        "description",
    }

    assert isinstance(data["id"], int)
    assert isinstance(data["amount"], (int, float))
    assert isinstance(data["date"], str)
    assert isinstance(data["source"], str)
    assert isinstance(data["description"], str)

    assert "user_id" not in data
    assert "password" not in data
    assert "hashed_password" not in data
    assert "token" not in data


# ============================================================
# PATCH INVALID ID TESTS
# ============================================================


@pytest.mark.parametrize(
    "income_id",
    [
        "abc",
        "1.5",
    ],
)
def test_patch_invalid_id(
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


@pytest.mark.parametrize(
    "income_id",
    [
        -1,
        0,
    ],
)
def test_patch_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    income_id,
):
    response = client.patch(
        f"{INCOME_URL}/{income_id}",
        json={
            "amount": 500,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


# ============================================================
# PATCH RESPONSE CONTRACT
# ============================================================


def test_patch_income_response_contract(
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
            "amount": 500,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "amount",
        "date",
        "source",
        "description",
    }

    assert isinstance(data["id"], int)
    assert isinstance(data["amount"], (int, float))
    assert isinstance(data["date"], str)
    assert isinstance(data["source"], str)
    assert isinstance(data["description"], str)

    assert data["amount"] == 500

    assert "user_id" not in data
    assert "password" not in data
    assert "hashed_password" not in data
    assert "token" not in data


# ============================================================
# DELETE INVALID AUTHENTICATION TESTS
# ============================================================


@pytest.mark.parametrize(
    "headers",
    [
        {
            "Authorization": "Basic token",
        },
        {
            "Authorization": "Token xyz",
        },
        {
            "Authorization": "Bearer invalid.token.value",
        },
    ],
)
def test_delete_income_invalid_authentication(
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


# ============================================================
# CREATE LARGE AND HIGH-PRECISION AMOUNT TESTS
# ============================================================


def test_create_income_with_very_large_amount(
    client,
    auth_user,
):
    response = client.post(
        INCOME_URL,
        json={
            "amount": 999999999999999,
            "date": "2026-09-01",
            "source": "Salary",
            "description": "Very large income",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 999999999999999


def test_create_income_with_high_precision_amount(
    client,
    auth_user,
):
    amount = 100.123456789

    response = client.post(
        INCOME_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "source": "Freelancing",
            "description": "High precision amount",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == pytest.approx(amount)


# ============================================================
# PATCH LARGE AND HIGH-PRECISION AMOUNT TESTS
# ============================================================


def test_patch_income_with_very_large_amount(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
    )

    large_amount = 999999999999999

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": large_amount,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == large_amount


def test_patch_income_with_high_precision_amount(
    client,
    auth_user,
):
    income = create_income(
        client,
        auth_user,
        amount=100,
    )

    amount = 100.123456789

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": amount,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == pytest.approx(amount)


# ============================================================
# STRONGER MULTI-USER UPDATE ISOLATION TEST
# ============================================================


def test_user_cannot_update_another_users_income_and_data_remains_unchanged(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
        amount=500,
        source="Second User Salary",
        description="Original description",
    )

    income_before_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert income_before_response.status_code == 200

    income_before = income_before_response.json()

    response = client.patch(
        f"{INCOME_URL}/{income['id']}",
        json={
            "amount": 999,
            "source": "Hacked Source",
            "description": "Hacked Description",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    income_after_response = client.get(
        f"{INCOME_URL}/{income['id']}",
        headers=second_auth_user["headers"],
    )

    assert income_after_response.status_code == 200

    income_after = income_after_response.json()

    assert income_after["id"] == income_before["id"]
    assert income_after["amount"] == income_before["amount"]
    assert income_after["date"] == income_before["date"]
    assert income_after["source"] == income_before["source"]
    assert income_after["description"] == income_before["description"]


# ============================================================
# STRONGER MULTI-USER DELETE ISOLATION TEST
# ============================================================


def test_user_cannot_delete_another_users_income_and_record_remains(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income(
        client,
        second_auth_user,
        amount=500,
        source="Second User Salary",
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

    data = owner_response.json()

    assert data["id"] == income["id"]
    assert data["amount"] == income["amount"]
    assert data["source"] == income["source"]