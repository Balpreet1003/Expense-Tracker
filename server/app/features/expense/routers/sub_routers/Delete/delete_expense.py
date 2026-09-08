from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.services.Delete.delete_expense_service import delete_expense as delete_expense_service
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

router = APIRouter()

@router.delete(
    "/expense/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_expense_service(
        expense_id,
        db,
        current_user
    )