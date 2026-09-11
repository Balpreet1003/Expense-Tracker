from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.services.Get.get_income_service import get_incomes
from app.features.expense.services.Get.get_expense_service import get_expenses
from app.features.transactions.schemas.Response.response import (
    IncomeTransactionResponse,
    ExpenseTransactionResponse
)

def get_transactions(
    db: Session,
    current_user: User
):
    incomes_response = get_incomes(
        db=db,
        current_user=current_user
    )

    expenses_response = get_expenses(
        db=db,
        current_user=current_user
    )

    incomes = [
        IncomeTransactionResponse.model_validate(incomes)
        for incomes in incomes_response
    ]
    expenses = [
        ExpenseTransactionResponse.model_validate(expenses)
        for expenses in expenses_response
    ]

    transactions = incomes + expenses

    transactions.sort(key=lambda x: (x.date, x.id), reverse=True)

    return transactions