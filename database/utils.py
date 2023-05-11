import logging


# This must be in a separate file
def build_database_url(user, password, host, db):
    tmp_url = "sqlite:///./sql_app.db"
    if host is not None:
        tmp_url = f"mariadb+pymysql://{user}:{password}@{host}/{db}?charset=utf8mb4"
    else:
        logging.exception("No DB_HOST found in environment variables --> Using SQLite")
    return tmp_url


_RETURN_NONE = (lambda: None).__code__.co_code


def is_pass(f):
    return f.__code__.co_code == _RETURN_NONE
