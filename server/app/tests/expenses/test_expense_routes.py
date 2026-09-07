import pytest

from app.features.expense.models.expense import Expense


# ============================================================
# Authentication Helpers
# ============================================================

def create_user_and_get_token(
    client,
    email="test@example.com",
    full_name="Test User",
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
    return create_user_and_get_token(
        client=client,
    )


# ============================================================
# Expense Helper
# ============================================================

def create_expense(
    client,
    auth_user,
    **overrides,
):
    payload = {
        "amount": 100,
        "date": "2026-09-01",
        "category": "food",
        "description": "Lunch",
    }

    payload.update(overrides)

    response = client.post(
        "/api/v1/expense",
        json=payload,
        headers=auth_user["headers"],
    )

    assert response.status_code == 201

    return response.json()


# ============================================================
# POST /api/v1/expense
# ============================================================

def test_create_expense_minimum_valid_request(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], int)

    assert data["amount"] == 100
    assert data["date"] == "2026-09-03"
    assert data["category"] == "food"
    assert data["description"] == ""


def test_create_expense_complete_request(client, auth_user):
    payload = {
        "amount": 250.50,
        "date": "2026-09-03",
        "category": "transport",
        "description": "Uber to airport",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == payload["amount"]
    assert data["date"] == payload["date"]
    assert data["category"] == payload["category"]
    assert data["description"] == payload["description"]


def test_create_expense_small_positive_amount(client, auth_user):
    payload = {
        "amount": 0.01,
        "date": "2026-09-03",
        "category": "food",
        "description": "Small expense",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 0.01


def test_create_expense_negative_amount(client, auth_user):
    payload = {
        "amount": -100,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_zero_amount(client, auth_user):
    payload = {
        "amount": 0,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_invalid_amount_type(client, auth_user):
    payload = {
        "amount": "abc",
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_null_amount(client, auth_user):
    payload = {
        "amount": None,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_missing_amount(client, auth_user):
    payload = {
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_missing_date(client, auth_user):
    payload = {
        "amount": 100,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_missing_category(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# POST - Category validation
# ============================================================

def test_create_expense_empty_category(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_whitespace_only_category(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "   ",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_category_is_trimmed(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "  food  ",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "food"


def test_create_expense_category_one_character(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "f",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201


def test_create_expense_category_exactly_100_characters(client, auth_user):
    category = "a" * 100

    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": category,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == category


def test_create_expense_category_101_characters(client, auth_user):
    category = "a" * 101

    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": category,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_null_category(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": None,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_invalid_category_type(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": 123,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# POST - Date validation
# ============================================================

def test_create_expense_valid_date(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201


def test_create_expense_date_is_trimmed(client, auth_user):
    payload = {
        "amount": 100,
        "date": " 2026-09-03 ",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["date"] == "2026-09-03"


def test_create_expense_empty_date(client, auth_user):
    payload = {
        "amount": 100,
        "date": "",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_whitespace_only_date(client, auth_user):
    payload = {
        "amount": 100,
        "date": "   ",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_invalid_date_format(client, auth_user):
    payload = {
        "amount": 100,
        "date": "03-09-2026",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_impossible_date(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-02-30",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_null_date(client, auth_user):
    payload = {
        "amount": 100,
        "date": None,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_invalid_date_type(client, auth_user):
    payload = {
        "amount": 100,
        "date": 123,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# POST - Description validation
# ============================================================

def test_create_expense_description_omitted(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == ""


def test_create_expense_empty_description(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": "",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == ""


def test_create_expense_description_exactly_500_characters(client, auth_user):
    description = "a" * 500

    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": description,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == description


def test_create_expense_description_501_characters(client, auth_user):
    description = "a" * 501

    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": description,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_null_description(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": None,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_create_expense_invalid_description_type(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": 123,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# POST - Unknown fields
# ============================================================

def test_create_expense_rejects_unknown_field(client, auth_user):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
        "unknown": "value",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# GET /api/v1/expense
# ============================================================

def test_get_expenses(client, auth_user):
    create_expense(client, auth_user)

    response = client.get(
        "/api/v1/expense",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    expense = data[0]

    assert "id" in expense
    assert "amount" in expense
    assert "date" in expense
    assert "category" in expense
    assert "description" in expense


def test_get_expenses_empty_collection(client, auth_user):
    response = client.get(
        "/api/v1/expense",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200
    assert response.json() == []


def test_get_expenses_ordered_by_date_desc_and_id_desc(client, auth_user):
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
        "/api/v1/expense",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    ids = [expense["id"] for expense in data]

    assert ids == [
        expense_3["id"],
        expense_2["id"],
        expense_1["id"],
    ]


# ============================================================
# GET /api/v1/expense/{expense_id}
# ============================================================

def test_get_expense_by_id(client, auth_user):
    expense = create_expense(client, auth_user)

    expense_id = expense["id"]

    response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "id",
        "amount",
        "date",
        "category",
        "description",
    }

    assert data["id"] == expense_id
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["category"] == expense["category"]
    assert data["description"] == expense["description"]


def test_get_nonexistent_expense(client, auth_user):
    response = client.get(
        "/api/v1/expense/999999",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data


def test_get_expense_invalid_id(client, auth_user):
    response = client.get(
        "/api/v1/expense/abc",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# PATCH /api/v1/expense/{expense_id}
# ============================================================

def test_patch_amount_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="food",
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 500,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert data["amount"] == 500
    assert data["date"] == "2026-09-01"
    assert data["category"] == "food"
    assert data["description"] == "Lunch"


def test_patch_small_positive_amount(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 0.01,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 0.01


def test_patch_date_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        date="2026-09-01",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "2026-09-05",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["date"] == "2026-09-05"
    assert data["amount"] == expense["amount"]
    assert data["category"] == expense["category"]
    assert data["description"] == expense["description"]


def test_patch_category_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        category="food",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "travel",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "travel"
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["description"] == expense["description"]


def test_patch_description_only(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "Dinner",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == "Dinner"
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["category"] == expense["category"]


def test_patch_multiple_fields(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="food",
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 500,
            "category": "travel",
            "description": "Taxi",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 500
    assert data["category"] == "travel"
    assert data["description"] == "Taxi"
    assert data["date"] == "2026-09-01"


def test_patch_all_four_fields(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        date="2026-09-01",
        category="food",
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 500,
            "date": "2026-09-10",
            "category": "travel",
            "description": "Taxi to airport",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert data["amount"] == 500
    assert data["date"] == "2026-09-10"
    assert data["category"] == "travel"
    assert data["description"] == "Taxi to airport"


# ============================================================
# PATCH - Date validation
# ============================================================

def test_patch_date_is_trimmed(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": " 2026-09-10 ",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["date"] == "2026-09-10"


def test_patch_empty_date(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_whitespace_only_date(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "   ",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_date(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "2026-02-30",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_date_type(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": 123,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_null_date(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": None,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# PATCH - Category validation
# ============================================================

def test_patch_category_is_trimmed(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "  travel  ",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "travel"


def test_patch_empty_category(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_whitespace_only_category(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "   ",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_category_exactly_100_characters(client, auth_user):
    expense = create_expense(client, auth_user)

    category = "a" * 100

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": category,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == category


def test_patch_category_101_characters(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "a" * 101,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_category_type(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": 123,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_null_category(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": None,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# PATCH - Description validation
# ============================================================

def test_patch_empty_description(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == ""


def test_patch_description_exactly_500_characters(client, auth_user):
    expense = create_expense(client, auth_user)

    description = "a" * 500

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": description,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == description


def test_patch_description_501_characters(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "a" * 501,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_description_type(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": 123,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_null_description(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": None,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# PATCH - Amount validation
# ============================================================

def test_patch_negative_amount(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": -50,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_zero_amount(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 0,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_amount_type(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": "abc",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_null_amount(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": None,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# PATCH - Request / resource errors
# ============================================================

def test_patch_empty_body(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={},
    
        headers=auth_user["headers"],
)

    assert response.status_code == 400


def test_patch_no_body(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_invalid_id(client, auth_user):
    response = client.patch(
        "/api/v1/expense/abc",
        json={
            "amount": 500,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_patch_nonexistent_expense(client, auth_user):
    response = client.patch(
        "/api/v1/expense/999999",
        json={
            "amount": 500,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 404


def test_patch_rejects_unknown_field(client, auth_user):
    expense = create_expense(client, auth_user)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "travel",
            "unknown": "value",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


# ============================================================
# DELETE /api/v1/expense/{expense_id}
# ============================================================

def test_delete_expense(client, auth_user):
    expense = create_expense(client, auth_user)

    expense_id = expense["id"]

    response = client.delete(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 204

    assert response.content == b""


def test_delete_expense_verifies_deletion(client, auth_user):
    expense = create_expense(client, auth_user)

    expense_id = expense["id"]

    delete_response = client.delete(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 404


def test_delete_nonexistent_expense(client, auth_user):
    response = client.delete(
        "/api/v1/expense/999999",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 404


def test_delete_invalid_id(client, auth_user):
    response = client.delete(
        "/api/v1/expense/abc",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422


def test_delete_same_expense_twice(client, auth_user):
    expense = create_expense(client, auth_user)

    expense_id = expense["id"]

    first_response = client.delete(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert first_response.status_code == 204

    second_response = client.delete(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert second_response.status_code == 404


# ============================================================
# Database integrity
# ============================================================

def test_invalid_post_does_not_create_expense(client, auth_user):
    response = client.post(
        "/api/v1/expense",
        json={
            "amount": -100,
            "date": "2026-09-03",
            "category": "food",
            "description": "Invalid",
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422

    get_response = client.get(
        "/api/v1/expense",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_invalid_patch_does_not_modify_expense(client, auth_user):
    expense = create_expense(
        client,
        auth_user,
        amount=100,
        category="food",
        description="Lunch",
    )

    expense_id = expense["id"]

    response = client.patch(
        f"/api/v1/expense/{expense_id}",
        json={
            "amount": -500,
        },
    
        headers=auth_user["headers"],
)

    assert response.status_code == 422

    get_response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["amount"] == 100
    assert data["category"] == "food"
    assert data["description"] == "Lunch"


def test_failed_delete_does_not_affect_other_expenses(client, auth_user):
    expense_1 = create_expense(
        client,
        auth_user,
        amount=100,
        category="food",
    )

    expense_2 = create_expense(
        client,
        auth_user,
        amount=200,
        category="travel",
    )

    response = client.delete(
        "/api/v1/expense/999999",
    
        headers=auth_user["headers"],
)

    assert response.status_code == 404

    response_1 = client.get(
        f"/api/v1/expense/{expense_1['id']}",
    
        headers=auth_user["headers"],
)

    response_2 = client.get(
        f"/api/v1/expense/{expense_2['id']}",
    
        headers=auth_user["headers"],
)

    assert response_1.status_code == 200
    assert response_2.status_code == 200


# ============================================================
# Complete Expense lifecycle
# ============================================================

def test_expense_complete_lifecycle(client, auth_user):
    # CREATE
    create_response = client.post(
        "/api/v1/expense",
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "food",
            "description": "Lunch",
        },
    
        headers=auth_user["headers"],
)

    assert create_response.status_code == 201

    expense = create_response.json()

    expense_id = expense["id"]

    assert expense["amount"] == 100
    assert expense["date"] == "2026-09-01"
    assert expense["category"] == "food"
    assert expense["description"] == "Lunch"

    # GET
    get_response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == expense_id
    assert data["amount"] == 100
    assert data["category"] == "food"

    # PATCH
    patch_response = client.patch(
        f"/api/v1/expense/{expense_id}",
        json={
            "amount": 250,
            "category": "travel",
        },
    
        headers=auth_user["headers"],
)

    assert patch_response.status_code == 200

    data = patch_response.json()

    assert data["amount"] == 250
    assert data["category"] == "travel"
    assert data["date"] == "2026-09-01"
    assert data["description"] == "Lunch"

    # GET AGAIN
    get_response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["amount"] == 250
    assert data["category"] == "travel"

    # DELETE
    delete_response = client.delete(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert delete_response.status_code == 204

    # VERIFY DELETION
    get_response = client.get(
        f"/api/v1/expense/{expense_id}",
    
        headers=auth_user["headers"],
)

    assert get_response.status_code == 404

# ============================================================
# Authentication Protection Tests
# ============================================================

def test_create_expense_without_token(client):
    response = client.post(
        "/api/v1/expense",
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "food",
            "description": "Lunch",
        },
    )

    assert response.status_code == 401


def test_get_expenses_without_token(client):
    response = client.get(
        "/api/v1/expense",
    )

    assert response.status_code == 401


def test_get_expense_by_id_without_token(client):
    response = client.get(
        "/api/v1/expense/1",
    )

    assert response.status_code == 401


def test_update_expense_without_token(client):
    response = client.patch(
        "/api/v1/expense/1",
        json={
            "amount": 200,
        },
    )

    assert response.status_code == 401


def test_delete_expense_without_token(client):
    response = client.delete(
        "/api/v1/expense/1",
    )

    assert response.status_code == 401


def test_get_expenses_with_invalid_token(client):
    response = client.get(
        "/api/v1/expense",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


# ============================================================
# User Isolation Tests
# ============================================================

def test_user_cannot_get_another_users_expense(client):
    user_a = create_user_and_get_token(
        client,
        email="usera@example.com",
        full_name="User A",
    )

    user_b = create_user_and_get_token(
        client,
        email="userb@example.com",
        full_name="User B",
    )

    expense = create_expense(
        client,
        user_a,
        amount=100,
        category="food",
    )

    response = client.get(
        f"/api/v1/expense/{expense['id']}",
        headers=user_b["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_update_another_users_expense(client):
    user_a = create_user_and_get_token(
        client,
        email="usera@example.com",
        full_name="User A",
    )

    user_b = create_user_and_get_token(
        client,
        email="userb@example.com",
        full_name="User B",
    )

    expense = create_expense(
        client,
        user_a,
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 500,
        },
        headers=user_b["headers"],
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_expense(client):
    user_a = create_user_and_get_token(
        client,
        email="usera@example.com",
        full_name="User A",
    )

    user_b = create_user_and_get_token(
        client,
        email="userb@example.com",
        full_name="User B",
    )

    expense = create_expense(
        client,
        user_a,
    )

    response = client.delete(
        f"/api/v1/expense/{expense['id']}",
        headers=user_b["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/api/v1/expense/{expense['id']}",
        headers=user_a["headers"],
    )

    assert owner_response.status_code == 200


def test_users_only_see_their_own_expenses(client):
    user_a = create_user_and_get_token(
        client,
        email="usera@example.com",
        full_name="User A",
    )

    user_b = create_user_and_get_token(
        client,
        email="userb@example.com",
        full_name="User B",
    )

    expense_a1 = create_expense(
        client,
        user_a,
        amount=100,
        category="food",
    )

    expense_a2 = create_expense(
        client,
        user_a,
        amount=200,
        category="transport",
    )

    expense_b1 = create_expense(
        client,
        user_b,
        amount=300,
        category="shopping",
    )

    response_a = client.get(
        "/api/v1/expense",
        headers=user_a["headers"],
    )

    assert response_a.status_code == 200

    expenses_a = response_a.json()
    expense_ids_a = {expense["id"] for expense in expenses_a}

    assert len(expenses_a) == 2
    assert expense_a1["id"] in expense_ids_a
    assert expense_a2["id"] in expense_ids_a
    assert expense_b1["id"] not in expense_ids_a

    response_b = client.get(
        "/api/v1/expense",
        headers=user_b["headers"],
    )

    assert response_b.status_code == 200

    expenses_b = response_b.json()

    assert len(expenses_b) == 1
    assert expenses_b[0]["id"] == expense_b1["id"]


def test_created_expense_belongs_to_authenticated_user(
    client,
    db,
    auth_user,
):
    expense_data = create_expense(
        client,
        auth_user,
    )

    expense = db.get(
        Expense,
        expense_data["id"],
    )

    assert expense is not None
    assert expense.user_id == auth_user["user"]["id"]


def test_user_cannot_modify_another_users_expense(client):
    user_a = create_user_and_get_token(
        client,
        email="usera@example.com",
        full_name="User A",
    )

    user_b = create_user_and_get_token(
        client,
        email="userb@example.com",
        full_name="User B",
    )

    expense = create_expense(
        client,
        user_a,
        amount=100,
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 999,
        },
        headers=user_b["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/api/v1/expense/{expense['id']}",
        headers=user_a["headers"],
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["amount"] == 100


def test_create_expense_cannot_accept_user_id(client, auth_user):
    response = client.post(
        "/api/v1/expense",
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "food",
            "description": "Lunch",
            "user_id": 999,
        },
        headers=auth_user["headers"],
    )

    assert response.status_code == 422