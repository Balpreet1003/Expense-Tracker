import pytest
import jwt
import time
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta, timezone

from app.features.auth.models.user import User
from app.features.auth.utils.jwt import SECRET_KEY, ALGORITHM


EXPENSE_URL = "/api/v1/expense"


# ============================================================
# Authentication Helpers
# ============================================================

def create_user_and_get_token(
    client,
    email="expense-test@example.com",
    full_name="Expense Test User",
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
        email="expense-second@example.com",
        full_name="Second Expense User",
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
# Expense Helper
# ============================================================

def create_expense(client, auth_user, **overrides):
    payload = {
        "icon": "",
        "amount": 100.0,
        "date": "2026-09-01",
        "category": "Food",
        "description": "Monthly expense",
    }

    payload.update(overrides)

    response = client.post(
        EXPENSE_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text

    return response.json()


# ============================================================
# POST /api/v1/expense - Success Cases
# ============================================================

def test_create_expense_with_all_fields(client, auth_user):
    payload = {
        "amount": 50000,
        "date": "2026-09-01",
        "category": "Food",
        "description": "Monthly expense",
    }

    response = client.post(
        EXPENSE_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "icon",
        "amount",
        "date",
        "category",
        "description",
        "created_at",
        "updated_at",
    }
    assert isinstance(data["id"], int)
    assert isinstance(data["icon"], str)
    assert data["icon"] == ""
    assert Decimal(data["amount"]) == Decimal(50000)
    assert data["date"] == "2026-09-01"
    assert data["category"] == "Food"
    assert data["description"] == "Monthly expense"
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


def test_create_expense_without_description(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 50000,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_expense_with_empty_description(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 50000,
            "date": "2026-09-01",
            "category": "Food",
            "description": "",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_expense_with_decimal_amount(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100.50,
            "date": "2026-09-01",
            "category": "Travel",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal(100.50)


def test_create_multiple_expenses_for_same_user(client, auth_user):
    expense_1 = create_expense(client, auth_user, amount=100)
    expense_2 = create_expense(client, auth_user, amount=200)
    expense_3 = create_expense(client, auth_user, amount=300)

    ids = {
        expense_1["id"],
        expense_2["id"],
        expense_3["id"],
    }

    assert len(ids) == 3

    response = client.get(
        EXPENSE_URL,
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
def test_create_expense_invalid_amount(client, auth_user, amount):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_missing_amount(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_with_maximum_valid_amount(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 9999999999.99,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert float(data["amount"]) == 9999999999.99


def test_create_expense_with_high_precision_amount_returns_422(
    client,
    auth_user,
):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100.123456789,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# POST - Date Validation
# ============================================================

def test_create_expense_valid_date(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201


def test_create_expense_date_is_trimmed(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": " 2026-09-01 ",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["date"] == "2026-09-01"


@pytest.mark.parametrize(
    "date_value",
    ["01-09-2026", "2026-02-30", "", "     ", None, 12345],
)
def test_create_expense_invalid_date(client, auth_user, date_value):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": date_value,
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_missing_date(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# POST - Category Validation
# ============================================================

def test_create_expense_category_is_trimmed(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "   Food   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["category"] == "Food"


@pytest.mark.parametrize(
    "category",
    ["", "     ", None, 123],
)
def test_create_expense_invalid_category(client, auth_user, category):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": category,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_missing_category(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "category, expected_status",
    [
        ("a" * 100, 201),
        ("a" * 101, 422),
        ("सैलरी", 201),
        ("Travel & Consulting!", 201),
    ],
)
def test_create_expense_category_boundaries_and_characters(
    client,
    auth_user,
    category,
    expected_status,
):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": category,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


# ============================================================
# POST - Description Validation
# ============================================================

def test_create_expense_description_is_trimmed(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
            "description": "   Monthly Food   ",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == "Monthly Food"


def test_create_expense_whitespace_description_becomes_empty(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
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
def test_create_expense_description_validation(
    client,
    auth_user,
    description,
    expected_status,
):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
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
def test_create_expense_rejects_extra_fields(
    client,
    auth_user,
    extra_field,
):
    payload = {
        "amount": 5000,
        "date": "2026-09-01",
        "category": "Food",
    }
    payload.update(extra_field)

    response = client.post(
        EXPENSE_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# Authentication Tests
# ============================================================

def test_create_expense_without_token(client):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
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
def test_create_expense_with_invalid_or_wrong_auth_scheme(client, headers):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=headers,
    )

    assert response.status_code == 401


def test_create_expense_with_expired_token(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
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
        EXPENSE_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/expense
# ============================================================

def test_get_expenses_empty_collection(client, auth_user):
    response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_one_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == expense["id"]


def test_get_multiple_expenses(client, auth_user):
    expense_1 = create_expense(client, auth_user, amount=100)
    expense_2 = create_expense(client, auth_user, amount=200)

    response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = {expense["id"] for expense in response.json()}

    assert ids == {expense_1["id"], expense_2["id"]}


def test_get_expenses_response_contract(client, auth_user):
    create_expense(client, auth_user)

    response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    expense = response.json()[0]

    assert set(expense.keys()) == {
        "id",
        "icon",
        "amount",
        "date",
        "category",
        "description",
        "created_at",
        "updated_at",
    }

    assert isinstance(expense["id"], int)
    assert isinstance(expense["icon"], str)

    # Decimal values are serialized as strings in the API response.
    assert isinstance(expense["amount"], str)

    # Verify that the returned string is a valid Decimal value.
    assert Decimal(expense["amount"]) == Decimal("100.00")

    assert isinstance(expense["date"], str)
    assert isinstance(expense["category"], str)
    assert isinstance(expense["description"], str)
    assert isinstance(expense["created_at"], str)
    assert isinstance(expense["updated_at"], str)


def test_get_expenses_ordered_by_date_desc_and_id_desc(
    client,
    auth_user,
):
    expense_1 = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
    )
    expense_2 = create_expense(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
    )
    expense_3 = create_expense(
        client,
        auth_user,
        amount=300,
        date="2026-09-02",
    )

    response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    ids = [expense["id"] for expense in response.json()]

    assert ids == [
        expense_3["id"],
        expense_2["id"],
        expense_1["id"],
    ]


def test_get_all_user_isolation(client, auth_user, second_auth_user):
    expense_a = create_expense(
        client,
        auth_user,
        category="User A Expense",
    )
    expense_b = create_expense(
        client,
        second_auth_user,
        category="User B Expense",
    )

    response_a = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )
    response_b = client.get(
        EXPENSE_URL,
        headers=second_auth_user["headers"],
    )

    ids_a = {expense["id"] for expense in response_a.json()}
    ids_b = {expense["id"] for expense in response_b.json()}

    assert expense_a["id"] in ids_a
    assert expense_b["id"] not in ids_a

    assert expense_b["id"] in ids_b
    assert expense_a["id"] not in ids_b


def test_get_expenses_without_token(client):
    response = client.get(EXPENSE_URL)

    assert response.status_code == 401


def test_get_expenses_with_invalid_token(client):
    response = client.get(
        EXPENSE_URL,
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_get_expenses_with_expired_token(client, auth_user):
    response = client.get(
        EXPENSE_URL,
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# GET /api/v1/expense/{expense_id}
# ============================================================

def test_get_expense_by_id(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data == expense


def test_get_correct_expense_when_multiple_exist(client, auth_user):
    expense_1 = create_expense(
        client,
        auth_user,
        category="Food",
    )
    expense_2 = create_expense(
        client,
        auth_user,
        category="Bonus",
    )

    response = client.get(
        f"{EXPENSE_URL}/{expense_2['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["id"] == expense_2["id"]
    assert response.json()["id"] != expense_1["id"]


@pytest.mark.parametrize(
    "expense_id",
    [999999, 999999999],
)
def test_get_non_existing_expense(client, auth_user, expense_id):
    response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_get_another_users_expense(
    client,
    auth_user,
    second_auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404


def test_owner_can_get_own_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "expense_id",
    ["abc", "1.5"],
)
def test_get_expense_invalid_path_id(client, auth_user, expense_id):
    response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "expense_id",
    [-1, 0],
)
def test_get_expense_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    expense_id,
):
    # Current route has no Path(gt=0), so service lookup returns 404.
    response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_get_expense_by_id_without_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.get(f"{EXPENSE_URL}/{expense['id']}")

    assert response.status_code == 401


# ============================================================
# PATCH /api/v1/expense/{expense_id} - Success Cases
# ============================================================

def test_patch_amount_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Monthly",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 500},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["amount"]) == Decimal(500)
    assert data["date"] == "2026-09-01"
    assert data["category"] == "Food"
    assert data["description"] == "Monthly"


def test_patch_date_only(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"date": "2026-09-05"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-09-05"


def test_patch_category_only(client, auth_user):
    expense = create_expense(client, auth_user, category="Food")

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": "Bonus"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Bonus"


def test_patch_description_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"description": "New description"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "New description"


def test_patch_amount_and_date(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 500,
            "date": "2026-09-10",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert Decimal(data["amount"]) == Decimal(500)
    assert data["date"] == "2026-09-10"


def test_patch_amount_and_category(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 500,
            "category": "Travel",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert Decimal(data["amount"]) == Decimal(500)
    assert data["category"] == "Travel"


def test_patch_all_fields(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Old",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 500,
            "date": "2026-09-10",
            "category": "Bonus",
            "description": "New",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert Decimal(data["amount"]) == Decimal(500)
    assert data["date"] == "2026-09-10"
    assert data["category"] == "Bonus"
    assert data["description"] == "New"


def test_patch_partial_update_preserves_unspecified_fields(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Monthly",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": "Bonus"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["amount"]) == Decimal(100)
    assert data["date"] == "2026-09-01"
    assert data["category"] == "Bonus"
    assert data["description"] == "Monthly"


# ============================================================
# PATCH - Empty Request
# ============================================================

def test_patch_empty_body(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "At least one field is required to update the expense"
    )


def test_patch_missing_body(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
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
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": amount},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_expense_with_maximum_valid_amount(
    client,
    auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 9_999_999_999.99,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(str(data["amount"])) == Decimal("9999999999.99")


def test_patch_expense_with_high_precision_amount_returns_422(
    client,
    auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 100.123456789,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Date Validation
# ============================================================

def test_patch_date_is_trimmed(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
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
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"date": date_value},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Category Validation
# ============================================================

def test_patch_category_is_trimmed(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": "  Bonus  "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Bonus"


@pytest.mark.parametrize(
    "category",
    ["", "   ", None, 123, "a" * 101],
)
def test_patch_invalid_category(client, auth_user, category):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": category},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_category_exactly_100_characters(client, auth_user):
    expense = create_expense(client, auth_user)

    category = "a" * 100

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": category},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["category"] == category


# ============================================================
# PATCH - Description Validation
# ============================================================

def test_patch_empty_description(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"description": ""},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == ""


def test_patch_whitespace_description_is_trimmed(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"description": "   New description   "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "New description"


def test_patch_whitespace_only_description_becomes_empty(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        description="Old description",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
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
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
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
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
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
        {"category": "Food"},
        {"description": "Monthly expense"},
        {
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
            "description": "Monthly expense",
        },
    ],
)
def test_patch_no_actual_change_returns_400(
    client,
    auth_user,
    payload,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Monthly expense",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "No changes detected in the expense"
    )


def test_patch_some_unchanged_and_one_changed_succeeds(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=5000,
        category="Food",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 5000,
            "category": "Bonus",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert Decimal(data["amount"]) == Decimal(5000)
    assert data["category"] == "Bonus"


def test_patch_whitespace_normalized_same_value_returns_400(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        category="Food",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"category": " Food "},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


# ============================================================
# PATCH - Recategory / Authorization / Authentication
# ============================================================

@pytest.mark.parametrize(
    "expense_id",
    [999999, 999999999],
)
def test_patch_non_existing_expense(client, auth_user, expense_id):
    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}",
        json={"amount": 500},
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_update_another_users_expense(
    client,
    auth_user,
    second_auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Monthly",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 999},
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert Decimal(get_response.json()["amount"]) == Decimal(100)
    assert get_response.json()["date"] == "2026-09-01"
    assert get_response.json()["category"] == "Food"
    assert get_response.json()["description"] == "Monthly"


def test_owner_can_update_own_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200


def test_patch_invalid_id(client, auth_user):
    response = client.patch(
        f"{EXPENSE_URL}/abc",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_without_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 200},
    )

    assert response.status_code == 401


def test_patch_with_invalid_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 200},
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_patch_with_expired_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 200},
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# DELETE /api/v1/expense/{expense_id}
# ============================================================

def test_delete_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_expense_verifies_deletion(client, auth_user):
    expense = create_expense(client, auth_user)

    delete_response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 404


def test_delete_one_expense_does_not_affect_others(client, auth_user):
    expense_a = create_expense(client, auth_user, category="A")
    expense_b = create_expense(client, auth_user, category="B")
    expense_c = create_expense(client, auth_user, category="C")

    response = client.delete(
        f"{EXPENSE_URL}/{expense_b['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204

    assert client.get(
        f"{EXPENSE_URL}/{expense_a['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{EXPENSE_URL}/{expense_b['id']}",
        headers=auth_user["headers"],
    ).status_code == 404

    assert client.get(
        f"{EXPENSE_URL}/{expense_c['id']}",
        headers=auth_user["headers"],
    ).status_code == 200


@pytest.mark.parametrize(
    "expense_id",
    [999999, 999999999],
)
def test_delete_non_existing_expense(client, auth_user, expense_id):
    response = client.delete(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_same_expense_twice(client, auth_user):
    expense = create_expense(client, auth_user)

    first_response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    second_response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert first_response.status_code == 204
    assert second_response.status_code == 404


def test_user_cannot_delete_another_users_expense(
    client,
    auth_user,
    second_auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert owner_response.status_code == 200


def test_owner_can_delete_own_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "expense_id",
    ["abc", "1.5"],
)
def test_delete_invalid_path_id(client, auth_user, expense_id):
    response = client.delete(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "expense_id",
    [-1, 0],
)
def test_delete_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    expense_id,
):
    response = client.delete(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_without_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
    )

    assert response.status_code == 401


def test_delete_with_invalid_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_delete_with_expired_token(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code == 401


# ============================================================
# Database Integrity / Regression
# ============================================================

def test_invalid_create_does_not_create_expense(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": -100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    get_response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_invalid_patch_does_not_modify_expense(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
        description="Monthly",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": -500},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    data = get_response.json()

    assert Decimal(data["amount"]) == Decimal(100)
    assert data["date"] == "2026-09-01"
    assert data["category"] == "Food"
    assert data["description"] == "Monthly"


def test_failed_delete_does_not_delete_other_expenses(
    client,
    auth_user,
):
    expense_1 = create_expense(client, auth_user, category="Expense 1")
    expense_2 = create_expense(client, auth_user, category="Expense 2")

    response = client.delete(
        f"{EXPENSE_URL}/999999",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    assert client.get(
        f"{EXPENSE_URL}/{expense_1['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{EXPENSE_URL}/{expense_2['id']}",
        headers=auth_user["headers"],
    ).status_code == 200


def test_updating_one_expense_does_not_modify_another(
    client,
    auth_user,
):
    expense_1 = create_expense(
        client,
        auth_user,
        amount=100,
        category="Food",
    )
    expense_2 = create_expense(
        client,
        auth_user,
        amount=200,
        category="Bonus",
    )

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense_1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_expense_2 = client.get(
        f"{EXPENSE_URL}/{expense_2['id']}",
        headers=auth_user["headers"],
    )

    assert get_expense_2.status_code == 200
    assert Decimal(get_expense_2.json()["amount"]) == Decimal(200)
    assert get_expense_2.json()["category"] == "Bonus"


# ============================================================
# Full CRUD Lifecycle
# ============================================================

def test_complete_expense_crud_lifecycle(client, auth_user):
    # CREATE
    create_response = client.post(
        EXPENSE_URL,
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
            "description": "Initial",
        },
        headers=auth_user["headers"],
    )

    assert create_response.status_code == 201

    expense = create_response.json()
    expense_id = expense["id"]

    # GET BY ID
    get_response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Initial"

    # GET ALL
    get_all_response = client.get(
        EXPENSE_URL,
        headers=auth_user["headers"],
    )

    assert get_all_response.status_code == 200
    assert expense_id in {
        item["id"]
        for item in get_all_response.json()
    }

    # UPDATE
    update_response = client.patch(
        f"{EXPENSE_URL}/{expense_id}",
        json={
            "amount": 500,
            "description": "Updated",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200
    assert Decimal(update_response.json()["amount"]) == Decimal(500)
    assert update_response.json()["description"] == "Updated"

    # GET UPDATED
    get_updated_response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert get_updated_response.status_code == 200
    assert Decimal(get_updated_response.json()["amount"]) == Decimal(500)

    # DELETE
    delete_response = client.delete(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    # FINAL GET
    final_get_response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
        headers=auth_user["headers"],
    )

    assert final_get_response.status_code == 404


# ============================================================
# Multi-User Integration
# ============================================================

def test_complete_multi_user_expense_isolation(
    client,
    auth_user,
    second_auth_user,
):
    expense_a1 = create_expense(
        client,
        auth_user,
        category="A1",
    )
    expense_a2 = create_expense(
        client,
        auth_user,
        category="A2",
    )

    expense_b1 = create_expense(
        client,
        second_auth_user,
        category="B1",
    )
    expense_b2 = create_expense(
        client,
        second_auth_user,
        category="B2",
    )

    # Owners can access their own records.
    assert client.get(
        f"{EXPENSE_URL}/{expense_a1['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{EXPENSE_URL}/{expense_b1['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 200

    # Cross-user GET is blocked.
    assert client.get(
        f"{EXPENSE_URL}/{expense_b1['id']}",
        headers=auth_user["headers"],
    ).status_code == 404

    assert client.get(
        f"{EXPENSE_URL}/{expense_a1['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 404

    # Cross-user UPDATE is blocked.
    assert client.patch(
        f"{EXPENSE_URL}/{expense_b1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    ).status_code == 404

    # Cross-user DELETE is blocked.
    assert client.delete(
        f"{EXPENSE_URL}/{expense_a2['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 404

    # Verify records remain accessible to owners.
    assert client.get(
        f"{EXPENSE_URL}/{expense_a2['id']}",
        headers=auth_user["headers"],
    ).status_code == 200

    assert client.get(
        f"{EXPENSE_URL}/{expense_b2['id']}",
        headers=second_auth_user["headers"],
    ).status_code == 200


# ============================================================
# Regression Scenarios
# ============================================================

def test_multiple_sequential_creates_have_unique_ids(
    client,
    auth_user,
):
    expenses = [
        create_expense(
            client,
            auth_user,
            amount=100 + index,
        )
        for index in range(5)
    ]

    ids = [expense["id"] for expense in expenses]

    assert len(ids) == len(set(ids))


def test_update_expense_multiple_times(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    for amount in [200, 300]:
        response = client.patch(
            f"{EXPENSE_URL}/{expense['id']}",
            json={"amount": amount},
            headers=auth_user["headers"],
        )

        assert response.status_code == 200

    final_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert final_response.status_code == 200
    assert Decimal(final_response.json()["amount"]) == Decimal(300)


def test_delete_after_update(client, auth_user):
    expense = create_expense(client, auth_user)

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 500},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    delete_response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204


def test_valid_update_after_failed_update(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    invalid_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": -100},
        headers=auth_user["headers"],
    )

    assert invalid_response.status_code == 422

    valid_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": 200},
        headers=auth_user["headers"],
    )

    assert valid_response.status_code == 200
    assert Decimal(valid_response.json()["amount"]) == Decimal(200)


def test_same_date_records_remain_independent(client, auth_user):
    expense_1 = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="Food",
    )
    expense_2 = create_expense(
        client,
        auth_user,
        amount=200,
        date="2026-09-01",
        category="Bonus",
    )

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense_1['id']}",
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    expense_2_response = client.get(
        f"{EXPENSE_URL}/{expense_2['id']}",
        headers=auth_user["headers"],
    )

    assert expense_2_response.status_code == 200
    assert Decimal(expense_2_response.json()["amount"]) == Decimal(200)


def test_same_category_records_remain_independent(client, auth_user):
    expense_1 = create_expense(
        client,
        auth_user,
        amount=100,
        category="Food",
    )
    expense_2 = create_expense(
        client,
        auth_user,
        amount=200,
        category="Food",
    )

    delete_response = client.delete(
        f"{EXPENSE_URL}/{expense_1['id']}",
        headers=auth_user["headers"],
    )

    assert delete_response.status_code == 204

    remaining_response = client.get(
        f"{EXPENSE_URL}/{expense_2['id']}",
        headers=auth_user["headers"],
    )

    assert remaining_response.status_code == 200
    assert Decimal(remaining_response.json()["amount"]) == Decimal(200)


# ============================================================
# MISSING GET INCOME BY ID AUTHENTICATION TESTS
# ============================================================


def test_get_expense_by_id_with_invalid_token(
    client,
    auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers={
            "Authorization": "Bearer invalid.token.value",
        },
    )

    assert response.status_code == 401


def test_get_expense_by_id_with_expired_token(
    client,
    auth_user,
):
    expense = create_expense(client, auth_user)

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=expired_headers(
            auth_user["user"]["id"]
        ),
    )

    assert response.status_code == 401


# ============================================================
# GET INCOME BY ID RESPONSE CONTRACT
# ============================================================


def test_get_expense_by_id_response_contract(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
    )

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "icon",
        "amount",
        "date",
        "category",
        "description",
        "created_at",
        "updated_at"
    }

    assert isinstance(data["id"], int)
    assert isinstance(data["icon"], str)
    assert isinstance(data["amount"], str)
    assert Decimal(data["amount"]) == Decimal("100.00")
    assert isinstance(data["date"], str)
    assert isinstance(data["category"], str)
    assert isinstance(data["description"], str)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


# ============================================================
# PATCH INVALID ID TESTS
# ============================================================


@pytest.mark.parametrize(
    "expense_id",
    [
        "abc",
        "1.5",
    ],
)
def test_patch_invalid_id(
    client,
    auth_user,
    expense_id,
):
    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "expense_id",
    [
        -1,
        0,
    ],
)
def test_patch_zero_and_negative_id_current_behavior(
    client,
    auth_user,
    expense_id,
):
    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}",
        json={
            "amount": 500,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


# ============================================================
# PATCH RESPONSE CONTRACT
# ============================================================


def test_patch_expense_response_contract(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 500,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "icon",
        "amount",
        "date",
        "category",
        "description",
        "created_at",
        "updated_at"
    }

    assert isinstance(data["id"], int)
    assert isinstance(data["icon"], str)
    assert isinstance(data["amount"], str)
    assert isinstance(data["date"], str)
    assert isinstance(data["category"], str)
    assert isinstance(data["description"], str)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

    assert Decimal(data["amount"]) == Decimal("500.00")

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
def test_delete_expense_invalid_authentication(
    client,
    auth_user,
    headers,
):
    expense = create_expense(
        client,
        auth_user,
    )

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=headers,
    )

    assert response.status_code == 401


# ============================================================
# CREATE LARGE AND HIGH-PRECISION AMOUNT TESTS
# ============================================================


@pytest.mark.parametrize(
    "amount",
    [
        999999999999999,
        100.123456789,
    ],
)
def test_create_expense_with_very_large_amount(
    client,
    auth_user,
    amount,
):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"amount": amount},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_with_high_precision_amount(
    client,
    auth_user,
):
    amount = 100.123456789

    response = client.post(
        EXPENSE_URL,
        json={
            "amount": amount,
            "date": "2026-09-01",
            "category": "Travel",
            "description": "High precision amount",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data
    assert any(
        error["loc"] == ["body", "amount"]
        for error in data["detail"]
    )


# ============================================================
# PATCH LARGE AND HIGH-PRECISION AMOUNT TESTS
# ============================================================


def test_patch_expense_with_very_large_amount(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    large_amount = 999999999999999

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": large_amount,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data
    assert any(
        error["loc"] == ["body", "amount"]
        for error in data["detail"]
    )

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert float(get_response.json()["amount"]) == 100


def test_patch_expense_with_high_precision_amount(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    amount = 100.123456789

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": amount,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data

    assert any(
        error["loc"] == ["body", "amount"]
        for error in data["detail"]
    )

    # Verify the original value was not changed
    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200
    assert float(get_response.json()["amount"]) == 100


# ============================================================
# STRONGER MULTI-USER UPDATE ISOLATION TEST
# ============================================================


def test_user_cannot_update_another_users_expense_and_data_remains_unchanged(
    client,
    auth_user,
    second_auth_user,
):
    expense = create_expense(
        client,
        second_auth_user,
        amount=500,
        category="Second User Food",
        description="Original description",
    )

    expense_before_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=second_auth_user["headers"],
    )

    assert expense_before_response.status_code == 200

    expense_before = expense_before_response.json()

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 999,
            "category": "Hacked Category",
            "description": "Hacked Description",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    expense_after_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=second_auth_user["headers"],
    )

    assert expense_after_response.status_code == 200

    expense_after = expense_after_response.json()

    assert expense_after["id"] == expense_before["id"]
    assert expense_after["amount"] == expense_before["amount"]
    assert expense_after["date"] == expense_before["date"]
    assert expense_after["category"] == expense_before["category"]
    assert expense_after["description"] == expense_before["description"]


# ============================================================
# STRONGER MULTI-USER DELETE ISOLATION TEST
# ============================================================


def test_user_cannot_delete_another_users_expense_and_record_remains(
    client,
    auth_user,
    second_auth_user,
):
    expense = create_expense(
        client,
        second_auth_user,
        amount=500,
        category="Second User Food",
    )

    response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=second_auth_user["headers"],
    )

    assert owner_response.status_code == 200

    data = owner_response.json()

    assert data["id"] == expense["id"]
    assert data["amount"] == expense["amount"]
    assert data["category"] == expense["category"]

# ============================================================
# ICON FIELD - UPDATED EXPENSE SCHEMA COVERAGE
# These tests are intentionally additive: no existing expense-route
# test has been removed. They cover the new shared-schema/model field.
# ============================================================


def test_create_expense_with_icon(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": "🍔",
            "amount": 50000,
            "date": "2026-09-01",
            "category": "Food",
            "description": "Monthly expense",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["icon"] == "🍔"


def test_create_expense_without_icon_uses_default_empty_string(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "amount": 50000,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["icon"] == ""


def test_create_expense_with_empty_icon(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": "",
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["icon"] == ""


def test_create_expense_with_whitespace_icon_is_allowed_and_preserved(client, auth_user):
    icon = "   "
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": icon,
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["icon"] == icon


def test_create_expense_with_icon_at_max_length(client, auth_user):
    icon = "i" * 100
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": icon,
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["icon"] == icon


def test_create_expense_with_icon_over_max_length_is_rejected(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": "i" * 101,
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_with_null_icon_is_rejected(client, auth_user):
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": None,
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize("icon", [123, 12.5, True, [], {}, ["food"]])
def test_create_expense_with_invalid_icon_type_is_rejected(client, auth_user, icon):
    response = client.post(
        EXPENSE_URL,
        json={
            "icon": icon,
            "amount": 100,
            "date": "2026-09-01",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_get_expenses_returns_icon_for_each_expense(client, auth_user):
    first = create_expense(client, auth_user, icon="🍔", amount=100)
    second = create_expense(client, auth_user, icon="🚕", amount=200)

    response = client.get(EXPENSE_URL, headers=auth_user["headers"])

    assert response.status_code == 200
    expenses = {item["id"]: item for item in response.json()}
    assert expenses[first["id"]]["icon"] == "🍔"
    assert expenses[second["id"]]["icon"] == "🚕"


def test_get_expense_by_id_returns_icon(client, auth_user):
    expense = create_expense(client, auth_user, icon="🏠")

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["icon"] == "🏠"


def test_patch_expense_icon_only(client, auth_user):
    expense = create_expense(client, auth_user, icon="🍔")

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": "🚕"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["icon"] == "🚕"
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["category"] == expense["category"]
    assert data["description"] == expense["description"]


def test_patch_expense_icon_to_empty_string(client, auth_user):
    expense = create_expense(client, auth_user, icon="🍔")

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": ""},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["icon"] == ""


def test_patch_expense_icon_at_max_length(client, auth_user):
    expense = create_expense(client, auth_user)
    icon = "x" * 100

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": icon},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["icon"] == icon


def test_patch_expense_icon_over_max_length_is_rejected(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": "x" * 101},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_expense_icon_null_is_rejected(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": None},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize("icon", [123, 12.5, True, [], {}, ["food"]])
def test_patch_expense_invalid_icon_type_is_rejected(client, auth_user, icon):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": icon},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_patch_expense_icon_does_not_modify_other_fields(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        icon="A",
        amount=321.45,
        date="2026-08-20",
        category="Travel",
        description="Original description",
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": "B"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["icon"] == "B"
    assert Decimal(data["amount"]) == Decimal("321.45")
    assert data["date"] == "2026-08-20"
    assert data["category"] == "Travel"
    assert data["description"] == "Original description"


def test_patch_expense_all_fields_including_icon(client, auth_user):
    expense = create_expense(client, auth_user, icon="A")

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "icon": "🚗",
            "amount": 999.99,
            "date": "2026-09-12",
            "category": "Transport",
            "description": "Updated expense",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["icon"] == "🚗"
    assert Decimal(data["amount"]) == Decimal("999.99")
    assert data["date"] == "2026-09-12"
    assert data["category"] == "Transport"
    assert data["description"] == "Updated expense"


def test_expense_icon_persists_through_create_get_update_and_list(client, auth_user):
    created = create_expense(client, auth_user, icon="🛒")

    get_response = client.get(
        f"{EXPENSE_URL}/{created['id']}",
        headers=auth_user["headers"],
    )
    assert get_response.status_code == 200
    assert get_response.json()["icon"] == "🛒"

    update_response = client.patch(
        f"{EXPENSE_URL}/{created['id']}",
        json={"icon": "🧾"},
        headers=auth_user["headers"],
    )
    assert update_response.status_code == 200
    assert update_response.json()["icon"] == "🧾"

    list_response = client.get(EXPENSE_URL, headers=auth_user["headers"])
    assert list_response.status_code == 200
    item = next(x for x in list_response.json() if x["id"] == created["id"])
    assert item["icon"] == "🧾"


def test_delete_expense_after_icon_update(client, auth_user):
    expense = create_expense(client, auth_user, icon="🍔")

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={"icon": "🚕"},
        headers=auth_user["headers"],
    )
    assert update_response.status_code == 200

    delete_response = client.delete(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )
    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )
    assert get_response.status_code == 404



def test_expense_created_at_is_set(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
    )

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["created_at"] is not None

    created_at = datetime.fromisoformat(
        data["created_at"].replace("Z", "+00:00")
    )

    assert isinstance(created_at, datetime)
    assert created_at.tzinfo is not None
    assert created_at.utcoffset() is not None


def test_expense_updated_at_is_set_on_creation(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
    )

    response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["updated_at"] is not None

    updated_at = datetime.fromisoformat(
        data["updated_at"].replace("Z", "+00:00")
    )

    assert isinstance(updated_at, datetime)
    assert updated_at.tzinfo is not None
    assert updated_at.utcoffset() is not None


def test_expense_created_at_remains_same_after_update(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    original_created_at = get_response.json()["created_at"]

    time.sleep(0.01)

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    updated_expense = get_response.json()

    assert updated_expense["created_at"] == original_created_at


def test_expense_updated_at_changes_after_update(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
    )

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    original_updated_at = datetime.fromisoformat(
        get_response.json()["updated_at"].replace("Z", "+00:00")
    )

    time.sleep(0.01)

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    updated_at = datetime.fromisoformat(
        get_response.json()["updated_at"].replace("Z", "+00:00")
    )

    assert updated_at > original_updated_at


def test_expense_updated_at_changes_on_multiple_updates(
    client,
    auth_user,
):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        category="Food",
    )

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    initial_data = get_response.json()

    original_created_at = initial_data["created_at"]

    updated_at_1 = datetime.fromisoformat(
        initial_data["updated_at"].replace("Z", "+00:00")
    )

    time.sleep(0.01)

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "amount": 200,
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    data_after_first_update = get_response.json()

    updated_at_2 = datetime.fromisoformat(
        data_after_first_update["updated_at"].replace("Z", "+00:00")
    )

    time.sleep(0.01)

    update_response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}",
        json={
            "category": "Travel",
        },
        headers=auth_user["headers"],
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"{EXPENSE_URL}/{expense['id']}",
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 200

    data_after_second_update = get_response.json()

    updated_at_3 = datetime.fromisoformat(
        data_after_second_update["updated_at"].replace("Z", "+00:00")
    )

    assert data_after_second_update["created_at"] == original_created_at

    assert updated_at_1 < updated_at_2 < updated_at_3