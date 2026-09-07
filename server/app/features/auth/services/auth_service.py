from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.auth.models.user import User
from app.features.auth.schemas.schemas import (
    AuthResponse,
    RegisterRequest,
    UserResponse,
    LoginRequest
)
from app.features.auth.utils.jwt import create_access_token
from app.features.auth.utils.password import (
    verify_password,
    hash_password
)


def register_user(
    register_data: RegisterRequest,
    db: Session,
) -> AuthResponse:

    existing_user = (
        db.query(User)
        .filter(User.email == register_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    hashed_password = hash_password(
        register_data.password
    )

    user = User(
        full_name=register_data.full_name,
        email=register_data.email,
        password=hashed_password,
        profile_image_url=register_data.profile_image_url,
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
            status_code=401,
            detail="Invalid email or password",
        )

    is_password_valid = verify_password(
        login_data.password,
        user.password,
    )

    if not is_password_valid:
        raise HTTPException(
            status_code=401,
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