from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.models.income import Income


def delete_income(
    income_id: int,
    db: Session,
    current_user: User,
) -> None:

    statement = select(Income).where(
        Income.id == income_id,
        Income.user_id == current_user.id,
    )

    income = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if income is None:
        raise HTTPException(
            status_code=404,
            detail=f"Income with ID {income_id} not found",
        )

    try:
        db.delete(income)
        db.commit()

    except Exception:
        db.rollback()
        raise