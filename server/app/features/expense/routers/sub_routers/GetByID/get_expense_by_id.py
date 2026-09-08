from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.Response.response import ExpenseResponse
from app.features.expense.services.GetByID.get_expense_by_id_service import get_expense_by_id as get_expense_by_id_service
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

router = APIRouter()

@router.get(
    "/expense/{expense_id}", 
    response_model=ExpenseResponse
)
def get_expense_by_id(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_expense_by_id_service(
        expense_id,
        db,
        current_user
    )