"""
Configuration utilities for the conversion uplift project.

This module is responsible for loading environment variables from the local
`.env` file and exposing them in a clean, reusable structure for the rest
of the project.

Main responsibilities:
- Load environment variables
- Validate required MySQL settings
- Build a SQLAlchemy database URL
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """
    Store MySQL database configuration values.

    Attributes:
        user: MySQL username.
        password: MySQL password.
        host: MySQL host address.
        port: MySQL port number.
        database: Target MySQL database name.
    """

    user: str
    password: str
    host: str
    port: int
    database: str

    @property
    def sqlalchemy_url(self) -> str:
        """
        Build a SQLAlchemy connection URL for MySQL.

        Returns:
            str: SQLAlchemy-compatible MySQL connection string.
        """
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


def _get_required_env_var(name: str) -> str:
    """
    Read a required environment variable.

    Args:
        name: Name of the environment variable.

    Returns:
        str: The environment variable value.

    Raises:
        ValueError: If the variable is missing or empty.
    """
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise ValueError(
            f"Missing required environment variable: {name}. "
            "Please check your .env file."
        )

    return value


def get_database_config() -> DatabaseConfig:
    """
    Load and validate MySQL configuration from environment variables.

    Expected variables:
    - MYSQL_USER
    - MYSQL_PASSWORD
    - MYSQL_HOST
    - MYSQL_PORT
    - MYSQL_DATABASE

    Returns:
        DatabaseConfig: Validated database configuration object.

    Raises:
        ValueError: If one or more variables are missing or invalid.
    """
    user = _get_required_env_var("MYSQL_USER")
    password = _get_required_env_var("MYSQL_PASSWORD")
    host = _get_required_env_var("MYSQL_HOST")
    database = _get_required_env_var("MYSQL_DATABASE")

    port_str = _get_required_env_var("MYSQL_PORT")

    try:
        port = int(port_str)
    except ValueError as exc:
        raise ValueError("MYSQL_PORT must be a valid integer.") from exc

    return DatabaseConfig(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )