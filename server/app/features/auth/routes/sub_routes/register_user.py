from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.schemas.schemas import (
    AuthResponse,
    RegisterRequest,
)
from app.features.auth.services.auth_service import register_user


router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    return register_user(
        register_data=register_data,
        db=db,
    )