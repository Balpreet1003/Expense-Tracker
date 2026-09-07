from fastapi import APIRouter, Depends

from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.auth.schemas.schemas import UserResponse


router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user