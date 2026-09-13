from datetime import date
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.dashboard.schemas.SummaryResponse.summary_response import SummaryResponse
from app.features.dashboard.services.TotalTransaction.total_transaction_service import get_total_transactions as get_total_transaction_service
from app.features.dashboard.services.OneWeekExpense.one_week_expense_service import get_one_week_expense as get_one_week_expense_service
from app.features.dashboard.services.OneWeekIncome.one_week_income_service import get_one_week_income as get_one_week_income_service
from app.features.dashboard.services.RecentTransactions.recent_transactions_service import get_recent_transactions as get_recent_transactions_service

def get_summary(
    db: Session,
    current_user: User
):
    today_date = date.today()
    
    total_transaction = get_total_transaction_service(db, current_user)
    recent_transactions = get_recent_transactions_service(db, current_user)
    one_week_income = get_one_week_income_service(db, current_user, today_date)
    one_week_expense = get_one_week_expense_service(db, current_user, today_date)

    return SummaryResponse(
        total_transaction=total_transaction,
        recent_transactions=recent_transactions,
        one_week_income=one_week_income,
        one_week_expense=one_week_expense
    )