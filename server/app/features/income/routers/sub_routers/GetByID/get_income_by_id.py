from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.income.services.GetByID.get_income_by_id_service import get_income_by_id as get_income_by_id_service
from app.features.income.schemas.Response.response import IncomeResponse

router = APIRouter()

@router.get(
    "/income/{income_id}",
    status_code=status.HTTP_200_OK,
    response_model=IncomeResponse
)
def get_income_by_id(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_income_by_id_service(
        income_id,
        db,
        current_user
    )