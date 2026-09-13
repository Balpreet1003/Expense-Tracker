from datetime import date as Date, timezone, datetime
from decimal import Decimal
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )

    icon: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
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

    created_at: Mapped[DateTime] = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[DateTime] = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship(
        "User",
        back_populates="expenses",
    )