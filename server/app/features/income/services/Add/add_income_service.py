from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.income.schemas.CreateRequest.create_request import CreateIncomeRequest

def add_income(
    income_data: CreateIncomeRequest,
    db: Session,
    current_user: User,
):
    try:
        income = Income(
            amount=income_data.amount,
            date=income_data.date,
            source=income_data.source,
            description=income_data.description,
            user_id=current_user.id,
        )

        db.add(income)
        db.commit()
        db.refresh(income)

        return income

    except Exception:
        db.rollback()
        raise