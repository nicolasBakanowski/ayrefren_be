from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.models import *  # Importa todos los modelos para que Alembic pueda detectarlos

# === CONFIG ALEMBIC ===
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === IMPORTA LOS MODELOS Y METADATA ===
from app.core.database import Base

target_metadata = Base.metadata


# === MIGRACIONES OFFLINE ===
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# === MIGRACIONES ONLINE ===
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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


# === EJECUCIÓN ===
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
