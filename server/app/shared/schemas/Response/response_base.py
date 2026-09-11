from datetime import date as Date
from pydantic import BaseModel

class ResponseBase(BaseModel):
    id: int
    amount: float
    date: Date
    description: str

    model_config = {
        "from_attributes": True
    }