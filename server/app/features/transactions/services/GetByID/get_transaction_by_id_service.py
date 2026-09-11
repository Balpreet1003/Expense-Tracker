from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.features.auth.models.user import User
from app.features.income.services.GetByID.get_income_by_id_service import get_income_by_id
from app.features.expense.services.GetByID.get_expense_by_id_service import get_expense_by_id
from app.features.transactions.schemas.Response.response import (
    IncomeTransactionResponse,
    ExpenseTransactionResponse,
)

def get_transaction_by_id(
    transaction_type: str,
    transaction_id: int,
    db: Session,
    current_user: User
):
    if transaction_type == "income":
        income_response = get_income_by_id(
            income_id=transaction_id,
            db=db,
            current_user=current_user
        )

        return IncomeTransactionResponse.model_validate(income_response)
    
    elif transaction_type == "expense":
        expense_response = get_expense_by_id(
            expense_id=transaction_id,
            db=db,
            current_user=current_user
        )

        return ExpenseTransactionResponse.model_validate(expense_response)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type. Must be 'income' or 'expense'."
        )