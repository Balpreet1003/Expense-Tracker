from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense
from app.features.expense.schemas.CreateRequest.create_request import CreateExpenseRequest

def add_expense(
    expense_data: CreateExpenseRequest,
    db: Session,
    current_user: User,
):
    try:
        expense = Expense(
            amount=expense_data.amount,
            date=expense_data.date,
            category=expense_data.category,
            description=expense_data.description,
            user_id=current_user.id,
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise