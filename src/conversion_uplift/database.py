"""
Database connection helpers for the conversion uplift project.

This module centralizes SQLAlchemy engine creation so that the rest of the
project can reuse one consistent database connection pattern.

Main responsibilities:
- Build a SQLAlchemy engine
- Test database connectivity
- Read SQL tables into pandas DataFrames
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from conversion_uplift.config import get_database_config


def get_engine() -> Engine:
    """
    Create a SQLAlchemy engine using environment-based MySQL settings.

    Returns:
        Engine: SQLAlchemy engine connected to the target MySQL database.
    """
    db_config = get_database_config()

    engine = create_engine(
        db_config.sqlalchemy_url,
        pool_pre_ping=True,
        future=True,
    )
    return engine


def read_table(table_name: str) -> pd.DataFrame:
    """
    Read a full SQL table into a pandas DataFrame.

    Args:
        table_name: Name of the database table to read.

    Returns:
        pd.DataFrame: Table contents.
    """
    engine = get_engine()
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)


def test_connection() -> None:
    """
    Test whether the MySQL connection works.

    This function opens a connection, runs a simple query, and prints
    a success message if the connection is valid.

    Raises:
        Exception: Propagates any underlying database connection error.
    """
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 AS connection_test;"))
        row = result.fetchone()

    print("Database connection successful.")
    print(f"Test query result: {row.connection_test}")


if __name__ == "__main__":
    test_connection()