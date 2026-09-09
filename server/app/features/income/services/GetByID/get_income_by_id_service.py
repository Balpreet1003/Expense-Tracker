from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.features.auth.models.user import User
from app.features.income.models.income import Income

def get_income_by_id(
    income_id: int,
    db: Session,
    current_user: User,
):
    statement = select(Income).where(
        Income.id == income_id,
        Income.user_id == current_user.id,
    )

    result = db.execute(statement)

    income = result.scalar_one_or_none()

    if income is None:
        raise HTTPException(
            status_code=404,
            detail=f"Income with ID {income_id} not found",
        )

    return income