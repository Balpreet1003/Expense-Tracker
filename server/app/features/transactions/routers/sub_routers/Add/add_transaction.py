from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.transactions.schemas.CreateRequest.create_request import CreateTransactionRequest
from app.features.transactions.schemas.Response.response import TransactionResponse
from app.features.transactions.services.Add.add_transaction_service import add_transaction as add_transaction_service

router = APIRouter()

@router.post(
    "/transaction",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def add_transaction(
    transaction_data: CreateTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_transaction_service(
        transaction_data,
        db,
        current_user
    )