from datetime import date as Date

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    date: Date
    category: str
    description: str

    model_config = {
        "from_attributes": True
    }