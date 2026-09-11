from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import Literal

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.transactions.schemas.UpdateRequest.update_request import UpdateTransactionRequest
from app.features.transactions.schemas.Response.response import TransactionResponse
from app.features.transactions.services.Update.update_transaction_service import update_transaction as update_transaction_service

router = APIRouter()

@router.patch(
    "/transaction/{transaction_type}/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=TransactionResponse
)
def update_transaction(
    transaction_data: UpdateTransactionRequest,
    transaction_type: Literal["income", "expense"] = Path(...),
    transaction_id: int = Path(..., gt=0, le=2147483647),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_transaction_service(
        transaction_type,
        transaction_id,
        transaction_data,
        db,
        current_user
    )