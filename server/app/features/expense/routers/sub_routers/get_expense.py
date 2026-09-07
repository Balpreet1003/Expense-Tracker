from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.expense.schemas.schemas import ExpenseResponse
from app.features.expense.services.service import get_expenses as get_expenses_service

router = APIRouter()

@router.get("/expense", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return get_expenses_service(db)