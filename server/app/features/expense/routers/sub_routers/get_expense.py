from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.schemas import ExpenseResponse
from app.features.expense.services.expense_service import get_expenses as get_expenses_service
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

router = APIRouter()

@router.get(
        "/expense",
        response_model=list[ExpenseResponse]
    )
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_expenses_service(db,
        current_user
    )