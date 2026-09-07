# ============================================================
# Helper
# ============================================================

def create_expense(client, **overrides):
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
    )

    assert response.status_code == 201

    return response.json()


# ============================================================
# POST /api/v1/expense
# ============================================================

def test_create_expense_minimum_valid_request(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], int)

    assert data["amount"] == 100
    assert data["date"] == "2026-09-03"
    assert data["category"] == "food"
    assert data["description"] == ""


def test_create_expense_complete_request(client):
    payload = {
        "amount": 250.50,
        "date": "2026-09-03",
        "category": "transport",
        "description": "Uber to airport",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == payload["amount"]
    assert data["date"] == payload["date"]
    assert data["category"] == payload["category"]
    assert data["description"] == payload["description"]


def test_create_expense_small_positive_amount(client):
    payload = {
        "amount": 0.01,
        "date": "2026-09-03",
        "category": "food",
        "description": "Small expense",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 0.01


def test_create_expense_negative_amount(client):
    payload = {
        "amount": -100,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_zero_amount(client):
    payload = {
        "amount": 0,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_invalid_amount_type(client):
    payload = {
        "amount": "abc",
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_null_amount(client):
    payload = {
        "amount": None,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_missing_amount(client):
    payload = {
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_missing_date(client):
    payload = {
        "amount": 100,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_missing_category(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# POST - Category validation
# ============================================================

def test_create_expense_empty_category(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_whitespace_only_category(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "   ",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_category_is_trimmed(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "  food  ",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "food"


def test_create_expense_category_one_character(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "f",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201


def test_create_expense_category_exactly_100_characters(client):
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
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == category


def test_create_expense_category_101_characters(client):
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
    )

    assert response.status_code == 422


def test_create_expense_null_category(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": None,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_invalid_category_type(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": 123,
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# POST - Date validation
# ============================================================

def test_create_expense_valid_date(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201


def test_create_expense_date_is_trimmed(client):
    payload = {
        "amount": 100,
        "date": " 2026-09-03 ",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["date"] == "2026-09-03"


def test_create_expense_empty_date(client):
    payload = {
        "amount": 100,
        "date": "",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_whitespace_only_date(client):
    payload = {
        "amount": 100,
        "date": "   ",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_invalid_date_format(client):
    payload = {
        "amount": 100,
        "date": "03-09-2026",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_impossible_date(client):
    payload = {
        "amount": 100,
        "date": "2026-02-30",
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_null_date(client):
    payload = {
        "amount": 100,
        "date": None,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_invalid_date_type(client):
    payload = {
        "amount": 100,
        "date": 123,
        "category": "food",
        "description": "Lunch",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# POST - Description validation
# ============================================================

def test_create_expense_description_omitted(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == ""


def test_create_expense_empty_description(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": "",
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == ""


def test_create_expense_description_exactly_500_characters(client):
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
    )

    assert response.status_code == 201

    data = response.json()

    assert data["description"] == description


def test_create_expense_description_501_characters(client):
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
    )

    assert response.status_code == 422


def test_create_expense_null_description(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": None,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_invalid_description_type(client):
    payload = {
        "amount": 100,
        "date": "2026-09-03",
        "category": "food",
        "description": 123,
    }

    response = client.post(
        "/api/v1/expense",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# POST - Unknown fields
# ============================================================

def test_create_expense_rejects_unknown_field(client):
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
    )

    assert response.status_code == 422


# ============================================================
# GET /api/v1/expense
# ============================================================

def test_get_expenses(client):
    create_expense(client)

    response = client.get(
        "/api/v1/expense"
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


def test_get_expenses_empty_collection(client):
    response = client.get(
        "/api/v1/expense"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_expenses_ordered_by_date_desc_and_id_desc(client):
    expense_1 = create_expense(
        client,
        amount=100,
        date="2026-09-01",
    )

    expense_2 = create_expense(
        client,
        amount=200,
        date="2026-09-02",
    )

    expense_3 = create_expense(
        client,
        amount=300,
        date="2026-09-02",
    )

    response = client.get(
        "/api/v1/expense"
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

def test_get_expense_by_id(client):
    expense = create_expense(client)

    expense_id = expense["id"]

    response = client.get(
        f"/api/v1/expense/{expense_id}"
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


def test_get_nonexistent_expense(client):
    response = client.get(
        "/api/v1/expense/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data


def test_get_expense_invalid_id(client):
    response = client.get(
        "/api/v1/expense/abc"
    )

    assert response.status_code == 422


# ============================================================
# PATCH /api/v1/expense/{expense_id}
# ============================================================

def test_patch_amount_only(client):
    expense = create_expense(
        client,
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
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert data["amount"] == 500
    assert data["date"] == "2026-09-01"
    assert data["category"] == "food"
    assert data["description"] == "Lunch"


def test_patch_small_positive_amount(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 0.01,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 0.01


def test_patch_date_only(client):
    expense = create_expense(
        client,
        date="2026-09-01",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "2026-09-05",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["date"] == "2026-09-05"
    assert data["amount"] == expense["amount"]
    assert data["category"] == expense["category"]
    assert data["description"] == expense["description"]


def test_patch_category_only(client):
    expense = create_expense(
        client,
        category="food",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "travel",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "travel"
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["description"] == expense["description"]


def test_patch_description_only(client):
    expense = create_expense(
        client,
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "Dinner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == "Dinner"
    assert data["amount"] == expense["amount"]
    assert data["date"] == expense["date"]
    assert data["category"] == expense["category"]


def test_patch_multiple_fields(client):
    expense = create_expense(
        client,
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
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 500
    assert data["category"] == "travel"
    assert data["description"] == "Taxi"
    assert data["date"] == "2026-09-01"


def test_patch_all_four_fields(client):
    expense = create_expense(
        client,
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

def test_patch_date_is_trimmed(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": " 2026-09-10 ",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["date"] == "2026-09-10"


def test_patch_empty_date(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "",
        },
    )

    assert response.status_code == 422


def test_patch_whitespace_only_date(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "   ",
        },
    )

    assert response.status_code == 422


def test_patch_invalid_date(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": "2026-02-30",
        },
    )

    assert response.status_code == 422


def test_patch_invalid_date_type(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": 123,
        },
    )

    assert response.status_code == 422


def test_patch_null_date(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "date": None,
        },
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Category validation
# ============================================================

def test_patch_category_is_trimmed(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "  travel  ",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "travel"


def test_patch_empty_category(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "",
        },
    )

    assert response.status_code == 422


def test_patch_whitespace_only_category(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "   ",
        },
    )

    assert response.status_code == 422


def test_patch_category_exactly_100_characters(client):
    expense = create_expense(client)

    category = "a" * 100

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": category,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == category


def test_patch_category_101_characters(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "a" * 101,
        },
    )

    assert response.status_code == 422


def test_patch_invalid_category_type(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": 123,
        },
    )

    assert response.status_code == 422


def test_patch_null_category(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": None,
        },
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Description validation
# ============================================================

def test_patch_empty_description(client):
    expense = create_expense(
        client,
        description="Lunch",
    )

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == ""


def test_patch_description_exactly_500_characters(client):
    expense = create_expense(client)

    description = "a" * 500

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": description,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == description


def test_patch_description_501_characters(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": "a" * 501,
        },
    )

    assert response.status_code == 422


def test_patch_invalid_description_type(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": 123,
        },
    )

    assert response.status_code == 422


def test_patch_null_description(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "description": None,
        },
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Amount validation
# ============================================================

def test_patch_negative_amount(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": -50,
        },
    )

    assert response.status_code == 422


def test_patch_zero_amount(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": 0,
        },
    )

    assert response.status_code == 422


def test_patch_invalid_amount_type(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": "abc",
        },
    )

    assert response.status_code == 422


def test_patch_null_amount(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "amount": None,
        },
    )

    assert response.status_code == 422


# ============================================================
# PATCH - Request / resource errors
# ============================================================

def test_patch_empty_body(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={},
    )

    assert response.status_code == 400


def test_patch_no_body(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}"
    )

    assert response.status_code == 422


def test_patch_invalid_id(client):
    response = client.patch(
        "/api/v1/expense/abc",
        json={
            "amount": 500,
        },
    )

    assert response.status_code == 422


def test_patch_nonexistent_expense(client):
    response = client.patch(
        "/api/v1/expense/999999",
        json={
            "amount": 500,
        },
    )

    assert response.status_code == 404


def test_patch_rejects_unknown_field(client):
    expense = create_expense(client)

    response = client.patch(
        f"/api/v1/expense/{expense['id']}",
        json={
            "category": "travel",
            "unknown": "value",
        },
    )

    assert response.status_code == 422


# ============================================================
# DELETE /api/v1/expense/{expense_id}
# ============================================================

def test_delete_expense(client):
    expense = create_expense(client)

    expense_id = expense["id"]

    response = client.delete(
        f"/api/v1/expense/{expense_id}"
    )

    assert response.status_code == 204

    assert response.content == b""


def test_delete_expense_verifies_deletion(client):
    expense = create_expense(client)

    expense_id = expense["id"]

    delete_response = client.delete(
        f"/api/v1/expense/{expense_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/expense/{expense_id}"
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_expense(client):
    response = client.delete(
        "/api/v1/expense/999999"
    )

    assert response.status_code == 404


def test_delete_invalid_id(client):
    response = client.delete(
        "/api/v1/expense/abc"
    )

    assert response.status_code == 422


def test_delete_same_expense_twice(client):
    expense = create_expense(client)

    expense_id = expense["id"]

    first_response = client.delete(
        f"/api/v1/expense/{expense_id}"
    )

    assert first_response.status_code == 204

    second_response = client.delete(
        f"/api/v1/expense/{expense_id}"
    )

    assert second_response.status_code == 404


# ============================================================
# Database integrity
# ============================================================

def test_invalid_post_does_not_create_expense(client):
    response = client.post(
        "/api/v1/expense",
        json={
            "amount": -100,
            "date": "2026-09-03",
            "category": "food",
            "description": "Invalid",
        },
    )

    assert response.status_code == 422

    get_response = client.get(
        "/api/v1/expense"
    )

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_invalid_patch_does_not_modify_expense(client):
    expense = create_expense(
        client,
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
    )

    assert response.status_code == 422

    get_response = client.get(
        f"/api/v1/expense/{expense_id}"
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["amount"] == 100
    assert data["category"] == "food"
    assert data["description"] == "Lunch"


def test_failed_delete_does_not_affect_other_expenses(client):
    expense_1 = create_expense(
        client,
        amount=100,
        category="food",
    )

    expense_2 = create_expense(
        client,
        amount=200,
        category="travel",
    )

    response = client.delete(
        "/api/v1/expense/999999"
    )

    assert response.status_code == 404

    response_1 = client.get(
        f"/api/v1/expense/{expense_1['id']}"
    )

    response_2 = client.get(
        f"/api/v1/expense/{expense_2['id']}"
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 200


# ============================================================
# Complete Expense lifecycle
# ============================================================

def test_expense_complete_lifecycle(client):
    # CREATE
    create_response = client.post(
        "/api/v1/expense",
        json={
            "amount": 100,
            "date": "2026-09-01",
            "category": "food",
            "description": "Lunch",
        },
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
        f"/api/v1/expense/{expense_id}"
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
    )

    assert patch_response.status_code == 200

    data = patch_response.json()

    assert data["amount"] == 250
    assert data["category"] == "travel"
    assert data["date"] == "2026-09-01"
    assert data["description"] == "Lunch"

    # GET AGAIN
    get_response = client.get(
        f"/api/v1/expense/{expense_id}"
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["amount"] == 250
    assert data["category"] == "travel"

    # DELETE
    delete_response = client.delete(
        f"/api/v1/expense/{expense_id}"
    )

    assert delete_response.status_code == 204

    # VERIFY DELETION
    get_response = client.get(
        f"/api/v1/expense/{expense_id}"
    )

    assert get_response.status_code == 404