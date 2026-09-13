from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta

from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.dashboard.schemas.OneDayTotal.one_day_total import (
    OneDayTotalResponse,
)


def get_one_week_income(
    db: Session,
    current_user: User,
    today_date: date
):
    start_date = today_date - timedelta(days=6)

    # Generate exactly 7 days, including today
    date_list = [
        start_date + timedelta(days=i)
        for i in range(7)
    ]

    one_week_income_query = (
        select(
            Income.date,
            func.sum(Income.amount).label("total_income"),
        )
        .where(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date <= today_date,
        )
        .group_by(Income.date)
        .order_by(Income.date.asc())
    )

    one_week_income = db.execute(one_week_income_query).all()

    # Create a lookup dictionary from database results
    income_by_date = {
        income.date: income.total_income
        for income in one_week_income
    }

    # Return all 7 days, filling missing dates with 0
    return [
        OneDayTotalResponse(
            date=current_date,
            total_amount=income_by_date.get(current_date, 0),
        )
        for current_date in date_list
    ]