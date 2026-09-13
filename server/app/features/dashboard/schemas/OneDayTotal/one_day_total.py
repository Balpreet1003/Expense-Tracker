from datetime import date as Date
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal


class OneDayTotalResponse(BaseModel):
    date: Date
    total_amount: Decimal = Field(
        decimal_places = 2,
    )

class OneTransactionResponse(BaseModel):
    id: str
    transaction_id: int
    icon: str
    date: Date
    amount: Decimal = Field(
        decimal_places = 2,
    )
    type: Literal["income", "expense"]