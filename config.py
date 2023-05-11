import argparse
import importlib.machinery
import logging

from alembic.command import revision, upgrade
from alembic.config import Config
import os

from database.utils import is_pass

ignore_files = ["__pycache__"]


def run_sql_migrations() -> str:
    """Runs the SQL Migrations
    :return:
    """
    # retrieves the directory that *this* file is in
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    # this assumes the alembic.ini is also contained in this same directory
    config_file = os.path.join(migrations_dir, "alembic.ini")

    config = Config(file_=config_file)

    files = os.listdir("./alembic/versions")
    # files only contains 1 change. That's why we don't need to filter to __pycache__ directory

    # generate the newest SQL_Creation
    revision(config, autogenerate=True)
    version_tag = None
    for i in os.listdir("./alembic/versions"):
        if i not in files:
            version_tag = i.split(".")[0]

    return version_tag


def upgrade_head():
    """Upgrades the head of the database
    :return:
    """
    logging.info("Upgrading head")
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(migrations_dir, "alembic.ini")

    config = Config(file_=config_file)
    try:
        upgrade(config, "head")
    except Exception as e:
        logging.exception("Error while upgrading head")
        logging.exception(e)
        exit(1)
    logging.info("Finished upgrading head")


def check_migrations():
    """Checks if the migrations are valid
    Following steps are executed:
    1. upgrade head
    2. generate migration
    3. check if migration is empty (function signature must be equal to pass)
    4. delete migration of step 2
    """
    upgrade_head()
    version_tag = run_sql_migrations()
    try:
        modulename = importlib.machinery.SourceFileLoader('', f"./alembic/versions/{version_tag}.py") \
            .load_module()

        # checks if the generated migration file upgrade function has statements
        if is_pass(modulename.upgrade) and is_pass(modulename.downgrade):
            logging.info("Migrations are valid")
            exit(0)
        else:
            logging.info(f"Migration {version_tag} are not valid")
            with open(f"./alembic/versions/{version_tag}.py", "r") as file:
                logging.info(file.read())
            exit(1)
    finally:
        delete_migration(version_tag)


def delete_migration(version_tag):
    """Deletes the migration file

    Arguments:
        version_tag {str} -- The version tag of the migration
    """
    os.remove(f"./alembic/versions/{version_tag}.py")



if __name__ == "__main__":
    commands = {
        "create_migration": (run_sql_migrations, "Creates a new migration"),
        "upgrade_head": (upgrade_head, "Upgrades to the head of the migrations"),
        "check_migrations": (check_migrations, "Checks if the migrations are valid")
    }
    parser = argparse.ArgumentParser(description="Manage Alembic Config")
    parser.add_argument("command", help="Commands to run \n" + "\n".join([f"{i}: {commands[i][1]}" for i in commands]))
    os.environ['PREVENT_START'] = 'True'
    args = parser.parse_args()
    if args.coomand not in commands:
        exit(1)
    else:
        commands[args.command][0]()