from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import app.db.models
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = app.db.models.Base.metadata

ignore_tables = ["langchain_pg_embedding", "langchain_pg_collection", "celery_tasksetmeta", "celery_taskmeta"]


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_objects(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ignore_tables:
        return False
    return True


def get_database_uri():
    # return "postgresql+psycopg://beehyv:beehyv123@localhost:5432/sahayak"
    return str(settings.SQLALCHEMY_DATABASE_URI_SYNC)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_uri()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"}, compare_type=True, include_object=include_objects)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config_mapping = config.get_section(config.config_ini_section, {})
    config_mapping.update({"sqlalchemy.url": get_database_uri()})
    connectable = engine_from_config(config_mapping, prefix="sqlalchemy.", poolclass=pool.NullPool, )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_object=include_objects)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
