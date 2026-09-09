from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.income.services.Get.get_income_service import get_incomes as get_incomes_service
from app.features.income.schemas.Response.response import IncomeResponse

router = APIRouter()

@router.get(
    "/income",
    status_code=status.HTTP_200_OK,
    response_model=list[IncomeResponse]
)
def get_incomes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_incomes_service(
        db,
        current_user
    )