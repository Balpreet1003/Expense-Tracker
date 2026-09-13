from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.models.user import User
from app.features.auth.dependencies.auth import get_current_user
from app.features.dashboard.schemas.SummaryResponse.summary_response import SummaryResponse 
from app.features.dashboard.services.summary_service import get_summary as get_summary_service

router = APIRouter()

@router.get(
    "/summary",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_summary_service(
        db,
        current_user
    )