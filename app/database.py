from contextlib import contextmanager

import psycopg2 as pg

@contextmanager
def connect(conn=None, config=None):
    if config is None:
        from app import app
        config = app.config

    config = config.get('DATABASE', None)
    if config is None:
        raise ValueError("No database configuration available.")

    if conn is None:
        conn = pg.connect(
                database=config.get("NAME"),
                user=config.get("USER"),
                password=config.get("PASSWORD", ""),
                host=config.get("HOST", "localhost"),
                port=config.get("PORT", 5432),
        )

    yield conn
