from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense
from app.features.expense.schemas.UpdateRequest.update_request import UpdateExpenseRequest


def update_expense(
    expense_id: int,
    updated_data: UpdateExpenseRequest,
    db: Session,
    current_user: User,
):
    try:
        statement = select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id,
        )

        result = db.execute(statement)

        expense = result.scalar_one_or_none()

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail=f"Expense with ID {expense_id} not found",
            )

        update_data = updated_data.model_dump(
            exclude_unset=True,
        )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="At least one field is required to update the expense",
            )

        for key, value in update_data.items():
            setattr(expense, key, value)

        db.commit()
        db.refresh(expense)

        return expense

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise