"""add created_at, updated_at and icon to income and expense

Revision ID: 8a3ed204b2c8
Revises: 4430f784e2c4
Create Date: 2026-09-12 21:18:53.327369
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8a3ed204b2c8"
down_revision: Union[str, Sequence[str], None] = "4430f784e2c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Expenses
    op.add_column(
        "expenses",
        sa.Column(
            "icon",
            sa.String(length=100),
            nullable=False,
            server_default=""
        )
    )

    op.add_column(
        "expenses",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    op.add_column(
        "expenses",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    op.alter_column(
        "expenses",
        "amount",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )

    # Incomes
    op.add_column(
        "incomes",
        sa.Column(
            "icon",
            sa.String(length=100),
            nullable=False,
            server_default=""
        )
    )

    op.add_column(
        "incomes",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    op.add_column(
        "incomes",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    op.alter_column(
        "incomes",
        "amount",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )


def downgrade() -> None:

    # Incomes
    op.alter_column(
        "incomes",
        "amount",
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )

    op.drop_column("incomes", "updated_at")
    op.drop_column("incomes", "created_at")
    op.drop_column("incomes", "icon")

    # Expenses
    op.alter_column(
        "expenses",
        "amount",
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )

    op.drop_column("expenses", "updated_at")
    op.drop_column("expenses", "created_at")
    op.drop_column("expenses", "icon")