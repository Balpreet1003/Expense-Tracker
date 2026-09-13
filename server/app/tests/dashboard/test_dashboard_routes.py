from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense
from app.features.income.models.income import Income


DASHBOARD_URL = "/api/v1/summary"


# ============================================================
# Authentication Helpers
# ============================================================


def create_user_and_get_token(
    client,
    email="dashboard-test@example.com",
    full_name="Dashboard Test User",
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
    return create_user_and_get_token(
        client,
        email="dashboard-user@example.com",
        full_name="Dashboard User",
    )


@pytest.fixture
def second_auth_user(client):
    return create_user_and_get_token(
        client,
        email="dashboard-second-user@example.com",
        full_name="Second Dashboard User",
    )


# ============================================================
# Database Helpers
#
# Direct database creation is intentionally used because the
# dashboard tests need control over:
#
# - created_at
# - icons
# - exact transaction dates
# - same-date ordering
# - future transactions
# - old transactions
# ============================================================


def get_user(db, user_id):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def create_income(
    db,
    user_id,
    amount=Decimal("100.00"),
    transaction_date=None,
    created_at=None,
    icon="income-icon",
    source="Salary",
    description="Income transaction",
):
    if transaction_date is None:
        transaction_date = date.today()

    if created_at is None:
        created_at = datetime.now(timezone.utc)

    income = Income(
        user_id=user_id,
        amount=Decimal(str(amount)),
        date=transaction_date,
        created_at=created_at,
        updated_at=created_at,
        icon=icon,
        source=source,
        description=description,
    )

    db.add(income)
    db.commit()
    db.refresh(income)

    return income


def create_expense(
    db,
    user_id,
    amount=Decimal("100.00"),
    transaction_date=None,
    created_at=None,
    icon="expense-icon",
    category="Food",
    description="Expense transaction",
):
    if transaction_date is None:
        transaction_date = date.today()

    if created_at is None:
        created_at = datetime.now(timezone.utc)

    expense = Expense(
        user_id=user_id,
        amount=Decimal(str(amount)),
        date=transaction_date,
        created_at=created_at,
        updated_at=created_at,
        icon=icon,
        category=category,
        description=description,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def get_dashboard(client, auth_user):
    response = client.get(
        DASHBOARD_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200, response.text

    return response.json()


def decimal_value(value):
    return Decimal(str(value))


def get_week_dates():
    today = date.today()
    start_date = today - timedelta(days=6)

    return [
        start_date + timedelta(days=index)
        for index in range(7)
    ]


def get_week_amounts(items):
    return [
        decimal_value(item["total_amount"])
        for item in items
    ]


# ============================================================
# 1. Basic Endpoint Tests
# ============================================================


def test_get_dashboard_summary_success(client, auth_user):
    response = client.get(
        DASHBOARD_URL,
        headers=auth_user["headers"],
    )

    assert response.status_code == 200


def test_dashboard_summary_response_structure(client, auth_user):
    data = get_dashboard(client, auth_user)

    assert set(data.keys()) == {
        "total_transaction",
        "recent_transactions",
        "one_week_income",
        "one_week_expense",
    }

    assert isinstance(data["total_transaction"], dict)
    assert isinstance(data["recent_transactions"], list)
    assert isinstance(data["one_week_income"], list)
    assert isinstance(data["one_week_expense"], list)


def test_dashboard_summary_for_new_user(client, auth_user):
    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(total["total_income"]) == Decimal("0")
    assert decimal_value(total["total_expense"]) == Decimal("0")
    assert decimal_value(total["total_balance"]) == Decimal("0")

    assert data["recent_transactions"] == []

    assert len(data["one_week_income"]) == 7
    assert len(data["one_week_expense"]) == 7

    assert all(
        decimal_value(day["total_amount"]) == Decimal("0")
        for day in data["one_week_income"]
    )

    assert all(
        decimal_value(day["total_amount"]) == Decimal("0")
        for day in data["one_week_expense"]
    )


# ============================================================
# 2. Authentication Tests
# ============================================================


def test_dashboard_without_authentication(client):
    response = client.get(DASHBOARD_URL)

    assert response.status_code == 401


def test_dashboard_with_invalid_token(client):
    response = client.get(
        DASHBOARD_URL,
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_dashboard_with_malformed_authorization_header(client):
    response = client.get(
        DASHBOARD_URL,
        headers={
            "Authorization": "InvalidHeader",
        },
    )

    assert response.status_code in {
        401,
        403,
    }


# ============================================================
# 3. Total Transaction Tests
# ============================================================


def test_dashboard_total_income(client, db, auth_user):
    user_id = auth_user["user"]["id"]

    create_income(db, user_id, amount="100.00")
    create_income(db, user_id, amount="200.00")
    create_income(db, user_id, amount="300.00")

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("600.00")


def test_dashboard_total_expense(client, db, auth_user):
    user_id = auth_user["user"]["id"]

    create_expense(db, user_id, amount="100.00")
    create_expense(db, user_id, amount="200.00")
    create_expense(db, user_id, amount="300.00")

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_expense"]
    ) == Decimal("600.00")


def test_dashboard_total_balance(client, db, auth_user):
    user_id = auth_user["user"]["id"]

    create_income(db, user_id, amount="1000.00")
    create_expense(db, user_id, amount="400.00")

    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) == Decimal("1000.00")

    assert decimal_value(
        total["total_expense"]
    ) == Decimal("400.00")

    assert decimal_value(
        total["total_balance"]
    ) == Decimal("600.00")


def test_dashboard_negative_balance(client, db, auth_user):
    user_id = auth_user["user"]["id"]

    create_income(db, user_id, amount="500.00")
    create_expense(db, user_id, amount="1000.00")

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_balance"]
    ) == Decimal("-500.00")


def test_dashboard_zero_income_with_expenses(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="500.00",
    )

    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) == Decimal("0")

    assert decimal_value(
        total["total_expense"]
    ) > Decimal("0")

    assert decimal_value(
        total["total_balance"]
    ) < Decimal("0")


def test_dashboard_income_with_zero_expenses(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="1000.00",
    )

    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) > Decimal("0")

    assert decimal_value(
        total["total_expense"]
    ) == Decimal("0")

    assert decimal_value(
        total["total_balance"]
    ) == decimal_value(
        total["total_income"]
    )


def test_dashboard_decimal_total_accuracy(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(db, user_id, amount="10.10")
    create_income(db, user_id, amount="20.20")
    create_income(db, user_id, amount="30.30")

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("60.60")


def test_dashboard_large_transaction_amounts(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="9999999999.99",
    )

    create_expense(
        db,
        user_id,
        amount="1.99",
    )

    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) == Decimal("9999999999.99")

    assert decimal_value(
        total["total_expense"]
    ) == Decimal("1.99")

    assert decimal_value(
        total["total_balance"]
    ) == Decimal("9999999998.00")


# ============================================================
# 4. Total Transactions Must Include All Dates
# ============================================================


def test_dashboard_total_income_includes_old_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="1000.00",
        transaction_date=date(2020, 1, 1),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("1000.00")


def test_dashboard_total_expense_includes_old_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="500.00",
        transaction_date=date(2020, 1, 1),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_expense"]
    ) == Decimal("500.00")


def test_dashboard_totals_include_future_dated_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    tomorrow = date.today() + timedelta(days=1)

    create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=tomorrow,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("500.00")


# ============================================================
# 5. One Week Income Tests
# ============================================================


def test_dashboard_one_week_income_returns_seven_days(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    assert len(data["one_week_income"]) == 7


def test_dashboard_one_week_income_date_range(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    expected_dates = [
        current_date.isoformat()
        for current_date in get_week_dates()
    ]

    actual_dates = [
        item["date"]
        for item in data["one_week_income"]
    ]

    assert actual_dates == expected_dates


def test_dashboard_one_week_income_dates_are_sorted(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    dates = [
        item["date"]
        for item in data["one_week_income"]
    ]

    assert dates == sorted(dates)


def test_dashboard_one_week_income_all_days_have_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    expected_amounts = []

    for index, current_date in enumerate(
        get_week_dates(),
        start=1,
    ):
        amount = Decimal(index * 100)

        create_income(
            db,
            user_id,
            amount=amount,
            transaction_date=current_date,
        )

        expected_amounts.append(amount)

    data = get_dashboard(client, auth_user)

    assert get_week_amounts(
        data["one_week_income"]
    ) == expected_amounts


def test_dashboard_one_week_income_fills_missing_days_with_zero(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    dates = get_week_dates()

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=dates[0],
    )

    create_income(
        db,
        user_id,
        amount="200.00",
        transaction_date=dates[2],
    )

    create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=dates[5],
    )

    data = get_dashboard(client, auth_user)

    assert get_week_amounts(
        data["one_week_income"]
    ) == [
        Decimal("100.00"),
        Decimal("0"),
        Decimal("200.00"),
        Decimal("0"),
        Decimal("0"),
        Decimal("500.00"),
        Decimal("0"),
    ]


def test_dashboard_one_week_income_sums_same_day_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    today = date.today()

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=today,
    )

    create_income(
        db,
        user_id,
        amount="200.00",
        transaction_date=today,
    )

    create_income(
        db,
        user_id,
        amount="300.00",
        transaction_date=today,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][-1]["total_amount"]
    ) == Decimal("600.00")


def test_dashboard_one_week_income_excludes_old_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    old_date = date.today() - timedelta(days=7)

    create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=old_date,
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_income"]
    )


def test_dashboard_one_week_income_includes_start_date(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    start_date = date.today() - timedelta(days=6)

    create_income(
        db,
        user_id,
        amount="700.00",
        transaction_date=start_date,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][0]["total_amount"]
    ) == Decimal("700.00")


def test_dashboard_one_week_income_includes_today(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][-1]["total_amount"]
    ) == Decimal("500.00")


def test_dashboard_one_week_income_excludes_future_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="999.00",
        transaction_date=date.today() + timedelta(days=1),
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_income"]
    )


def test_dashboard_one_week_income_empty_history(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    result = data["one_week_income"]

    assert len(result) == 7

    assert all(
        decimal_value(day["total_amount"]) == Decimal("0")
        for day in result
    )


# ============================================================
# 6. One Week Expense Tests
# ============================================================


def test_dashboard_one_week_expense_returns_seven_days(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    assert len(data["one_week_expense"]) == 7


def test_dashboard_one_week_expense_date_range(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    expected_dates = [
        current_date.isoformat()
        for current_date in get_week_dates()
    ]

    actual_dates = [
        item["date"]
        for item in data["one_week_expense"]
    ]

    assert actual_dates == expected_dates


def test_dashboard_one_week_expense_dates_are_sorted(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    dates = [
        item["date"]
        for item in data["one_week_expense"]
    ]

    assert dates == sorted(dates)


def test_dashboard_one_week_expense_all_days_have_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    expected_amounts = []

    for index, current_date in enumerate(
        get_week_dates(),
        start=1,
    ):
        amount = Decimal(index * 100)

        create_expense(
            db,
            user_id,
            amount=amount,
            transaction_date=current_date,
        )

        expected_amounts.append(amount)

    data = get_dashboard(client, auth_user)

    assert get_week_amounts(
        data["one_week_expense"]
    ) == expected_amounts


def test_dashboard_one_week_expense_fills_missing_days_with_zero(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    dates = get_week_dates()

    create_expense(
        db,
        user_id,
        amount="100.00",
        transaction_date=dates[0],
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=dates[2],
    )

    create_expense(
        db,
        user_id,
        amount="500.00",
        transaction_date=dates[5],
    )

    data = get_dashboard(client, auth_user)

    assert get_week_amounts(
        data["one_week_expense"]
    ) == [
        Decimal("100.00"),
        Decimal("0"),
        Decimal("200.00"),
        Decimal("0"),
        Decimal("0"),
        Decimal("500.00"),
        Decimal("0"),
    ]


def test_dashboard_one_week_expense_sums_same_day_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    today = date.today()

    create_expense(
        db,
        user_id,
        amount="100.00",
        transaction_date=today,
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=today,
    )

    create_expense(
        db,
        user_id,
        amount="300.00",
        transaction_date=today,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_expense"][-1]["total_amount"]
    ) == Decimal("600.00")


def test_dashboard_one_week_expense_excludes_old_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="500.00",
        transaction_date=date.today() - timedelta(days=7),
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_expense"]
    )


def test_dashboard_one_week_expense_includes_start_date(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    start_date = date.today() - timedelta(days=6)

    create_expense(
        db,
        user_id,
        amount="700.00",
        transaction_date=start_date,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_expense"][0]["total_amount"]
    ) == Decimal("700.00")


def test_dashboard_one_week_expense_includes_today(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="500.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_expense"][-1]["total_amount"]
    ) == Decimal("500.00")


def test_dashboard_one_week_expense_excludes_future_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="999.00",
        transaction_date=date.today() + timedelta(days=1),
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_expense"]
    )


def test_dashboard_one_week_expense_empty_history(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    result = data["one_week_expense"]

    assert len(result) == 7

    assert all(
        decimal_value(day["total_amount"]) == Decimal("0")
        for day in result
    )


# ============================================================
# 7. Recent Transactions Tests
# ============================================================


def test_dashboard_recent_transactions_empty(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    assert data["recent_transactions"] == []


def test_dashboard_recent_transactions_income(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="100.00",
    )

    data = get_dashboard(client, auth_user)

    assert len(
        data["recent_transactions"]
    ) == 1

    assert (
        data["recent_transactions"][0]["type"]
        == "income"
    )


def test_dashboard_recent_transactions_expense(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="100.00",
    )

    data = get_dashboard(client, auth_user)

    assert len(
        data["recent_transactions"]
    ) == 1

    assert (
        data["recent_transactions"][0]["type"]
        == "expense"
    )


def test_dashboard_recent_transactions_combines_income_and_expense(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="100.00",
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
    )

    data = get_dashboard(client, auth_user)

    types = {
        item["type"]
        for item in data["recent_transactions"]
    }

    assert types == {
        "income",
        "expense",
    }


def test_dashboard_recent_transactions_returns_maximum_five(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    for index in range(10):
        create_income(
            db,
            user_id,
            amount=str(index + 1),
            transaction_date=(
                date.today()
                - timedelta(days=index)
            ),
        )

    data = get_dashboard(client, auth_user)

    assert len(
        data["recent_transactions"]
    ) == 5


def test_dashboard_recent_transactions_returns_available_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(db, user_id)
    create_expense(db, user_id)
    create_income(db, user_id)

    data = get_dashboard(client, auth_user)

    assert len(
        data["recent_transactions"]
    ) == 3


def test_dashboard_recent_transactions_orders_by_date(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    oldest = create_income(
        db,
        user_id,
        transaction_date=date.today() - timedelta(days=2),
    )

    middle = create_expense(
        db,
        user_id,
        transaction_date=date.today() - timedelta(days=1),
    )

    newest = create_income(
        db,
        user_id,
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    transactions = data["recent_transactions"]

    assert transactions[0]["transaction_id"] == newest.id
    assert transactions[1]["transaction_id"] == middle.id
    assert transactions[2]["transaction_id"] == oldest.id


def test_dashboard_recent_transactions_same_date_orders_by_created_at(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    transaction_date = date.today()

    first = create_income(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    second = create_expense(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            11,
            0,
            tzinfo=timezone.utc,
        ),
    )

    third = create_income(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert ids == [
        f"income-{third.id}",
        f"expense-{second.id}",
        f"income-{first.id}",
    ]


def test_dashboard_recent_transactions_transaction_date_has_priority_over_created_at(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    transaction_a = create_income(
        db,
        user_id,
        transaction_date=date.today(),
        created_at=datetime(
            2026,
            9,
            1,
            tzinfo=timezone.utc,
        ),
    )

    transaction_b = create_expense(
        db,
        user_id,
        transaction_date=date.today() - timedelta(days=1),
        created_at=datetime(
            2026,
            9,
            12,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert ids[0] == f"income-{transaction_a.id}"
    assert ids[1] == f"expense-{transaction_b.id}"


def test_dashboard_recent_transactions_old_transaction_added_today(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    old_transaction = create_income(
        db,
        user_id,
        transaction_date=date.today() - timedelta(days=10),
        created_at=datetime.now(timezone.utc),
    )

    new_transaction = create_expense(
        db,
        user_id,
        transaction_date=date.today(),
        created_at=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    assert (
        data["recent_transactions"][0]["id"]
        == f"expense-{new_transaction.id}"
    )

    assert (
        data["recent_transactions"][1]["id"]
        == f"income-{old_transaction.id}"
    )


def test_dashboard_recent_transactions_newer_date_with_older_created_at(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    newer_transaction = create_income(
        db,
        user_id,
        transaction_date=date.today(),
        created_at=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    older_transaction = create_expense(
        db,
        user_id,
        transaction_date=date.today() - timedelta(days=1),
        created_at=datetime.now(timezone.utc),
    )

    data = get_dashboard(client, auth_user)

    assert (
        data["recent_transactions"][0]["id"]
        == f"income-{newer_transaction.id}"
    )

    assert (
        data["recent_transactions"][1]["id"]
        == f"expense-{older_transaction.id}"
    )


def test_dashboard_recent_transactions_selects_correct_top_five_from_combined_transactions(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    base_date = date.today()

    expected = []

    for index in range(10):
        income = create_income(
            db,
            user_id,
            amount=str(index + 1),
            transaction_date=base_date - timedelta(days=index),
            created_at=datetime(
                2026,
                1,
                1,
                index % 24,
                0,
                tzinfo=timezone.utc,
            ),
        )

        expected.append(
            (
                income.date,
                income.created_at,
                f"income-{income.id}",
            )
        )

    for index in range(10):
        expense = create_expense(
            db,
            user_id,
            amount=str(index + 1),
            transaction_date=base_date - timedelta(days=index),
            created_at=datetime(
                2026,
                2,
                1,
                index % 24,
                0,
                tzinfo=timezone.utc,
            ),
        )

        expected.append(
            (
                expense.date,
                expense.created_at,
                f"expense-{expense.id}",
            )
        )

    expected_top_five = [
        item[2]
        for item in sorted(
            expected,
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )[:5]
    ]

    data = get_dashboard(client, auth_user)

    actual_ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert actual_ids == expected_top_five


def test_dashboard_recent_transactions_income_only_top_five(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    created = []

    for index in range(10):
        income = create_income(
            db,
            user_id,
            transaction_date=(
                date.today()
                - timedelta(days=index)
            ),
        )

        created.append(income)

    data = get_dashboard(client, auth_user)

    expected_ids = [
        f"income-{income.id}"
        for income in created[:5]
    ]

    actual_ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert actual_ids == expected_ids


def test_dashboard_recent_transactions_expense_only_top_five(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    created = []

    for index in range(10):
        expense = create_expense(
            db,
            user_id,
            transaction_date=(
                date.today()
                - timedelta(days=index)
            ),
        )

        created.append(expense)

    data = get_dashboard(client, auth_user)

    expected_ids = [
        f"expense-{expense.id}"
        for expense in created[:5]
    ]

    actual_ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert actual_ids == expected_ids


def test_dashboard_recent_transaction_transaction_id(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
    )

    data = get_dashboard(client, auth_user)

    transaction = data["recent_transactions"][0]

    assert transaction["transaction_id"] == income.id


def test_dashboard_recent_transaction_income_unique_id(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
    )

    data = get_dashboard(client, auth_user)

    assert (
        data["recent_transactions"][0]["id"]
        == f"income-{income.id}"
    )


def test_dashboard_recent_transaction_expense_unique_id(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    expense = create_expense(
        db,
        user_id,
    )

    data = get_dashboard(client, auth_user)

    assert (
        data["recent_transactions"][0]["id"]
        == f"expense-{expense.id}"
    )


def test_dashboard_recent_transactions_unique_ids_across_income_and_expense(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    expense = create_expense(
        db,
        user_id,
        created_at=datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    ids = {
        item["id"]
        for item in data["recent_transactions"]
    }

    assert f"income-{income.id}" in ids
    assert f"expense-{expense.id}" in ids


def test_dashboard_recent_transaction_returns_icon(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
        icon="income-custom-icon",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    expense = create_expense(
        db,
        user_id,
        icon="expense-custom-icon",
        created_at=datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    icons = {
        item["id"]: item["icon"]
        for item in data["recent_transactions"]
    }

    assert (
        icons[f"income-{income.id}"]
        == "income-custom-icon"
    )

    assert (
        icons[f"expense-{expense.id}"]
        == "expense-custom-icon"
    )


def test_dashboard_recent_transaction_amount(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
        amount="123.45",
    )

    data = get_dashboard(client, auth_user)

    transaction = next(
        item
        for item in data["recent_transactions"]
        if item["id"] == f"income-{income.id}"
    )

    assert decimal_value(
        transaction["amount"]
    ) == Decimal("123.45")


def test_dashboard_recent_transaction_type(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    income = create_income(
        db,
        user_id,
    )

    expense = create_expense(
        db,
        user_id,
    )

    data = get_dashboard(client, auth_user)

    transactions = {
        item["id"]: item["type"]
        for item in data["recent_transactions"]
    }

    assert (
        transactions[f"income-{income.id}"]
        == "income"
    )

    assert (
        transactions[f"expense-{expense.id}"]
        == "expense"
    )


# ============================================================
# 8. User Isolation Tests
# ============================================================


def test_dashboard_user_isolation_totals(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_a_id = auth_user["user"]["id"]
    user_b_id = second_auth_user["user"]["id"]

    create_income(
        db,
        user_a_id,
        amount="1000.00",
    )

    create_income(
        db,
        user_b_id,
        amount="5000.00",
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("1000.00")


def test_dashboard_user_isolation_one_week_income(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_a_id = auth_user["user"]["id"]
    user_b_id = second_auth_user["user"]["id"]

    create_income(
        db,
        user_a_id,
        amount="100.00",
        transaction_date=date.today(),
    )

    create_income(
        db,
        user_b_id,
        amount="999.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][-1]["total_amount"]
    ) == Decimal("100.00")


def test_dashboard_user_isolation_one_week_expense(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_a_id = auth_user["user"]["id"]
    user_b_id = second_auth_user["user"]["id"]

    create_expense(
        db,
        user_a_id,
        amount="100.00",
        transaction_date=date.today(),
    )

    create_expense(
        db,
        user_b_id,
        amount="999.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_expense"][-1]["total_amount"]
    ) == Decimal("100.00")


def test_dashboard_user_isolation_recent_transactions(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_a_id = auth_user["user"]["id"]
    user_b_id = second_auth_user["user"]["id"]

    own_income = create_income(
        db,
        user_a_id,
    )

    other_income = create_income(
        db,
        user_b_id,
    )

    data = get_dashboard(client, auth_user)

    ids = {
        item["id"]
        for item in data["recent_transactions"]
    }

    assert f"income-{own_income.id}" in ids
    assert f"income-{other_income.id}" not in ids


def test_dashboard_complete_user_data_isolation(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_a_id = auth_user["user"]["id"]
    user_b_id = second_auth_user["user"]["id"]

    own_income = create_income(
        db,
        user_a_id,
        amount="1000.00",
        transaction_date=date.today(),
    )

    own_expense = create_expense(
        db,
        user_a_id,
        amount="200.00",
        transaction_date=date.today(),
    )

    other_income = create_income(
        db,
        user_b_id,
        amount="5000.00",
        transaction_date=date.today(),
    )

    other_expense = create_expense(
        db,
        user_b_id,
        amount="3000.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) == Decimal("1000.00")

    assert decimal_value(
        total["total_expense"]
    ) == Decimal("200.00")

    assert decimal_value(
        total["total_balance"]
    ) == Decimal("800.00")

    assert decimal_value(
        data["one_week_income"][-1]["total_amount"]
    ) == Decimal("1000.00")

    assert decimal_value(
        data["one_week_expense"][-1]["total_amount"]
    ) == Decimal("200.00")

    ids = {
        item["id"]
        for item in data["recent_transactions"]
    }

    assert f"income-{own_income.id}" in ids
    assert f"expense-{own_expense.id}" in ids

    assert f"income-{other_income.id}" not in ids
    assert f"expense-{other_expense.id}" not in ids


# ============================================================
# 9. Income and Expense Independence Tests
# ============================================================


def test_dashboard_income_graph_ignores_expenses(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_expense(
        db,
        user_id,
        amount="500.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_income"]
    )


def test_dashboard_expense_graph_ignores_incomes(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_expense"]
    )


def test_dashboard_total_income_ignores_expenses(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="1000.00",
    )

    create_expense(
        db,
        user_id,
        amount="500.00",
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_income"]
    ) == Decimal("1000.00")


def test_dashboard_total_expense_ignores_income(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="1000.00",
    )

    create_expense(
        db,
        user_id,
        amount="500.00",
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["total_transaction"]["total_expense"]
    ) == Decimal("500.00")


# ============================================================
# 10. Boundary Date Tests
# ============================================================


def test_dashboard_week_boundary_today_minus_seven_excluded(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    boundary_date = (
        date.today()
        - timedelta(days=7)
    )

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=boundary_date,
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=boundary_date,
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_income"]
    )

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_expense"]
    )


def test_dashboard_week_boundary_today_minus_six_included(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    boundary_date = (
        date.today()
        - timedelta(days=6)
    )

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=boundary_date,
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=boundary_date,
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][0]["total_amount"]
    ) == Decimal("100.00")

    assert decimal_value(
        data["one_week_expense"][0]["total_amount"]
    ) == Decimal("200.00")


def test_dashboard_week_boundary_today_included(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=date.today(),
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    assert decimal_value(
        data["one_week_income"][-1]["total_amount"]
    ) == Decimal("100.00")

    assert decimal_value(
        data["one_week_expense"][-1]["total_amount"]
    ) == Decimal("200.00")


def test_dashboard_week_boundary_tomorrow_excluded(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    tomorrow = (
        date.today()
        + timedelta(days=1)
    )

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=tomorrow,
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=tomorrow,
    )

    data = get_dashboard(client, auth_user)

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_income"]
    )

    assert all(
        decimal_value(item["total_amount"]) == Decimal("0")
        for item in data["one_week_expense"]
    )


# ============================================================
# 11. Mixed Complete Dashboard Test
# ============================================================


def test_dashboard_complete_realistic_data(
    client,
    db,
    auth_user,
    second_auth_user,
):
    user_id = auth_user["user"]["id"]
    other_user_id = second_auth_user["user"]["id"]

    dates = get_week_dates()

    # --------------------------------------------------------
    # Income
    # --------------------------------------------------------

    income_day_1 = create_income(
        db,
        user_id,
        amount="1000.00",
        transaction_date=dates[0],
        icon="salary-icon",
    )

    income_day_3 = create_income(
        db,
        user_id,
        amount="500.00",
        transaction_date=dates[2],
        icon="freelance-icon",
    )

    income_day_7 = create_income(
        db,
        user_id,
        amount="200.00",
        transaction_date=dates[6],
        icon="bonus-icon",
    )

    # Same-day income transaction
    same_day_income = create_income(
        db,
        user_id,
        amount="50.00",
        transaction_date=dates[6],
        icon="extra-income-icon",
    )

    # --------------------------------------------------------
    # Expenses
    # --------------------------------------------------------

    expense_day_2 = create_expense(
        db,
        user_id,
        amount="300.00",
        transaction_date=dates[1],
        icon="food-icon",
    )

    expense_day_4 = create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=dates[3],
        icon="travel-icon",
    )

    expense_day_7 = create_expense(
        db,
        user_id,
        amount="100.00",
        transaction_date=dates[6],
        icon="shopping-icon",
    )

    # --------------------------------------------------------
    # Older transactions
    # Included in totals and recent transactions,
    # excluded from weekly graphs
    # --------------------------------------------------------

    old_income = create_income(
        db,
        user_id,
        amount="1000.00",
        transaction_date=date.today() - timedelta(days=30),
        icon="old-income-icon",
    )

    old_expense = create_expense(
        db,
        user_id,
        amount="400.00",
        transaction_date=date.today() - timedelta(days=30),
        icon="old-expense-icon",
    )

    # --------------------------------------------------------
    # Future transactions
    # Included in totals and recent transactions,
    # excluded from weekly graphs
    # --------------------------------------------------------

    future_income = create_income(
        db,
        user_id,
        amount="700.00",
        transaction_date=date.today() + timedelta(days=1),
        icon="future-income-icon",
    )

    future_expense = create_expense(
        db,
        user_id,
        amount="250.00",
        transaction_date=date.today() + timedelta(days=1),
        icon="future-expense-icon",
    )

    # --------------------------------------------------------
    # Other user transactions
    # --------------------------------------------------------

    other_income = create_income(
        db,
        other_user_id,
        amount="9999.00",
        transaction_date=date.today(),
    )

    other_expense = create_expense(
        db,
        other_user_id,
        amount="8888.00",
        transaction_date=date.today(),
    )

    data = get_dashboard(client, auth_user)

    # --------------------------------------------------------
    # Totals
    # --------------------------------------------------------

    expected_total_income = Decimal(
        "3450.00"
    )

    expected_total_expense = Decimal(
        "1250.00"
    )

    expected_balance = Decimal(
        "2200.00"
    )

    total = data["total_transaction"]

    assert decimal_value(
        total["total_income"]
    ) == expected_total_income

    assert decimal_value(
        total["total_expense"]
    ) == expected_total_expense

    assert decimal_value(
        total["total_balance"]
    ) == expected_balance

    # --------------------------------------------------------
    # Weekly Income
    # --------------------------------------------------------

    assert len(
        data["one_week_income"]
    ) == 7

    assert get_week_amounts(
        data["one_week_income"]
    ) == [
        Decimal("1000.00"),
        Decimal("0"),
        Decimal("500.00"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
        Decimal("250.00"),
    ]

    # --------------------------------------------------------
    # Weekly Expense
    # --------------------------------------------------------

    assert len(
        data["one_week_expense"]
    ) == 7

    assert get_week_amounts(
        data["one_week_expense"]
    ) == [
        Decimal("0"),
        Decimal("300.00"),
        Decimal("0"),
        Decimal("200.00"),
        Decimal("0"),
        Decimal("0"),
        Decimal("100.00"),
    ]

    # --------------------------------------------------------
    # Recent Transactions
    # --------------------------------------------------------

    assert len(
        data["recent_transactions"]
    ) <= 5

    recent_ids = {
        item["id"]
        for item in data["recent_transactions"]
    }

    # Current user's transactions may appear
    assert all(
        item["id"].startswith(
            ("income-", "expense-")
        )
        for item in data["recent_transactions"]
    )

    # Other user's transactions must never appear
    assert (
        f"income-{other_income.id}"
        not in recent_ids
    )

    assert (
        f"expense-{other_expense.id}"
        not in recent_ids
    )

    # Verify current user's future transactions are candidates
    # for recent transactions because recent transaction logic
    # has no date filter.
    expected_possible_ids = {
        f"income-{income_day_1.id}",
        f"income-{income_day_3.id}",
        f"income-{income_day_7.id}",
        f"income-{same_day_income.id}",
        f"income-{old_income.id}",
        f"income-{future_income.id}",
        f"expense-{expense_day_2.id}",
        f"expense-{expense_day_4.id}",
        f"expense-{expense_day_7.id}",
        f"expense-{old_expense.id}",
        f"expense-{future_expense.id}",
    }

    assert recent_ids.issubset(
        expected_possible_ids
    )


# ============================================================
# 12. Response Schema Tests
# ============================================================


def test_dashboard_response_data_types(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    assert isinstance(
        data["total_transaction"],
        dict,
    )

    assert isinstance(
        data["recent_transactions"],
        list,
    )

    assert isinstance(
        data["one_week_income"],
        list,
    )

    assert isinstance(
        data["one_week_expense"],
        list,
    )


def test_dashboard_decimal_response_serialization(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="10.10",
    )

    create_income(
        db,
        user_id,
        amount="20.20",
    )

    data = get_dashboard(client, auth_user)

    total_income = data[
        "total_transaction"
    ]["total_income"]

    assert decimal_value(
        total_income
    ) == Decimal("30.30")

    assert decimal_value(
        data["recent_transactions"][0]["amount"]
    ).as_tuple().exponent >= -2


def test_dashboard_date_response_serialization(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    today = date.today()

    create_income(
        db,
        user_id,
        transaction_date=today,
    )

    data = get_dashboard(client, auth_user)

    for item in data["one_week_income"]:
        assert len(item["date"]) == 10

        datetime.strptime(
            item["date"],
            "%Y-%m-%d",
        )

    transaction = data[
        "recent_transactions"
    ][0]

    assert transaction["date"] == today.isoformat()


def test_dashboard_recent_transaction_response_schema(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    create_income(
        db,
        user_id,
        amount="100.00",
        icon="test-icon",
    )

    data = get_dashboard(client, auth_user)

    transaction = data[
        "recent_transactions"
    ][0]

    assert set(
        transaction.keys()
    ) == {
        "id",
        "transaction_id",
        "icon",
        "date",
        "amount",
        "type",
    }

    assert isinstance(
        transaction["id"],
        str,
    )

    assert isinstance(
        transaction["transaction_id"],
        int,
    )

    assert isinstance(
        transaction["icon"],
        str,
    )

    assert isinstance(
        transaction["date"],
        str,
    )

    assert isinstance(
        transaction["type"],
        str,
    )

    assert transaction["type"] in {
        "income",
        "expense",
    }


# ============================================================
# 13. Regression Tests for Fixed Bugs
# ============================================================


def test_dashboard_week_data_never_returns_eight_days(
    client,
    auth_user,
):
    data = get_dashboard(client, auth_user)

    assert len(
        data["one_week_income"]
    ) == 7

    assert len(
        data["one_week_expense"]
    ) == 7


def test_dashboard_missing_days_are_not_omitted(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    dates = get_week_dates()

    create_income(
        db,
        user_id,
        amount="100.00",
        transaction_date=dates[0],
    )

    create_expense(
        db,
        user_id,
        amount="200.00",
        transaction_date=dates[6],
    )

    data = get_dashboard(client, auth_user)

    assert len(
        data["one_week_income"]
    ) == 7

    assert len(
        data["one_week_expense"]
    ) == 7

    expected_dates = [
        current_date.isoformat()
        for current_date in dates
    ]

    assert [
        item["date"]
        for item in data["one_week_income"]
    ] == expected_dates

    assert [
        item["date"]
        for item in data["one_week_expense"]
    ] == expected_dates


def test_dashboard_recent_transactions_combined_sort_uses_created_at(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    transaction_date = date.today()

    oldest = create_income(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    middle = create_expense(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            11,
            0,
            tzinfo=timezone.utc,
        ),
    )

    newest = create_income(
        db,
        user_id,
        transaction_date=transaction_date,
        created_at=datetime(
            2026,
            1,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    data = get_dashboard(client, auth_user)

    ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert ids == [
        f"income-{newest.id}",
        f"expense-{middle.id}",
        f"income-{oldest.id}",
    ]


def test_dashboard_recent_transaction_ids_are_unique(
    client,
    db,
    auth_user,
):
    user_id = auth_user["user"]["id"]

    for index in range(3):
        create_income(
            db,
            user_id,
            transaction_date=(
                date.today()
                - timedelta(days=index)
            ),
        )

    for index in range(3):
        create_expense(
            db,
            user_id,
            transaction_date=(
                date.today()
                - timedelta(days=index)
            ),
        )

    data = get_dashboard(client, auth_user)

    ids = [
        item["id"]
        for item in data["recent_transactions"]
    ]

    assert len(ids) == len(set(ids))