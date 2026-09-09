from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.income.schemas.CreateRequest.create_request import CreateIncomeRequest
from app.features.income.schemas.Response.response import IncomeResponse
from app.features.income.services.Add.add_income_service import add_income as add_income_service

router = APIRouter()

@router.post(
    "/income",
    response_model=IncomeResponse,
    status_code=status.HTTP_201_CREATED
)
def add_income(
    income_data: CreateIncomeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_income_service(
        income_data,
        db,
        current_user
    )