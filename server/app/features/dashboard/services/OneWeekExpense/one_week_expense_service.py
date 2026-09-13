from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta

from app.features.auth.models.user import User
from app.features.expense.models.expense import Expense
from app.features.dashboard.schemas.OneDayTotal.one_day_total import (
    OneDayTotalResponse,
)


def get_one_week_expense(
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

    one_week_expense_query = (
        select(
            Expense.date,
            func.sum(Expense.amount).label("total_expense"),
        )
        .where(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date <= today_date,
        )
        .group_by(Expense.date)
        .order_by(Expense.date.asc())
    )

    one_week_expense = db.execute(one_week_expense_query).all()

    # Create a lookup dictionary from database results
    expense_by_date = {
        expense.date: expense.total_expense
        for expense in one_week_expense
    }

    # Return all 7 days, filling missing dates with 0
    return [
        OneDayTotalResponse(
            date=current_date,
            total_amount=expense_by_date.get(current_date, 0),
        )
        for current_date in date_list
    ]