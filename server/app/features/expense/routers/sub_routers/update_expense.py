from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.schemas import UpdateExpenseRequest, ExpenseResponse
from app.features.expense.services.service import update_expense as update_expense_service

router = APIRouter()


@router.patch(
    "/expense/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense(
    expense_id: int,
    expense_data: UpdateExpenseRequest,
    db: Session = Depends(get_db)
):
    return update_expense_service(
        expense_id,
        expense_data,
        db
    )