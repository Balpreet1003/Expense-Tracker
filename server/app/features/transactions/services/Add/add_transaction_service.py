from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.features.auth.models.user import User
from app.features.transactions.schemas.CreateRequest.create_request import CreateTransactionRequest
from app.features.income.services.Add.add_income_service import add_income
from app.features.expense.services.Add.add_expense_service import add_expense
from app.features.income.schemas.CreateRequest.create_request import CreateIncomeRequest
from app.features.expense.schemas.CreateRequest.create_request import CreateExpenseRequest
from app.features.transactions.schemas.Response.response import (
    IncomeTransactionResponse,
    ExpenseTransactionResponse,
)


def add_transaction(
    transaction_data: CreateTransactionRequest,
    db: Session,
    current_user: User,
):

    if transaction_data.type == "income":

        income_data = CreateIncomeRequest(
            amount=transaction_data.amount,
            date=transaction_data.date,
            source=transaction_data.source,
            description=transaction_data.description,
        )

        income_response = add_income(
            income_data=income_data,
            db=db,
            current_user=current_user,
        )

        return IncomeTransactionResponse.model_validate(income_response)

    elif transaction_data.type == "expense":

        expense_data = CreateExpenseRequest(
            amount=transaction_data.amount,
            date=transaction_data.date,
            category=transaction_data.category,
            description=transaction_data.description,
        )

        expense_response = add_expense(
            expense_data=expense_data,
            db=db,
            current_user=current_user,
        )

        return ExpenseTransactionResponse.model_validate(expense_response)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type",
        )