from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.income.services.Delete.delete_income_service import delete_income as delete_income_service

router = APIRouter()

@router.delete(
    "/income/{income_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_income_service(
        income_id,
        db,
        current_user
    )