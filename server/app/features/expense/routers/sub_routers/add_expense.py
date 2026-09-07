from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .....database.session import get_db
from ...schemas.schemas import CreateExpenseRequest, ExpenseResponse
from ...services.service import add_expense as add_expense_service


router = APIRouter()

@router.post(
    "/expense", 
    response_model = ExpenseResponse,
    status_code = status.HTTP_201_CREATED
)
def add_expense(expense_data: CreateExpenseRequest, db: Session = Depends(get_db)):
    return add_expense_service(expense_data, db)