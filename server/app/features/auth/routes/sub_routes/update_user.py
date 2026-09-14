from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.features.auth.dependencies.auth import (
    get_current_user,
)

from app.features.auth.models.user import User

from app.features.auth.schemas.schemas import (
    UpdateUserRequest,
    UserResponse,
)

from app.features.auth.services.auth_service import (
    update_user_profile,
)


router = APIRouter()


@router.patch(
    "/profile",
    response_model=UserResponse,
)
def update_current_user_profile(
    full_name: str | None = Form(
        default=None,
        min_length=1,
        max_length=100,
        alias="fullName",
    ),

    password: str | None = Form(
        default=None,
        min_length=8,
    ),

    user_profile_image: UploadFile | None = File(
        default=None,
        alias="profileImage",
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    update_data = UpdateUserRequest(
        fullName=full_name,
        password=password,
    )

    return update_user_profile(
        update_data=update_data,
        user_profile_image=user_profile_image,
        current_user=current_user,
        db=db,
    )