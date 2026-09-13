from sqlalchemy.orm import Session
from sqlalchemy import select

from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.expense.models.expense import Expense
from app.features.dashboard.schemas.OneDayTotal.one_day_total import (
    OneTransactionResponse,
)


def get_recent_transactions(
    db: Session,
    current_user: User,
):
    # Recent Income Transactions
    recent_income_query = (
        select(Income)
        .where(
            Income.user_id == current_user.id
        )
        .order_by(
            Income.date.desc(),
            Income.created_at.desc(),
        )
        .limit(5)
    )

    recent_income_transactions = (
        db.execute(recent_income_query)
        .scalars()
        .all()
    )

    # Recent Expense Transactions
    recent_expense_query = (
        select(Expense)
        .where(
            Expense.user_id == current_user.id
        )
        .order_by(
            Expense.date.desc(),
            Expense.created_at.desc(),
        )
        .limit(5)
    )

    recent_expense_transactions = (
        db.execute(recent_expense_query)
        .scalars()
        .all()
    )

    # Combine database model objects
    recent_transactions = (
        recent_income_transactions
        + recent_expense_transactions
    )

    # Sort by transaction date first,
    # then created_at for transactions with the same date
    recent_transactions = sorted(
        recent_transactions,
        key=lambda transaction: (
            transaction.date,
            transaction.created_at,
        ),
        reverse=True,
    )[:5]

    # Convert to response schema after sorting
    return [
        OneTransactionResponse(
            id=(
                f"income-{transaction.id}"
                if isinstance(transaction, Income)
                else f"expense-{transaction.id}"
            ),
            transaction_id=transaction.id,
            icon=transaction.icon,
            date=transaction.date,
            amount=transaction.amount,
            type=(
                "income"
                if isinstance(transaction, Income)
                else "expense"
            ),
        )
        for transaction in recent_transactions
    ]