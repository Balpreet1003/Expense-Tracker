import pytest
import jwt
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from app.features.auth.utils.jwt import SECRET_KEY, ALGORITHM


TRANSACTION_URL = "/api/v1/transaction"
TRANSACTIONS_URL = "/api/v1/transactions"


# ============================================================
# Authentication Helpers
# ============================================================

def create_user_and_get_token(
    client,
    email="transaction-test@example.com",
    full_name="Transaction Test User",
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
        email="transaction-second@example.com",
        full_name="Second Transaction User",
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

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# Transaction Helpers
# ============================================================

def income_payload(**overrides):
    payload = {
        "type": "income",
        "icon": "",
        "amount": 100.0,
        "date": "2026-09-01",
        "source": "Salary",
        "description": "Monthly income",
    }
    payload.update(overrides)
    return payload


def expense_payload(**overrides):
    payload = {
        "type": "expense",
        "icon": "",
        "amount": 100.0,
        "date": "2026-09-01",
        "category": "Food",
        "description": "Monthly expense",
    }
    payload.update(overrides)
    return payload


def create_transaction(client, auth_user, payload):
    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text
    return response.json()


def create_income_transaction(client, auth_user, **overrides):
    return create_transaction(
        client,
        auth_user,
        income_payload(**overrides),
    )


def create_expense_transaction(client, auth_user, **overrides):
    return create_transaction(
        client,
        auth_user,
        expense_payload(**overrides),
    )


def transaction_url(transaction_type, transaction_id):
    return f"{TRANSACTION_URL}/{transaction_type}/{transaction_id}"


# ============================================================
# 1. CREATE TRANSACTION - SUCCESS CASES
# ============================================================

def test_create_income_transaction_success(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(
            amount=50000,
            date="2026-09-01",
            source="Salary",
            description="Monthly salary",
        ),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "icon",
        "amount",
        "date",
        "source",
        "description",
        "created_at",
        "updated_at",
        "type",
    }
    assert isinstance(data["id"], int)
    assert Decimal(data["amount"]) == Decimal(50000)
    assert data["date"] == "2026-09-01"
    assert data["source"] == "Salary"
    assert data["description"] == "Monthly salary"
    assert data["type"] == "income"
    assert "category" not in data
    assert "user_id" not in data


def test_create_income_transaction_without_description(client, auth_user):
    payload = income_payload()
    payload.pop("description")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""
    assert response.json()["type"] == "income"


def test_create_income_transaction_with_empty_description(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(description=""),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_expense_transaction_success(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(
            amount=50000,
            date="2026-09-01",
            category="Food",
            description="Monthly expense",
        ),
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
        "type",
    }
    assert isinstance(data["id"], int)
    assert Decimal(data["amount"]) == Decimal(50000)
    assert data["date"] == "2026-09-01"
    assert data["category"] == "Food"
    assert data["description"] == "Monthly expense"
    assert data["type"] == "expense"
    assert "source" not in data
    assert "user_id" not in data


def test_create_expense_transaction_without_description(client, auth_user):
    payload = expense_payload()
    payload.pop("description")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""
    assert response.json()["type"] == "expense"


def test_create_expense_transaction_with_empty_description(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(description=""),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""


@pytest.mark.parametrize(
    "transaction_type",
    [
        "salary",
        "",
        " ",
        "INCOME",
        "Income",
        None,
        123,
        True,
        {},
        [],
    ],
)
def test_create_transaction_invalid_type(client, auth_user, transaction_type):
    payload = income_payload()
    payload["type"] = transaction_type

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_transaction_missing_type(client, auth_user):
    payload = income_payload()
    payload.pop("type")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# 2. CREATE INCOME VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [
        1,
        100,
        100.50,
        0.01,
        9999999999.99,
    ],
)
def test_create_income_valid_amounts(client, auth_user, amount):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(amount=amount),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert Decimal(data["amount"]) == Decimal(str(amount))


@pytest.mark.parametrize(
    "amount",
    [
        0.000001,          # More than 2 decimal places
        1.001,             # More than 2 decimal places
        999999999999999,   # More than 12 total digits
    ],
)
def test_create_income_invalid_amount_precision_or_digits(
    client,
    auth_user,
    amount,
):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(amount=amount),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422, response.text


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100.50,
        None,
        "abc",
        "",
        "   ",
        True,
        {},
        [],
    ],
)
def test_create_income_invalid_amounts(client, auth_user, amount):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(amount=amount),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_missing_amount(client, auth_user):
    payload = income_payload()
    payload.pop("amount")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-01",
        "2020-01-01",
        "2099-12-31",
    ],
)
def test_create_income_valid_dates(client, auth_user, value):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(date=value),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text


@pytest.mark.parametrize(
    "value",
    [
        "not-a-date",
        "2026-02-30",
        "",
        "   ",
        None,
        123,
        True,
        {},
        [],
    ],
)
def test_create_income_invalid_dates(client, auth_user, value):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(date=value),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_missing_date(client, auth_user):
    payload = income_payload()
    payload.pop("date")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_valid_source_is_trimmed(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(source="  Salary  "),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["source"] == "Salary"


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        None,
        123,
        True,
        {},
        [],
        "a" * 101,
    ],
)
def test_create_income_invalid_source(client, auth_user, source):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(source=source),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_missing_source(client, auth_user):
    payload = income_payload()
    payload.pop("source")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "description",
    [
        "",
        "Valid description",
        "   ",
        "  trimmed description  ",
        "收入 description 😀",
        "special !@#$%^&*()",
        "a" * 500,
    ],
)
def test_create_income_valid_description_values(client, auth_user, description):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(description=description),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text


@pytest.mark.parametrize(
    "description",
    [
        None,
        123,
        True,
        {},
        [],
        "a" * 501,
    ],
)
def test_create_income_invalid_description_values(client, auth_user, description):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(description=description),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# 3. CREATE EXPENSE VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "amount",
    [
        1,
        100,
        100.50,
        0.01,
        9999999999.99,
    ],
)
def test_create_expense_valid_amounts(client, auth_user, amount):

    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(amount=amount),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert Decimal(str(data["amount"])) == Decimal(str(amount))


@pytest.mark.parametrize(
    "amount",
    [
        0.000001,          # More than 2 decimal places
        1.001,             # More than 2 decimal places
        999999999999999,   # More than 12 total digits
    ],
)
def test_create_expense_invalid_amount_precision_or_digits(
    client,
    auth_user,
    amount,
):
    response = client.post(
    TRANSACTION_URL,
    json=expense_payload(amount=amount),
    headers=auth_user["headers"],
    )

    assert response.status_code == 422, response.text



@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100.50,
        None,
        "abc",
        "",
        "   ",
        True,
        {},
        [],
    ],
)
def test_create_expense_invalid_amounts(client, auth_user, amount):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(amount=amount),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "value",
    [
        "not-a-date",
        "2026-02-30",
        "",
        "   ",
        None,
        123,
        True,
        {},
        [],
    ],
)
def test_create_expense_invalid_dates(client, auth_user, value):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(date=value),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_valid_category_is_trimmed(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(category="  Food  "),
        headers=auth_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["category"] == "Food"


@pytest.mark.parametrize(
    "category",
    [
        "",
        "   ",
        None,
        123,
        True,
        {},
        [],
        "a" * 101,
    ],
)
def test_create_expense_invalid_category(client, auth_user, category):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(category=category),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "description",
    [
        None,
        123,
        True,
        {},
        [],
        "a" * 501,
    ],
)
def test_create_expense_invalid_description_values(client, auth_user, description):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(description=description),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# 4. CREATE CROSS-TYPE AND EXTRA FIELD TESTS
# ============================================================

def test_create_income_rejects_expense_field(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(category="Food"),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_rejects_income_field(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=expense_payload(source="Salary"),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_income_missing_source_with_category(client, auth_user):
    payload = income_payload(category="Food")
    payload.pop("source")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_create_expense_missing_category_with_source(client, auth_user):
    payload = expense_payload(source="Salary")
    payload.pop("category")

    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        income_payload(unknown_field="value"),
        expense_payload(unknown_field="value"),
        income_payload(
            unknown_field_1="value",
            unknown_field_2="value",
        ),
        expense_payload(
            unknown_nested={"value": "test"},
        ),
    ],
)
def test_create_transaction_rejects_extra_fields(client, auth_user, payload):
    response = client.post(
        TRANSACTION_URL,
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# 5. CREATE AUTHENTICATION AND OWNERSHIP
# ============================================================

@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
        {"Authorization": "invalid-header"},
    ],
)
def test_create_transaction_requires_valid_authentication(client, headers):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(),
        headers=headers,
    )

    assert response.status_code in (401, 403)


def test_create_transaction_rejects_expired_token(client, auth_user):
    response = client.post(
        TRANSACTION_URL,
        json=income_payload(),
        headers=expired_headers(auth_user["user"]["id"]),
    )

    assert response.status_code in (401, 403)


def test_create_transaction_is_owned_by_authenticated_user(
    client,
    auth_user,
    second_auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
        amount=123,
    )

    response = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    other_user_response = client.get(
        transaction_url("income", created["id"]),
        headers=second_auth_user["headers"],
    )

    assert other_user_response.status_code == 404


# ============================================================
# 6. GET ALL TRANSACTIONS
# ============================================================

def test_get_all_transactions_empty(client, auth_user):
    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_transactions_income_only(client, auth_user):
    income_1 = create_income_transaction(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
    )
    income_2 = create_income_transaction(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(item["type"] == "income" for item in data)
    assert {item["id"] for item in data} == {
        income_1["id"],
        income_2["id"],
    }


def test_get_all_transactions_expense_only(client, auth_user):
    expense_1 = create_expense_transaction(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
    )
    expense_2 = create_expense_transaction(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(item["type"] == "expense" for item in data)
    assert {item["id"] for item in data} == {
        expense_1["id"],
        expense_2["id"],
    }


def test_get_all_transactions_mixed(client, auth_user):
    income_1 = create_income_transaction(
        client,
        auth_user,
        date="2026-09-01",
    )
    expense_1 = create_expense_transaction(
        client,
        auth_user,
        date="2026-09-02",
    )
    income_2 = create_income_transaction(
        client,
        auth_user,
        date="2026-09-03",
    )
    expense_2 = create_expense_transaction(
        client,
        auth_user,
        date="2026-09-04",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 4
    assert {
        (item["type"], item["id"])
        for item in data
    } == {
        ("income", income_1["id"]),
        ("expense", expense_1["id"]),
        ("income", income_2["id"]),
        ("expense", expense_2["id"]),
    }


def test_get_all_transactions_sorted_by_date_descending(
    client,
    auth_user,
):
    create_income_transaction(
        client,
        auth_user,
        date="2026-09-01",
    )
    create_expense_transaction(
        client,
        auth_user,
        date="2026-09-10",
    )
    create_income_transaction(
        client,
        auth_user,
        date="2026-09-05",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    dates = [item["date"] for item in response.json()]

    assert dates == sorted(dates, reverse=True)


def test_get_all_transactions_same_date_is_deterministic(
    client,
    auth_user,
):
    income = create_income_transaction(
        client,
        auth_user,
        date="2026-09-10",
    )
    expense = create_expense_transaction(
        client,
        auth_user,
        date="2026-09-10",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(item["date"] == "2026-09-10" for item in data)

    # Current service sorts by (date, created_at) descending.
    expected = sorted(
        data,
        key=lambda item: (item["date"], item["created_at"]),
        reverse=True,
    )

    assert data == expected


def test_get_all_transactions_same_date_same_id_is_supported(
    client,
    auth_user,
):
    income = create_income_transaction(
        client,
        auth_user,
        date="2026-09-10",
    )
    expense = create_expense_transaction(
        client,
        auth_user,
        date="2026-09-10",
    )

    # Income and Expense tables have independent primary key sequences.
    assert income["type"] == "income"
    assert expense["type"] == "expense"

    assert income["date"] == "2026-09-10"
    assert expense["date"] == "2026-09-10"

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_all_transactions_user_isolation(
    client,
    auth_user,
    second_auth_user,
):
    own_income = create_income_transaction(client, auth_user)
    own_expense = create_expense_transaction(client, auth_user)

    create_income_transaction(
        client,
        second_auth_user,
        source="Other Salary",
    )
    create_expense_transaction(
        client,
        second_auth_user,
        category="Other Food",
    )

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    own_ids = {
        ("income", own_income["id"]),
        ("expense", own_expense["id"]),
    }

    actual_ids = {
        (item["type"], item["id"])
        for item in response.json()
    }

    assert actual_ids == own_ids


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
        {"Authorization": "invalid-header"},
    ],
)
def test_get_all_transactions_requires_authentication(client, headers):
    response = client.get(
        TRANSACTIONS_URL,
        headers=headers,
    )

    assert response.status_code in (401, 403)


# ============================================================
# 7. GET TRANSACTION BY ID
# ============================================================

def test_get_income_transaction_by_id(client, auth_user):
    created = create_income_transaction(
        client,
        auth_user,
        amount=1000,
        date="2026-09-05",
        source="Freelancing",
        description="Project payment",
    )

    response = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data == created
    assert data["type"] == "income"


def test_get_expense_transaction_by_id(client, auth_user):
    created = create_expense_transaction(
        client,
        auth_user,
        amount=500,
        date="2026-09-05",
        category="Travel",
        description="Cab fare",
    )

    response = client.get(
        transaction_url("expense", created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data == created
    assert data["type"] == "expense"


@pytest.mark.parametrize(
    "transaction_type",
    [
        "income",
        "expense",
    ],
)
def test_get_transaction_by_id_not_found(
    client,
    auth_user,
    transaction_type,
):
    response = client.get(
        transaction_url(transaction_type, 999999999),
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "transaction_id",
    [
        0,
        -1,
        "abc",
        "1.5",
        "999999999999999999999999999999",
    ],
)
def test_get_transaction_by_id_invalid_id(
    client,
    auth_user,
    transaction_id,
):
    response = client.get(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert response.status_code in (404, 422)


@pytest.mark.parametrize(
    "transaction_type",
    [
        "salary",
        "transfer",
        "INCOME",
        "Income",
        "expensee",
    ],
)
def test_get_transaction_by_id_invalid_type(
    client,
    auth_user,
    transaction_type,
):
    response = client.get(
        transaction_url(transaction_type, 1),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_get_transaction_by_id_ownership_isolation(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income_transaction(client, auth_user)
    expense = create_expense_transaction(client, auth_user)

    income_response = client.get(
        transaction_url("income", income["id"]),
        headers=second_auth_user["headers"],
    )
    expense_response = client.get(
        transaction_url("expense", expense["id"]),
        headers=second_auth_user["headers"],
    )

    assert income_response.status_code == 404
    assert expense_response.status_code == 404


# ============================================================
# 8. UPDATE TRANSACTION - SUCCESS CASES
# ============================================================

def test_update_income_amount_only(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert Decimal(response.json()["amount"]) == Decimal(999)
    assert response.json()["source"] == created["source"]


def test_update_income_date_only(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"date": "2026-09-10"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-09-10"


def test_update_income_source_only(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"source": "Freelancing"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Freelancing"


def test_update_income_description_only(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"description": "Updated"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated"


def test_update_income_multiple_fields(client, auth_user):
    created = create_income_transaction(client, auth_user)

    payload = {
        "amount": 1000,
        "date": "2026-09-10",
        "source": "Freelancing",
        "description": "Updated",
    }

    response = client.patch(
        transaction_url("income", created["id"]),
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


def test_update_expense_amount_only(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"amount": 999},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert Decimal(response.json()["amount"]) == Decimal(999)
    assert response.json()["category"] == created["category"]


def test_update_expense_date_only(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"date": "2026-09-10"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-09-10"


def test_update_expense_category_only(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"category": "Travel"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Travel"


def test_update_expense_description_only(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"description": "Updated"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated"


def test_update_expense_multiple_fields(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    payload = {
        "amount": 1000,
        "date": "2026-09-10",
        "category": "Travel",
        "description": "Updated",
    }

    response = client.patch(
        transaction_url("expense", created["id"]),
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


# ============================================================
# 9. UPDATE EMPTY / SAME / MIXED VALUES
# ============================================================

@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_update_transaction_empty_body(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user)

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "transaction_type, factory, field, value",
    [
        ("income", create_income_transaction, "amount", 100.0),
        ("income", create_income_transaction, "date", "2026-09-01"),
        ("income", create_income_transaction, "source", "Salary"),
        ("income", create_income_transaction, "description", "Monthly income"),
        ("expense", create_expense_transaction, "amount", 100.0),
        ("expense", create_expense_transaction, "date", "2026-09-01"),
        ("expense", create_expense_transaction, "category", "Food"),
        ("expense", create_expense_transaction, "description", "Monthly expense"),
    ],
)
def test_update_transaction_same_value_returns_400(
    client,
    auth_user,
    transaction_type,
    factory,
    field,
    value,
):
    created = factory(client, auth_user)

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={field: value},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


def test_update_income_mixed_same_and_changed_values(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={
            "amount": created["amount"],
            "description": "Updated",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["amount"] == created["amount"]
    assert response.json()["description"] == "Updated"


def test_update_expense_mixed_same_and_changed_values(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={
            "amount": created["amount"],
            "description": "Updated",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["amount"] == created["amount"]
    assert response.json()["description"] == "Updated"


def test_update_income_all_same_values_returns_400(client, auth_user):
    created = create_income_transaction(client, auth_user)

    payload = {
        "amount": created["amount"],
        "date": created["date"],
        "source": created["source"],
        "description": created["description"],
    }

    response = client.patch(
        transaction_url("income", created["id"]),
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


def test_update_expense_all_same_values_returns_400(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    payload = {
        "amount": created["amount"],
        "date": created["date"],
        "category": created["category"],
        "description": created["description"],
    }

    response = client.patch(
        transaction_url("expense", created["id"]),
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 400


# ============================================================
# 10. UPDATE VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "payload",
    [
        {"amount": 0},
        {"amount": -1},
        {"amount": None},
        {"amount": "abc"},
        {"amount": True},
        {"amount": {}},
        {"amount": []},
        {"date": None},
        {"date": ""},
        {"date": "   "},
        {"date": "invalid-date"},
        {"date": "2026-02-30"},
        {"date": {}},
        {"date": []},
        {"description": None},
        {"description": {}},
        {"description": []},
        {"description": "a" * 501},
    ],
)
def test_update_income_invalid_common_fields(
    client,
    auth_user,
    payload,
):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"amount": 0},
        {"amount": -1},
        {"amount": None},
        {"amount": "abc"},
        {"amount": True},
        {"amount": {}},
        {"amount": []},
        {"date": None},
        {"date": ""},
        {"date": "   "},
        {"date": "invalid-date"},
        {"date": "2026-02-30"},
        {"date": {}},
        {"date": []},
        {"description": None},
        {"description": {}},
        {"description": []},
        {"description": "a" * 501},
    ],
)
def test_update_expense_invalid_common_fields(
    client,
    auth_user,
    payload,
):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


# ============================================================
# 11. UPDATE CROSS-TYPE AND EXTRA FIELD REGRESSION TESTS
# ============================================================

def test_update_income_with_category_returns_422(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"category": "Food"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_update_expense_with_source_returns_422(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"source": "Salary"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_update_income_with_both_source_and_category_returns_422(
    client,
    auth_user,
):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={
            "source": "Freelancing",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_update_expense_with_both_source_and_category_returns_422(
    client,
    auth_user,
):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={
            "source": "Salary",
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_cross_type_invalid_update_does_not_partially_modify_income(
    client,
    auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
        amount=100,
    )

    response = client.patch(
        transaction_url("income", created["id"]),
        json={
            "amount": 999,
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    verify = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert verify.status_code == 200
    assert Decimal(verify.json()["amount"]) == Decimal(100)


def test_cross_type_invalid_update_does_not_partially_modify_expense(
    client,
    auth_user,
):
    created = create_expense_transaction(
        client,
        auth_user,
        amount=100,
    )

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={
            "amount": 999,
            "source": "Salary",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    verify = client.get(
        transaction_url("expense", created["id"]),
        headers=auth_user["headers"],
    )

    assert verify.status_code == 200
    assert Decimal(verify.json()["amount"]) == Decimal(100)


def test_update_transaction_rejects_extra_field(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"unknown_field": "value"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


def test_update_extra_field_does_not_partially_modify_database(
    client,
    auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
        amount=100,
    )

    response = client.patch(
        transaction_url("income", created["id"]),
        json={
            "amount": 999,
            "unknown_field": "value",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    verify = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert verify.status_code == 200
    assert Decimal(verify.json()["amount"]) == Decimal(100)


# ============================================================
# 12. UPDATE LENGTH AND STRING VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "value, expected_status",
    [
        ("a" * 100, 200),
        ("a" * 101, 422),
        ("", 422),
        ("   ", 422),
        ("  Salary  ", 400),
        ("收入 😀", 200),
        ("!@#$%^&*", 200),
        (None, 422),
    ],
)
def test_update_income_source_validation(
    client,
    auth_user,
    value,
    expected_status,
):
    created = create_income_transaction(client, auth_user)

    response = client.patch(
        transaction_url("income", created["id"]),
        json={"source": value},
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "value, expected_status",
    [
        ("a" * 100, 200),
        ("a" * 101, 422),
        ("", 422),
        ("   ", 422),
        ("  Food  ", 400),
        ("食品 😀", 200),
        ("!@#$%^&*", 200),
        (None, 422),
    ],
)
def test_update_expense_category_validation(
    client,
    auth_user,
    value,
    expected_status,
):
    created = create_expense_transaction(client, auth_user)

    response = client.patch(
        transaction_url("expense", created["id"]),
        json={"category": value},
        headers=auth_user["headers"],
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_update_description_max_length(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user)

    valid_response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"description": "a" * 500},
        headers=auth_user["headers"],
    )

    assert valid_response.status_code == 200

    invalid_response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"description": "a" * 501},
        headers=auth_user["headers"],
    )

    assert invalid_response.status_code == 422


# ============================================================
# 13. UPDATE ROUTE / NOT FOUND / OWNERSHIP / AUTH
# ============================================================

@pytest.mark.parametrize(
    "transaction_type",
    [
        "salary",
        "transfer",
        "Income",
        "INCOME",
        "Expense",
    ],
)
def test_update_invalid_transaction_type(
    client,
    auth_user,
    transaction_type,
):
    response = client.patch(
        transaction_url(transaction_type, 1),
        json={"amount": 100},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "transaction_id",
    [
        0,
        -1,
        "abc",
        "1.5",
    ],
)
def test_update_invalid_transaction_id(
    client,
    auth_user,
    transaction_id,
):
    response = client.patch(
        transaction_url("income", transaction_id),
        json={"amount": 100},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "transaction_type",
    [
        "income",
        "expense",
    ],
)
def test_update_transaction_not_found(
    client,
    auth_user,
    transaction_type,
):
    response = client.patch(
        transaction_url(transaction_type, 999999999),
        json={"amount": 100},
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_update_transaction_ownership_isolation(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income_transaction(
        client,
        auth_user,
        amount=100,
    )
    expense = create_expense_transaction(
        client,
        auth_user,
        amount=100,
    )

    income_response = client.patch(
        transaction_url("income", income["id"]),
        json={"amount": 999},
        headers=second_auth_user["headers"],
    )

    expense_response = client.patch(
        transaction_url("expense", expense["id"]),
        json={"amount": 999},
        headers=second_auth_user["headers"],
    )

    assert income_response.status_code == 404
    assert expense_response.status_code == 404

    verify_income = client.get(
        transaction_url("income", income["id"]),
        headers=auth_user["headers"],
    )
    verify_expense = client.get(
        transaction_url("expense", expense["id"]),
        headers=auth_user["headers"],
    )

    assert Decimal(verify_income.json()["amount"]) == Decimal(100)
    assert Decimal(verify_expense.json()["amount"]) == Decimal(100)


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
        {"Authorization": "invalid-header"},
    ],
)
def test_update_requires_authentication(client, headers):
    response = client.patch(
        transaction_url("income", 1),
        json={"amount": 100},
        headers=headers,
    )

    assert response.status_code in (401, 403)


# ============================================================
# 14. DELETE TRANSACTION
# ============================================================

def test_delete_income_transaction(client, auth_user):
    created = create_income_transaction(client, auth_user)

    response = client.delete(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 404

    get_all_response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert get_all_response.status_code == 200
    assert (
        ("income", created["id"])
        not in {
            (item["type"], item["id"])
            for item in get_all_response.json()
        }
    )


def test_delete_expense_transaction(client, auth_user):
    created = create_expense_transaction(client, auth_user)

    response = client.delete(
        transaction_url("expense", created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        transaction_url("expense", created["id"]),
        headers=auth_user["headers"],
    )

    assert get_response.status_code == 404


@pytest.mark.parametrize(
    "transaction_type",
    [
        "income",
        "expense",
    ],
)
def test_delete_transaction_not_found(
    client,
    auth_user,
    transaction_type,
):
    response = client.delete(
        transaction_url(transaction_type, 999999999),
        headers=auth_user["headers"],
    )

    assert response.status_code == 404


def test_delete_transaction_twice(client, auth_user):
    created = create_income_transaction(client, auth_user)

    first_response = client.delete(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert first_response.status_code == 204

    second_response = client.delete(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert second_response.status_code == 404


def test_delete_transaction_ownership_isolation(
    client,
    auth_user,
    second_auth_user,
):
    income = create_income_transaction(client, auth_user)
    expense = create_expense_transaction(client, auth_user)

    income_response = client.delete(
        transaction_url("income", income["id"]),
        headers=second_auth_user["headers"],
    )

    expense_response = client.delete(
        transaction_url("expense", expense["id"]),
        headers=second_auth_user["headers"],
    )

    assert income_response.status_code == 404
    assert expense_response.status_code == 404

    verify_income = client.get(
        transaction_url("income", income["id"]),
        headers=auth_user["headers"],
    )
    verify_expense = client.get(
        transaction_url("expense", expense["id"]),
        headers=auth_user["headers"],
    )

    assert verify_income.status_code == 200
    assert verify_expense.status_code == 200


@pytest.mark.parametrize(
    "transaction_type",
    [
        "salary",
        "transfer",
        "Income",
        "INCOME",
        "expensee",
    ],
)
def test_delete_invalid_transaction_type(
    client,
    auth_user,
    transaction_type,
):
    response = client.delete(
        transaction_url(transaction_type, 1),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "transaction_id",
    [
        0,
        -1,
        "abc",
        "1.5",
    ],
)
def test_delete_invalid_transaction_id(
    client,
    auth_user,
    transaction_id,
):
    response = client.delete(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
        {"Authorization": "invalid-header"},
    ],
)
def test_delete_requires_authentication(client, headers):
    response = client.delete(
        transaction_url("income", 1),
        headers=headers,
    )

    assert response.status_code in (401, 403)



# ============================================================
# 14A. UPDATED TRANSACTION SCHEMA: ICON + TIMESTAMPS
# ============================================================

@pytest.mark.parametrize(
    "factory, field_name",
    [
        (create_income_transaction, "source"),
        (create_expense_transaction, "category"),
    ],
)
def test_create_transaction_default_icon_and_timestamps(
    client,
    auth_user,
    factory,
    field_name,
):
    created = factory(client, auth_user)

    assert created["icon"] == ""
    assert created["created_at"] is not None
    assert created["updated_at"] is not None
    created_at = datetime.fromisoformat(
        created["created_at"].replace("Z", "+00:00")
    )
    updated_at = datetime.fromisoformat(
        created["updated_at"].replace("Z", "+00:00")
    )

    assert updated_at >= created_at


@pytest.mark.parametrize(
    "factory",
    [
        create_income_transaction,
        create_expense_transaction,
    ],
)
def test_create_transaction_custom_icon_is_returned_and_persisted(
    client,
    auth_user,
    factory,
):
    icon = "wallet-outline"

    created = factory(
        client,
        auth_user,
        icon=icon,
    )

    assert created["icon"] == icon

    response = client.get(
        transaction_url(created["type"], created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["icon"] == icon


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_create_transaction_icon_length_boundaries(
    client,
    auth_user,
    transaction_type,
    factory,
):
    for icon in ["", "i" * 100]:
        created = factory(client, auth_user, icon=icon)
        assert created["type"] == transaction_type
        assert created["icon"] == icon


@pytest.mark.parametrize(
    "transaction_type, payload_factory",
    [
        ("income", income_payload),
        ("expense", expense_payload),
    ],
)
@pytest.mark.parametrize(
    "icon",
    [
        "i" * 101,
        None,
        123,
        True,
        {},
        [],
    ],
)
def test_create_transaction_rejects_invalid_icon_values(
    client,
    auth_user,
    transaction_type,
    payload_factory,
    icon,
):
    response = client.post(
        TRANSACTION_URL,
        json=payload_factory(icon=icon),
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_update_transaction_icon_only(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user, icon="old-icon")

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"icon": "new-icon"},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["icon"] == "new-icon"


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
@pytest.mark.parametrize(
    "icon",
    [
        "i",
        "i" * 100,
    ],
)
def test_update_transaction_accepts_valid_icon_boundaries(
    client,
    auth_user,
    transaction_type,
    factory,
    icon,
):
    created = factory(client, auth_user)

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"icon": icon},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["icon"] == icon


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_update_transaction_rejects_empty_icon(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user)

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"icon": ""},
        headers=auth_user["headers"],
    )

    assert response.status_code == 400, response.text


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
@pytest.mark.parametrize(
    "icon",
    [
        None,
        "i" * 101,
        123,
        True,
        {},
        [],
    ],
)
def test_update_transaction_rejects_invalid_icon_values(
    client,
    auth_user,
    transaction_type,
    factory,
    icon,
):
    created = factory(client, auth_user)

    response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"icon": icon},
        headers=auth_user["headers"],
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_transaction_timestamps_are_immutable_through_response_contract(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user)
    transaction_id = created["id"]

    response = client.get(
        transaction_url(transaction_type, transaction_id),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert data["created_at"] == created["created_at"]
    assert data["updated_at"] == created["updated_at"]


@pytest.mark.parametrize(
    "transaction_type, factory, update_field, update_value",
    [
        ("income", create_income_transaction, "source", "Freelancing"),
        ("expense", create_expense_transaction, "category", "Travel"),
    ],
)
def test_update_transaction_preserves_created_at_and_changes_updated_at(
    client,
    auth_user,
    transaction_type,
    factory,
    update_field,
    update_value,
):
    created = factory(client, auth_user)
    transaction_id = created["id"]

    response = client.patch(
        transaction_url(transaction_type, transaction_id),
        json={update_field: update_value},
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    updated = response.json()
    assert updated["created_at"] == created["created_at"]
    assert updated["updated_at"] >= created["updated_at"]

    persisted = client.get(
        transaction_url(transaction_type, transaction_id),
        headers=auth_user["headers"],
    )

    assert persisted.status_code == 200
    assert persisted.json()["created_at"] == created["created_at"]
    assert persisted.json()["updated_at"] == updated["updated_at"]


@pytest.mark.parametrize(
    "transaction_type, factory",
    [
        ("income", create_income_transaction),
        ("expense", create_expense_transaction),
    ],
)
def test_transaction_routes_reject_client_supplied_response_only_timestamps(
    client,
    auth_user,
    transaction_type,
    factory,
):
    created = factory(client, auth_user)

    create_payload = (
        income_payload(created_at="2020-01-01T00:00:00Z")
        if transaction_type == "income"
        else expense_payload(created_at="2020-01-01T00:00:00Z")
    )
    create_response = client.post(
        TRANSACTION_URL,
        json=create_payload,
        headers=auth_user["headers"],
    )
    assert create_response.status_code == 422

    update_response = client.patch(
        transaction_url(transaction_type, created["id"]),
        json={"updated_at": "2020-01-01T00:00:00Z"},
        headers=auth_user["headers"],
    )
    assert update_response.status_code == 422



# ============================================================
# 15. RESPONSE MODEL AND SENSITIVE DATA TESTS
# ============================================================

@pytest.mark.parametrize(
    "transaction_type, factory, expected_keys, forbidden_keys",
    [
        (
            "income",
            create_income_transaction,
            {
                "id",
                "amount",
                "date",
                "source",
                "description",
                "type",
                "icon",
                "created_at",
                "updated_at",
            },
            {
                "category",
                "user_id",
                "password",
                "email",
                "hashed_password",
            },
        ),
        (
            "expense",
            create_expense_transaction,
            {
                "id",
                "amount",
                "date",
                "category",
                "description",
                "type",
                "icon",
                "created_at",
                "updated_at",
            },
            {
                "source",
                "user_id",
                "password",
                "email",
                "hashed_password",
            },
        ),
    ],
)
def test_transaction_response_fields_and_sensitive_data(
    client,
    auth_user,
    transaction_type,
    factory,
    expected_keys,
    forbidden_keys,
):
    created = factory(client, auth_user)

    response = client.get(
        transaction_url(transaction_type, created["id"]),
        headers=auth_user["headers"],
    )

    assert response.status_code == 200, response.text

    data = response.json()

    # Verify the exact response schema.
    assert set(data.keys()) == expected_keys

    # Verify transaction-type-specific fields.
    if transaction_type == "income":
        assert "source" in data
        assert "category" not in data
    else:
        assert "category" in data
        assert "source" not in data

    # Verify newly added transaction fields.
    assert "icon" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # Verify sensitive/internal fields are never exposed.
    for field in forbidden_keys:
        assert field not in data



def test_get_all_transaction_type_consistency(
    client,
    auth_user,
):
    create_income_transaction(client, auth_user)
    create_expense_transaction(client, auth_user)

    response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200

    for item in response.json():
        if item["type"] == "income":
            assert "source" in item
            assert "category" not in item
        elif item["type"] == "expense":
            assert "category" in item
            assert "source" not in item
        else:
            pytest.fail(
                f"Unexpected transaction type: {item['type']}"
            )


# ============================================================
# 16. COMPLETE INCOME LIFECYCLE
# ============================================================

def test_income_transaction_complete_lifecycle(client, auth_user):
    created = create_income_transaction(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )

    transaction_id = created["id"]

    # Verify creation
    assert created["id"] == transaction_id
    assert created["type"] == "income"
    assert Decimal(str(created["amount"])) == Decimal("100")

    # Get all transactions
    get_all = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert get_all.status_code == 200, get_all.text

    assert (
        ("income", transaction_id)
        in {
            (item["type"], item["id"])
            for item in get_all.json()
        }
    )

    # Get by ID
    get_by_id = client.get(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_by_id.status_code == 200, get_by_id.text

    fetched = get_by_id.json()

    assert fetched["id"] == transaction_id
    assert fetched["type"] == "income"
    assert Decimal(str(fetched["amount"])) == Decimal("100")
    assert fetched["source"] == "Salary"

    # Update
    update = client.patch(
        transaction_url("income", transaction_id),
        json={
            "amount": 500,
            "source": "Freelancing",
        },
        headers=auth_user["headers"],
    )

    assert update.status_code == 200, update.text

    updated = update.json()

    assert updated["id"] == transaction_id
    assert updated["type"] == "income"
    assert Decimal(str(updated["amount"])) == Decimal("500")
    assert updated["source"] == "Freelancing"

    # Verify persistence
    get_updated = client.get(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_updated.status_code == 200, get_updated.text

    persisted = get_updated.json()

    assert persisted["id"] == transaction_id
    assert persisted["type"] == "income"
    assert Decimal(str(persisted["amount"])) == Decimal("500")
    assert persisted["source"] == "Freelancing"

    # Delete
    delete = client.delete(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert delete.status_code == 204, delete.text

    # Verify deletion
    get_deleted = client.get(
        transaction_url("income", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_deleted.status_code == 404


# ============================================================
# 17. COMPLETE EXPENSE LIFECYCLE
# ============================================================

def test_expense_transaction_complete_lifecycle(client, auth_user):
    created = create_expense_transaction(
        client,
        auth_user,
        amount=100,
        category="Food",
    )

    transaction_id = created["id"]

    # Verify creation
    assert created["id"] == transaction_id
    assert created["type"] == "expense"
    assert Decimal(str(created["amount"])) == Decimal("100")

    # Get all transactions
    get_all = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert get_all.status_code == 200, get_all.text

    assert (
        ("expense", transaction_id)
        in {
            (item["type"], item["id"])
            for item in get_all.json()
        }
    )

    # Get by ID
    get_by_id = client.get(
        transaction_url("expense", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_by_id.status_code == 200, get_by_id.text

    fetched = get_by_id.json()

    assert fetched["id"] == transaction_id
    assert fetched["type"] == "expense"
    assert Decimal(str(fetched["amount"])) == Decimal("100")
    assert fetched["category"] == "Food"

    # Update
    update = client.patch(
        transaction_url("expense", transaction_id),
        json={
            "amount": 500,
            "category": "Travel",
        },
        headers=auth_user["headers"],
    )

    assert update.status_code == 200, update.text

    updated = update.json()

    assert updated["id"] == transaction_id
    assert updated["type"] == "expense"
    assert Decimal(str(updated["amount"])) == Decimal("500")
    assert updated["category"] == "Travel"

    # Verify persistence
    get_updated = client.get(
        transaction_url("expense", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_updated.status_code == 200, get_updated.text

    persisted = get_updated.json()

    assert persisted["id"] == transaction_id
    assert persisted["type"] == "expense"
    assert Decimal(str(persisted["amount"])) == Decimal("500")
    assert persisted["category"] == "Travel"

    # Delete
    delete = client.delete(
        transaction_url("expense", transaction_id),
        headers=auth_user["headers"],
    )

    assert delete.status_code == 204, delete.text

    # Verify deletion
    get_deleted = client.get(
        transaction_url("expense", transaction_id),
        headers=auth_user["headers"],
    )

    assert get_deleted.status_code == 404


# ============================================================
# 18. MIXED TRANSACTION LIFECYCLE
# ============================================================

def test_mixed_transaction_lifecycle(client, auth_user):
    # =========================================================
    # Create transactions
    # =========================================================

    income_a = create_income_transaction(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
    )

    expense_a = create_expense_transaction(
        client,
        auth_user,
        amount=200,
        date="2026-09-02",
    )

    income_b = create_income_transaction(
        client,
        auth_user,
        amount=300,
        date="2026-09-03",
    )

    expense_b = create_expense_transaction(
        client,
        auth_user,
        amount=400,
        date="2026-09-04",
    )

    # =========================================================
    # Verify all transactions are returned
    # =========================================================

    initial = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert initial.status_code == 200, initial.text

    initial_data = initial.json()

    assert len(initial_data) == 4

    initial_transactions = {
        (transaction["type"], transaction["id"])
        for transaction in initial_data
    }

    assert ("income", income_a["id"]) in initial_transactions
    assert ("expense", expense_a["id"]) in initial_transactions
    assert ("income", income_b["id"]) in initial_transactions
    assert ("expense", expense_b["id"]) in initial_transactions

    # =========================================================
    # Update income A
    # =========================================================

    update_income_a = client.patch(
        transaction_url("income", income_a["id"]),
        json={
            "amount": 111,
        },
        headers=auth_user["headers"],
    )

    assert update_income_a.status_code == 200, update_income_a.text

    updated_income_a = update_income_a.json()

    assert updated_income_a["id"] == income_a["id"]
    assert updated_income_a["type"] == "income"

    assert (
        Decimal(str(updated_income_a["amount"]))
        == Decimal("111")
    )

    # =========================================================
    # Update expense A
    # =========================================================

    update_expense_a = client.patch(
        transaction_url("expense", expense_a["id"]),
        json={
            "amount": 222,
        },
        headers=auth_user["headers"],
    )

    assert update_expense_a.status_code == 200, update_expense_a.text

    updated_expense_a = update_expense_a.json()

    assert updated_expense_a["id"] == expense_a["id"]
    assert updated_expense_a["type"] == "expense"

    assert (
        Decimal(str(updated_expense_a["amount"]))
        == Decimal("222")
    )

    # =========================================================
    # Verify income update persisted
    # =========================================================

    income_after_update = client.get(
        transaction_url("income", income_a["id"]),
        headers=auth_user["headers"],
    )

    assert income_after_update.status_code == 200, income_after_update.text

    income_after_update_data = income_after_update.json()

    assert income_after_update_data["id"] == income_a["id"]
    assert income_after_update_data["type"] == "income"

    assert (
        Decimal(str(income_after_update_data["amount"]))
        == Decimal("111")
    )

    # =========================================================
    # Verify expense update persisted
    # =========================================================

    expense_after_update = client.get(
        transaction_url("expense", expense_a["id"]),
        headers=auth_user["headers"],
    )

    assert expense_after_update.status_code == 200, expense_after_update.text

    expense_after_update_data = expense_after_update.json()

    assert expense_after_update_data["id"] == expense_a["id"]
    assert expense_after_update_data["type"] == "expense"

    assert (
        Decimal(str(expense_after_update_data["amount"]))
        == Decimal("222")
    )

    # =========================================================
    # Delete income B
    # =========================================================

    delete_income_b = client.delete(
        transaction_url("income", income_b["id"]),
        headers=auth_user["headers"],
    )

    assert delete_income_b.status_code == 204, delete_income_b.text

    get_deleted_income = client.get(
        transaction_url("income", income_b["id"]),
        headers=auth_user["headers"],
    )

    assert get_deleted_income.status_code == 404

    # =========================================================
    # Delete expense B
    # =========================================================

    delete_expense_b = client.delete(
        transaction_url("expense", expense_b["id"]),
        headers=auth_user["headers"],
    )

    assert delete_expense_b.status_code == 204, delete_expense_b.text

    get_deleted_expense = client.get(
        transaction_url("expense", expense_b["id"]),
        headers=auth_user["headers"],
    )

    assert get_deleted_expense.status_code == 404

    # =========================================================
    # Verify final transaction list
    # =========================================================

    final_response = client.get(
        TRANSACTIONS_URL,
        headers=auth_user["headers"],
    )

    assert final_response.status_code == 200, final_response.text

    final_data = final_response.json()

    assert len(final_data) == 2

    final_transactions = {
        (transaction["type"], transaction["id"])
        for transaction in final_data
    }

    # Remaining transactions
    assert ("income", income_a["id"]) in final_transactions
    assert ("expense", expense_a["id"]) in final_transactions

    # Deleted transactions
    assert ("income", income_b["id"]) not in final_transactions
    assert ("expense", expense_b["id"]) not in final_transactions

    # =========================================================
    # Find transactions using BOTH type and ID
    #
    # Important because income and expense IDs can overlap.
    # =========================================================

    final_income = next(
        transaction
        for transaction in final_data
        if (
            transaction["type"] == "income"
            and transaction["id"] == income_a["id"]
        )
    )

    final_expense = next(
        transaction
        for transaction in final_data
        if (
            transaction["type"] == "expense"
            and transaction["id"] == expense_a["id"]
        )
    )

    # =========================================================
    # Verify final income
    # =========================================================

    assert final_income["type"] == "income"
    assert final_income["id"] == income_a["id"]

    assert (
        Decimal(str(final_income["amount"]))
        == Decimal("111")
    )

    # =========================================================
    # Verify final expense
    # =========================================================

    assert final_expense["type"] == "expense"
    assert final_expense["id"] == expense_a["id"]

    assert (
        Decimal(str(final_expense["amount"]))
        == Decimal("222")
    )


# ============================================================
# 19. DATABASE / ROLLBACK REGRESSION COVERAGE
# ============================================================

def test_failed_validation_does_not_modify_existing_transaction(
    client,
    auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
        amount=100,
        source="Salary",
    )

    response = client.patch(
        transaction_url("income", created["id"]),
        json={
            "amount": 999,
            "category": "Food",
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422

    verify = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert verify.status_code == 200
    assert Decimal(verify.json()["amount"]) == Decimal(100)
    assert verify.json()["source"] == "Salary"


def test_failed_delete_of_other_user_does_not_remove_transaction(
    client,
    auth_user,
    second_auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
    )

    response = client.delete(
        transaction_url("income", created["id"]),
        headers=second_auth_user["headers"],
    )

    assert response.status_code == 404

    verify = client.get(
        transaction_url("income", created["id"]),
        headers=auth_user["headers"],
    )

    assert verify.status_code == 200


# ============================================================
# 20. ROUTE DELEGATION / TYPE REGRESSION
# ============================================================

def test_income_transaction_route_delegates_to_income_behavior(
    client,
    auth_user,
):
    created = create_income_transaction(
        client,
        auth_user,
        source="Salary",
    )

    assert created["type"] == "income"
    assert "source" in created
    assert "category" not in created

    updated = client.patch(
        transaction_url("income", created["id"]),
        json={"source": "Freelancing"},
        headers=auth_user["headers"],
    )

    assert updated.status_code == 200
    assert updated.json()["type"] == "income"
    assert updated.json()["source"] == "Freelancing"


def test_expense_transaction_route_delegates_to_expense_behavior(
    client,
    auth_user,
):
    created = create_expense_transaction(
        client,
        auth_user,
        category="Food",
    )

    assert created["type"] == "expense"
    assert "category" in created
    assert "source" not in created

    updated = client.patch(
        transaction_url("expense", created["id"]),
        json={"category": "Travel"},
        headers=auth_user["headers"],
    )

    assert updated.status_code == 200
    assert updated.json()["type"] == "expense"
    assert updated.json()["category"] == "Travel"
