from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.income.schemas.UpdateRequest.update_request import UpdateIncomeRequest


def update_income(
    income_id: int,
    income_update: UpdateIncomeRequest,
    db: Session,
    current_user: User,
):
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

    update_data = income_update.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="At least one field is required to update the income",
        )

    has_changes = False

    for key, value in update_data.items():
        if getattr(income, key) != value:
            setattr(income, key, value)
            has_changes = True

    if not has_changes:
        raise HTTPException(
            status_code=400,
            detail="No changes detected in the income",
        )

    try:
        db.commit()
        db.refresh(income)

    except Exception:
        db.rollback()
        raise

    return income