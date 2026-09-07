from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.expense.models.expense import Expense
from app.features.expense.schemas.schemas import CreateExpenseRequest, UpdateExpenseRequest


def add_expense(expense_data: CreateExpenseRequest, db: Session):
    try:
        expense = Expense(
            amount=expense_data.amount,
            date=expense_data.date,
            category=expense_data.category,
            description=expense_data.description
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise


def get_expenses(db: Session):
    statement = ( 
        select(Expense) 
        .order_by( 
            Expense.date.desc(), 
            Expense.id.desc() 
        )
    )

    result = db.execute(statement)

    expenses = result.scalars().all()

    return expenses

def get_expense_by_id(expense_id: int, db: Session):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail=f"Expense with ID {expense_id} not found"
        )

    return expense

def delete_expense(expense_id: int, db: Session):
    try:
        expense = db.get(Expense, expense_id)

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail=f"Expense with ID {expense_id} not found"
            )

        db.delete(expense)
        db.commit()

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

def update_expense(
    expense_id: int,
    updated_data: UpdateExpenseRequest,
    db: Session
):
    try:
        expense = db.get(Expense, expense_id)

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail=f"Expense with ID {expense_id} not found"
            )

        update_data = updated_data.model_dump(
            exclude_unset=True
            )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="At least one field is required to update the expense"
            )

        for key, value in update_data.items():
            setattr(expense, key, value)

        db.commit()
        db.refresh(expense)

        return expense

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise