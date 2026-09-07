from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.services.service import delete_expense as delete_expense_service


router = APIRouter()

@router.delete(
    "/expense/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    delete_expense_service(expense_id, db)