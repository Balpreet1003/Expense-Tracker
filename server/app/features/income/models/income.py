from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Column, Date, DateTime, Numeric, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.database.base import Base


if TYPE_CHECKING:
    from app.features.auth.models.user import User


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
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
        nullable=False,
    )

    date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="incomes",
    )