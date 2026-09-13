from pydantic import BaseModel

from app.features.dashboard.schemas.OneDayTotal.one_day_total import OneDayTotalResponse
from app.features.dashboard.schemas.OneDayTotal.one_day_total import OneTransactionResponse
from app.features.dashboard.schemas.TotalResponse.total_transaction import TotalTransactionResponse

class SummaryResponse(BaseModel):
    total_transaction: TotalTransactionResponse
    recent_transactions: list[OneTransactionResponse]
    one_week_income: list[OneDayTotalResponse]
    one_week_expense: list[OneDayTotalResponse]