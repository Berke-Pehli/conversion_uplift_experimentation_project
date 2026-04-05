"""
Tests for configuration utilities in the conversion uplift project.
"""

from __future__ import annotations

import pytest

from conversion_uplift.config import DatabaseConfig, get_database_config


def test_database_config_builds_expected_sqlalchemy_url() -> None:
    """
    DatabaseConfig should build the expected SQLAlchemy connection URL.
    """
    config = DatabaseConfig(
        user="test_user",
        password="test_password",
        host="localhost",
        port=3306,
        database="test_db",
    )

    assert (
        config.sqlalchemy_url
        == "mysql+pymysql://test_user:test_password@localhost:3306/test_db"
    )


def test_get_database_config_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    get_database_config should read and return validated environment variables.
    """
    monkeypatch.setenv("MYSQL_USER", "berke")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DATABASE", "conversion_uplift_db")

    config = get_database_config()

    assert config.user == "berke"
    assert config.password == "secret"
    assert config.host == "127.0.0.1"
    assert config.port == 3306
    assert config.database == "conversion_uplift_db"


def test_get_database_config_raises_for_missing_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    get_database_config should raise a clear error if a required env var is missing.
    """
    monkeypatch.delenv("MYSQL_USER", raising=False)
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DATABASE", "conversion_uplift_db")

    with pytest.raises(ValueError, match="Missing required environment variable"):
        get_database_config()


def test_get_database_config_raises_for_invalid_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    get_database_config should raise a clear error if MYSQL_PORT is not an integer.
    """
    monkeypatch.setenv("MYSQL_USER", "berke")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "not_a_number")
    monkeypatch.setenv("MYSQL_DATABASE", "conversion_uplift_db")

    with pytest.raises(ValueError, match="MYSQL_PORT must be a valid integer"):
        get_database_config()