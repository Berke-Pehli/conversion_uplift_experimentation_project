"""
Tests for database helpers in the conversion uplift project.
"""

from __future__ import annotations

import pandas as pd
import pytest

from conversion_uplift import database


class DummyConfig:
    """
    Dummy database config for testing engine creation.
    """

    sqlalchemy_url = "mysql+pymysql://user:password@localhost:3306/test_db"


class FakeResult:
    """
    Fake SQLAlchemy result object.
    """

    def fetchone(self):
        class Row:
            connection_test = 1

        return Row()


class FakeConnection:
    """
    Fake SQLAlchemy connection object.
    """

    def execute(self, _statement):
        return FakeResult()


class FakeConnectionContext:
    """
    Fake context manager returned by engine.connect().
    """

    def __enter__(self):
        return FakeConnection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class FakeEngine:
    """
    Fake SQLAlchemy engine object.
    """

    def connect(self):
        return FakeConnectionContext()


def test_get_engine_uses_config_and_expected_sqlalchemy_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    get_engine should call create_engine with the configured URL and options.
    """
    captured: dict[str, object] = {}

    def fake_create_engine(url: str, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return "fake_engine"

    monkeypatch.setattr(database, "get_database_config", lambda: DummyConfig())
    monkeypatch.setattr(database, "create_engine", fake_create_engine)

    engine = database.get_engine()

    assert engine == "fake_engine"
    assert captured["url"] == DummyConfig.sqlalchemy_url
    assert captured["kwargs"] == {"pool_pre_ping": True, "future": True}


def test_read_table_uses_expected_query(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    read_table should issue SELECT * FROM <table_name> through pandas.read_sql.
    """
    fake_df = pd.DataFrame({"a": [1, 2, 3]})
    captured: dict[str, object] = {}

    monkeypatch.setattr(database, "get_engine", lambda: "fake_engine")

    def fake_read_sql(query: str, engine):
        captured["query"] = query
        captured["engine"] = engine
        return fake_df

    monkeypatch.setattr(database.pd, "read_sql", fake_read_sql)

    result = database.read_table("dim_campaign")

    assert captured["query"] == "SELECT * FROM dim_campaign"
    assert captured["engine"] == "fake_engine"
    pd.testing.assert_frame_equal(result, fake_df)


def test_test_connection_prints_success_message(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    test_connection should print a success message when the query works.
    """
    monkeypatch.setattr(database, "get_engine", lambda: FakeEngine())

    database.test_connection()

    captured = capsys.readouterr()
    assert "Database connection successful." in captured.out
    assert "Test query result: 1" in captured.out