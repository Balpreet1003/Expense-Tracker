"""add cascade delete to expenses and incomes user foreign key

Revision ID: 4430f784e2c4
Revises: 8ad03bd39ec0
Create Date: 2026-09-10 02:20:50.677038

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.

revision: str = "4430f784e2c4"
down_revision: Union[str, Sequence[str], None] = "8ad03bd39ec0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Add ON DELETE CASCADE to user foreign keys."""

    op.drop_constraint(
        "expenses_user_id_fkey",
        "expenses",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "expenses_user_id_fkey",
        "expenses",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "incomes_user_id_fkey",
        "incomes",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "incomes_user_id_fkey",
        "incomes",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

def downgrade() -> None:
    """Remove ON DELETE CASCADE from user foreign keys."""

    op.drop_constraint(
        "incomes_user_id_fkey",
        "incomes",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "incomes_user_id_fkey",
        "incomes",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(
        "expenses_user_id_fkey",
        "expenses",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "expenses_user_id_fkey",
        "expenses",
        "users",
        ["user_id"],
        ["id"],
    )