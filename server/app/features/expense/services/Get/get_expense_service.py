from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense


def get_expenses(
    db: Session,
    current_user: User,
):
    statement = (
        select(Expense)
        .where(
            Expense.user_id == current_user.id
        )
        .order_by(
            Expense.date.desc(),
            Expense.created_at.desc(),
        )
    )

    result = db.execute(statement)

    expenses = result.scalars().all()

    return expenses