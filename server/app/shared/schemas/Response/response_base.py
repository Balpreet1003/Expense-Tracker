from datetime import date as Date, datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class ResponseBase(BaseModel):
    id: int
    icon: str
    amount: Decimal = Field(
        decimal_places = 2,
    )
    date: Date
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }