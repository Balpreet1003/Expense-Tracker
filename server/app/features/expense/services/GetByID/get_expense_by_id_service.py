from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense


def get_expense_by_id(
    expense_id: int,
    db: Session,
    current_user: User,
):
    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    )

    result = db.execute(statement)

    expense = result.scalar_one_or_none()

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found",
        )

    return expense