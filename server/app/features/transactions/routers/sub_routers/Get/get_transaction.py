from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.models.user import User
from app.features.auth.dependencies.auth import get_current_user
from app.features.transactions.services.Get.get_transaction_service import get_transactions
from app.features.transactions.schemas.Response.response import TransactionResponse

router = APIRouter()

@router.get(
    "/transactions",
    status_code=status.HTTP_200_OK,
    response_model = list[TransactionResponse]
)
def get_transactions_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transactions(
        db=db,
        current_user=current_user
    )