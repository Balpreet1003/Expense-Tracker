from typing import Annotated, Literal, Union
from pydantic import Field

from app.features.income.schemas.CreateRequest.create_request import CreateIncomeRequest
from app.features.expense.schemas.CreateRequest.create_request import CreateExpenseRequest


class IncomeTransactionRequest(CreateIncomeRequest):
    type: Literal["income"] = Field(...)


class ExpenseTransactionRequest(CreateExpenseRequest):
    type: Literal["expense"] = Field(...)


CreateTransactionRequest = Annotated[
    Union[
        IncomeTransactionRequest,
        ExpenseTransactionRequest,
    ],
    Field(discriminator="type"),
]