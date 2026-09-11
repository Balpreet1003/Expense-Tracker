from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import Literal

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.transactions.schemas.Response.response import TransactionResponse
from app.features.transactions.services.GetByID.get_transaction_by_id_service import get_transaction_by_id as get_transaction_by_id_service

router = APIRouter()

@router.get(
    "/transaction/{transaction_type}/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=TransactionResponse
)
def get_transaction_by_id(
    transaction_type: Literal["income", "expense"] = Path(...),
    transaction_id: int = Path(..., gt=0, le=2147483647),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_transaction_by_id_service(
        transaction_type,
        transaction_id,
        db,
        current_user
    )