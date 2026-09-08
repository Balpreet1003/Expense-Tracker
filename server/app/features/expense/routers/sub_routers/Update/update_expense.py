from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.UpdateRequest.update_request import UpdateExpenseRequest
from app.features.expense.schemas.Response.response import ExpenseResponse
from app.features.expense.services.Update.update_expense_service import update_expense as update_expense_service
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

router = APIRouter()


@router.patch(
    "/expense/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense(
    expense_id: int,
    expense_data: UpdateExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_expense_service(
        expense_id,
        expense_data,
        db,
        current_user
    )