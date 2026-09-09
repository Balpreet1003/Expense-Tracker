from logging.config import fileConfig
import os

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from app.database.base import Base
from app.features.auth.models.user import User
from app.features.income.models.income import Income
from app.features.expense.models.expense import Expense


# Load environment variables from .env
load_dotenv()


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Get the database URL from Alembic configuration.
#
# Normal Alembic commands will not provide a URL, so we fall back
# to DB_URL from the environment.
#
# Pytest can explicitly provide DB_TEST_URL through the Alembic Config.
database_url = config.get_main_option("sqlalchemy.url")


if not database_url:
    database_url = os.getenv("DB_URL")


if not database_url:
    raise ValueError(
        "Database URL is not configured. "
        "Set DB_URL or provide sqlalchemy.url through Alembic configuration."
    )


# Ensure Alembic uses the resolved database URL.
config.set_main_option(
    "sqlalchemy.url",
    database_url,
)


# Expense is imported above so SQLAlchemy registers
# the model with Base.metadata.


# Tell Alembic about your SQLAlchemy models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()