from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.income.schemas.UpdateRequest.update_request import UpdateIncomeRequest
from app.features.income.schemas.Response.response import IncomeResponse
from app.features.income.services.Update.update_income_service import update_income as update_income_service

router = APIRouter()

@router.patch(
    "/income/{income_id}",
    status_code=status.HTTP_200_OK,
    response_model=IncomeResponse
)
def update_income(
    income_id: int,
    income_data: UpdateIncomeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_income_service(
        income_id,
        income_data,
        db,
        current_user
    )