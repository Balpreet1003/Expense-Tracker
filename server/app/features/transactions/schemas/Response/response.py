from typing import Annotated, Literal, Union
from pydantic import Field

from app.features.income.schemas.Response.response import IncomeResponse
from app.features.expense.schemas.Response.response import ExpenseResponse

class IncomeTransactionResponse(IncomeResponse):
    type: Literal["income"] = "income"

class ExpenseTransactionResponse(ExpenseResponse):
    type: Literal["expense"] = "expense"

TransactionResponse = Annotated[
    Union[
        IncomeTransactionResponse,
        ExpenseTransactionResponse,
    ],
    Field(discriminator="type")
]