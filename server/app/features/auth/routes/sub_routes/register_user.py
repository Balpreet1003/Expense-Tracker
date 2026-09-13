from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.features.auth.schemas.schemas import (
    AuthResponse,
    RegisterRequest,
)

from app.features.auth.services.auth_service import (
    register_user,
)


router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    full_name: str = Form(
        ...,
        min_length=1,
        max_length=100,
        alias="fullName",
    ),
    email: EmailStr = Form(...),
    password: str = Form(
        ...,
        min_length=8,
    ),
    user_profile_image: UploadFile | None = File(
        default=None,
        alias="profileImage",
    ),
    db: Session = Depends(get_db),
):

    register_data = RegisterRequest(
        fullName=full_name,
        email=email,
        password=password,
    )

    return register_user(
        register_data=register_data,
        user_profile_image=user_profile_image,
        db=db,
    )