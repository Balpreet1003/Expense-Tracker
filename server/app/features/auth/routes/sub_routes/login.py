from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.schemas.schemas import AuthResponse, LoginRequest
from app.features.auth.services.auth_service import login_user


router = APIRouter()


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    return login_user(
        login_data=login_data,
        db=db,
    )