from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.models.income import Income

def get_incomes(
    db: Session,
    current_user: User,
):
    statement = (
        select(Income)
        .where(
            Income.user_id == current_user.id
        )
        .order_by(
            Income.date.desc(),
            Income.id.desc(),
        )
    )

    result = db.execute(statement)

    incomes = result.scalars().all()

    return incomes