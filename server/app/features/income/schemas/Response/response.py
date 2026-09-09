from datetime import date as Date
from pydantic import BaseModel

class IncomeResponse(BaseModel):
    id: int
    amount: float
    date: Date
    source: str
    description: str

    model_config = {
        "from_attributes": True
    }