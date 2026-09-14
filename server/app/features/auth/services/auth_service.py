from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.auth.schemas.schemas import (
    AuthResponse,
    RegisterRequest,
    UserResponse,
    LoginRequest,
    UpdateUserRequest
)
from app.features.auth.utils.jwt import create_access_token
from app.features.auth.utils.image_upload import upload_profile_image
from app.features.auth.utils.password import (
    verify_password,
    hash_password
)


def register_user(
    register_data: RegisterRequest,
    user_profile_image: UploadFile | None,
    db: Session,
) -> AuthResponse:

    existing_user = (
        db.query(User)
        .filter(User.email == register_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    profile_image_url = ""

    if user_profile_image:
        profile_image_url = upload_profile_image(
            user_profile_image
        )

    hashed_password = hash_password(
        register_data.password
    )

    user = User(
        full_name=register_data.full_name,
        email=register_data.email,
        password=hashed_password,
        profile_image_url=profile_image_url,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    token = create_access_token(
        user_id=user.id
    )

    user_response = UserResponse.model_validate(user)

    return AuthResponse(
        user=user_response,
        token=token,
    )

def login_user(
    login_data: LoginRequest,
    db: Session,
) -> AuthResponse:

    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    is_password_valid = verify_password(
        login_data.password,
        user.password,
    )

    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        user_id=user.id,
    )

    user_response = UserResponse.model_validate(user)

    return AuthResponse(
        user=user_response,
        token=token,
    )


def update_user_profile(
    update_data: UpdateUserRequest,
    user_profile_image: UploadFile | None,
    current_user: User,
    db: Session,
) -> UserResponse:

    has_changes = False

    # Update full name
    if update_data.full_name is not None:

        if current_user.full_name != update_data.full_name:
            current_user.full_name = update_data.full_name
            has_changes = True

    # Update password
    if update_data.password is not None:

        hashed_password = hash_password(
            update_data.password
        )

        current_user.password = hashed_password
        has_changes = True

    # Update profile image
    if user_profile_image is not None:

        profile_image_url = upload_profile_image(
            user_profile_image
        )

        current_user.profile_image_url = (
            profile_image_url
        )

        has_changes = True

    # No update fields provided
    if not has_changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to update the profile",
        )

    try:
        db.commit()
        db.refresh(current_user)

    except Exception:
        db.rollback()
        raise

    return UserResponse.model_validate(
        current_user
    )