from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.features.auth.models.user import User
from app.features.transactions.schemas.UpdateRequest.update_request import UpdateTransactionRequest
from app.features.income.services.Update.update_income_service import update_income
from app.features.expense.services.Update.update_expense_service import update_expense
from app.features.income.schemas.UpdateRequest.update_request import UpdateIncomeRequest
from app.features.expense.schemas.UpdateRequest.update_request import UpdateExpenseRequest
from app.features.transactions.schemas.Response.response import (
    IncomeTransactionResponse,
    ExpenseTransactionResponse
)

def update_transaction(
    transaction_type: str,
    transaction_id: int,
    transaction_data: UpdateTransactionRequest,
    db: Session,
    current_user: User,
):
    update_data = transaction_data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    try:
        if transaction_type == "income":

            income_data = UpdateIncomeRequest.model_validate(
                update_data
            )

            income_response = update_income(
                income_id=transaction_id,
                income_update=income_data,
                db=db,
                current_user=current_user,
            )

            return IncomeTransactionResponse.model_validate(
                income_response
            )

        elif transaction_type == "expense":

            expense_data = UpdateExpenseRequest.model_validate(
                update_data
            )

            expense_response = update_expense(
                expense_id=transaction_id,
                expense_update=expense_data,
                db=db,
                current_user=current_user,
            )

            return ExpenseTransactionResponse.model_validate(
                expense_response
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type",
        )

    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=jsonable_encoder(error.errors()),
        )