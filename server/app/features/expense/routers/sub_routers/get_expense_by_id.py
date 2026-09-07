from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.schemas import ExpenseResponse
from app.features.expense.services.service import get_expense_by_id as get_expense_by_id_service


router = APIRouter()

@router.get(
    "/expense/{expense_id}", 
    response_model=ExpenseResponse
)
def get_expense_by_id(
    expense_id: int,
    db: Session = Depends(get_db)
):
    return get_expense_by_id_service(expense_id, db)