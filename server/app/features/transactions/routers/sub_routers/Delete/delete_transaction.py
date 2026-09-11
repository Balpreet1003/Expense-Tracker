from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import Literal

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.transactions.services.Delete.delete_transaction_service import delete_transaction as delete_transaction_service

router = APIRouter()

@router.delete(
    "/transaction/{transaction_type}/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_type: Literal["income", "expense"] = Path(...),
    transaction_id: int = Path(..., gt=0, le=2147483647),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_transaction_service(
        transaction_type,
        transaction_id,
        db,
        current_user
    )