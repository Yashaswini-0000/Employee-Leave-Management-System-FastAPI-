from logging.config import fileConfig

from alembic import context

from app.config import settings

from app.database import Base

from app.models import models

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.mysql_database_url.replace("%", "%%")
)

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():

    context.configure(
        url=settings.mysql_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    from sqlalchemy import create_engine

    connectable = create_engine(settings.mysql_database_url)

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
