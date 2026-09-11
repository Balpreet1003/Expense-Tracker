from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense
from app.features.expense.schemas.UpdateRequest.update_request import UpdateExpenseRequest


def update_expense(
    expense_id: int,
    expense_update: UpdateExpenseRequest,
    db: Session,
    current_user: User,
):
    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    )

    expense = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found",
        )

    update_data = expense_update.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to update the expense",
        )

    has_changes = False

    for key, value in update_data.items():
        if getattr(expense, key) != value:
            setattr(expense, key, value)
            has_changes = True

    if not has_changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No changes detected in the expense",
        )
    
    try:
        db.commit()
        db.refresh(expense)

    except Exception:
        db.rollback()
        raise

    return expense