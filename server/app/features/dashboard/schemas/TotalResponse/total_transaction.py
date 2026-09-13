from pydantic import BaseModel, Field
from decimal import Decimal


class TotalTransactionResponse(BaseModel):
    total_income: Decimal = Field(
        decimal_places = 2,
    )
    total_expense: Decimal = Field(
        decimal_places = 2,
    )
    total_balance: Decimal = Field(
        decimal_places = 2,
    )