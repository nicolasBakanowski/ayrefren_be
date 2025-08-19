from logging.config import fileConfig
import os
from urllib.parse import urlparse, urlunparse

from sqlalchemy import engine_from_config, pool
from alembic import context

# Importa tus modelos y Base
from app.models import *  # noqa: F401,F403
from app.core.database import Base  # tu declarative_base

config = context.config

# ─────────────────────────────────────────────────────────────
# 1) Obtener DATABASE_URL (async) y convertirla a sync
# ─────────────────────────────────────────────────────────────
def to_sync_url(async_url: str) -> str:
    """
    Convierte una URL async (postgresql+asyncpg://) a una sync para Alembic.
    Prioriza psycopg (psycopg3); si querés psycopg2, cambiá el return.
    """
    if not async_url:
        return async_url

    # Solo tocar si es asyncpg
    if async_url.startswith("postgresql+asyncpg://"):
        # Opción A (psycopg3 - recomendado en SQLAlchemy 2.x):
        return async_url.replace("postgresql+asyncpg", "postgresql+psycopg", 1)

        # Opción B (psycopg2 - clásico):
        # return async_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)

    # Si ya viene con otro dialecto sync, la dejo igual
    return async_url


def resolve_database_url() -> str:
    # 1) Del entorno
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return to_sync_url(env_url)

    # 2) Del alembic.ini (por si quedó definido ahí, aunque idealmente vacío)
    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        return ini_url

    # 3) Sin URL -> error explícito
    raise RuntimeError(
        "DATABASE_URL no está definida y sqlalchemy.url en alembic.ini está vacío. "
        "Definí la variable de entorno DATABASE_URL (async) antes de correr Alembic."
    )


sync_db_url = resolve_database_url()
config.set_main_option("sqlalchemy.url", sync_db_url)

# ─────────────────────────────────────────────────────────────
# 2) Logging de Alembic
# ─────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ─────────────────────────────────────────────────────────────
# 3) Metadata
# ─────────────────────────────────────────────────────────────
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # útil para detectar cambios de tipo
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # útil para detectar cambios de tipo
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
