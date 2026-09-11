from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.income.services.Delete.delete_income_service import delete_income
from app.features.expense.services.Delete.delete_expense_service import delete_expense

def delete_transaction(
    transaction_type: str,
    transaction_id: int,
    db: Session,
    current_user: User
):
    if transaction_type == "income":
        delete_income(
            income_id=transaction_id,
            db=db,
            current_user=current_user
        )
    
    elif transaction_type == "expense":
        delete_expense(
            expense_id=transaction_id,
            db=db,
            current_user=current_user
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type. Must be 'income' or 'expense'."
        )