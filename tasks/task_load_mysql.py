"""
Pytask task for loading processed data into MySQL in the conversion uplift project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from conversion_uplift.database import get_engine
from conversion_uplift.load_mysql import (
    build_dim_customers,
    build_fact_campaign_assignment,
    build_fact_campaign_outcomes,
    load_processed_data,
    validate_no_missing_foreign_keys,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"
MYSQL_LOAD_SUMMARY_FILE = PROJECT_ROOT / "outputs" / "reports" / "mysql_load_summary.csv"


def task_load_mysql(
    depends_on: Path = PROCESSED_DATA_FILE,
    produces: Annotated[Path, Product] = MYSQL_LOAD_SUMMARY_FILE,
) -> None:
    """
    Load processed data into the normalized MySQL tables and save a small summary.
    """
    _ = depends_on

    df = load_processed_data()

    dim_customers = build_dim_customers(df)
    fact_assignment = build_fact_campaign_assignment(df)
    fact_outcomes = build_fact_campaign_outcomes(df)

    validate_no_missing_foreign_keys(dim_customers, ["zip_code_id", "channel_id"])
    validate_no_missing_foreign_keys(fact_assignment, ["campaign_id"])

    try:
        engine = get_engine()
    except Exception as exc:
        raise RuntimeError(
            "Failed to create the MySQL engine. Check your .env settings and "
            "make sure required MySQL auth dependencies are installed."
        ) from exc

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM fact_campaign_outcomes;")
            connection.exec_driver_sql("DELETE FROM fact_campaign_assignment;")
            connection.exec_driver_sql("DELETE FROM dim_customers;")

        dim_customers.to_sql(
            "dim_customers",
            engine,
            if_exists="append",
            index=False,
            chunksize=5000,
        )

        fact_assignment.to_sql(
            "fact_campaign_assignment",
            engine,
            if_exists="append",
            index=False,
            chunksize=5000,
        )

        fact_outcomes.to_sql(
            "fact_campaign_outcomes",
            engine,
            if_exists="append",
            index=False,
            chunksize=5000,
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed during MySQL load. Verify database access, authentication "
            "method, and table availability."
        ) from exc

    summary_df = pd.DataFrame(
        {
            "dim_customers_rows": [len(dim_customers)],
            "fact_campaign_assignment_rows": [len(fact_assignment)],
            "fact_campaign_outcomes_rows": [len(fact_outcomes)],
        }
    )

    produces.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(produces, index=False)