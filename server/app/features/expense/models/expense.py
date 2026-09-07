from datetime import date as Date

from sqlalchemy import Column, Date, Float, Integer, String, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )

    amount: Mapped[float] = mapped_column(
        Float, 
        nullable=False
    )

    date: Mapped[Date] = mapped_column(
        Date, 
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        default=""
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_expenses"),
    )