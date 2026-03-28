from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

from alembic import context

alembic_path = Path(__file__).parent.absolute()
if str(alembic_path) not in sys.path:
    sys.path.insert(0, str(alembic_path))

# Ensure Alembic reads backend/.env when run from CLI.
project_root = alembic_path.parent
load_dotenv(project_root / ".env", override=False)

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/ai_marketplace")

from models_standalone import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    return os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/ai_marketplace")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url().replace("+asyncpg", "+psycopg2")
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
