"""
Configuration utilities for the conversion uplift project.

This module is responsible for:
- loading environment variables from the local `.env` file
- validating required MySQL settings
- building a SQLAlchemy database URL
- exposing reusable project path constants, including build paths
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FINAL_DATA_DIR = DATA_DIR / "final"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
REPORTS_DIR = OUTPUTS_DIR / "reports"

DOCS_DIR = PROJECT_ROOT / "docs"
SQL_DIR = PROJECT_ROOT / "sql"
POWERBI_DIR = PROJECT_ROOT / "powerbi"
TASKS_DIR = PROJECT_ROOT / "tasks"
TESTS_DIR = PROJECT_ROOT / "tests"

# ---------------------------------------------------------------------
# Reproducible build paths (ignored by Git)
# ---------------------------------------------------------------------

BLD_DIR = PROJECT_ROOT / "bld"
BLD_DATA_DIR = BLD_DIR / "data"
BLD_DATA_PROCESSED_DIR = BLD_DATA_DIR / "processed"
BLD_DATA_FINAL_DIR = BLD_DATA_DIR / "final"
BLD_CHARTS_DIR = BLD_DIR / "charts"
BLD_REPORTS_DIR = BLD_DIR / "reports"


def create_build_directories() -> None:
    """
    Create the reproducible build folder structure if it does not exist.
    """
    BLD_DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    BLD_DATA_FINAL_DIR.mkdir(parents=True, exist_ok=True)
    BLD_CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    BLD_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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