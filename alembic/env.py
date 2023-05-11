import logging
import os
from sqlalchemy import create_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from ..database.utils import build_database_url
from ..database.models import get_combined_metadata

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support


target_metadata = get_combined_metadata()


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url() -> str:
    env_data = {}
    if os.environ.get("DB_HOST") is None:
        if os.path.exists(".env"):
            logging.info("Loading environment variables from .env file")
            for line in open(".env"):
                if line.startswith("#"):
                    continue
                var = line.strip().split("=")
                if len(var) == 2:
                    env_data[var[0]] = var[1]
                else:
                    logging.info("Invalid line in .env file: {}".format(line))
            if env_data.get("DB_HOST") is None:
                logging.info("DB_HOST environment variable not set")
                logging.info("Invalid .env file")
                raise Exception("Invalid .env file")
            # url = build_database_url(None, None, None, None)
            url = build_database_url(env_data.get('DB_USER'), env_data.get('DB_PASS'), env_data.get('DB_HOST'),
                                     env_data.get('DB_NAME'))
        else:
            logging.info("No .env file found")
            url = build_database_url(None, None, None, None)
    else:
        logging.info("Loading environment variables from environment")
        url = build_database_url(os.environ.get('DB_USER'), os.environ.get('DB_PASS'), os.environ.get('DB_HOST'),
                                 os.environ.get('DB_NAME'))
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        logging.info("Running migrations offline")
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(get_url())
    logging.info("FINAL URL: {}".format(get_url()))
    logging.info("Connecting to database")
    with connectable.connect() as connection:
        logging.info("Connections established")
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            logging.info("Running migrations online")
            context.run_migrations()


try:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
except Exception as e:
    logging.info("Error: {}".format(e))
