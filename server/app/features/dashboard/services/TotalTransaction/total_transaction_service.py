from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.expense.models.expense import Expense
from app.features.dashboard.schemas.TotalResponse.total_transaction import TotalTransactionResponse


def get_total_transactions(
    db: Session,
    current_user: User,      
):

    #Total Income
    total_income_query = select(
        func.sum(Income.amount)
    ).where(
        Income.user_id == current_user.id
    )

    total_income = db.execute(total_income_query).scalar() or Decimal("0.0")

    #Total Expense
    total_expense_query = select(
        func.sum(Expense.amount)
    ).where(
        Expense.user_id == current_user.id
    )

    total_expense = db.execute(total_expense_query).scalar() or Decimal("0.0")

    #Total Balance
    total_balance = total_income - total_expense

    return TotalTransactionResponse(
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance
    )