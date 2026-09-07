from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.schemas import CreateExpenseRequest, ExpenseResponse
from app.features.expense.services.expense_service import add_expense as add_expense_service
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

router = APIRouter()

@router.post(
    "/expense", 
    response_model = ExpenseResponse,
    status_code = status.HTTP_201_CREATED
)
def add_expense(
    expense_data: CreateExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_expense_service(
        expense_data,
        db,
        current_user
    )