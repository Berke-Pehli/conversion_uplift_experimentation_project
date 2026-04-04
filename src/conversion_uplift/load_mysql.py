"""
Load processed Hillstrom data into the normalized MySQL schema.

This module reads the processed dataset and inserts data into:
- dim_customers
- fact_campaign_assignment
- fact_campaign_outcomes

It assumes that lookup tables have already been populated:
- dim_zip_code
- dim_channel
- dim_campaign
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conversion_uplift.database import get_engine, read_table


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "hillstrom_processed.csv"


def load_processed_data() -> pd.DataFrame:
    """
    Load the processed Hillstrom dataset from disk.

    Returns:
        pd.DataFrame: Processed dataset ready for database loading.

    Raises:
        FileNotFoundError: If the processed CSV does not exist.
    """
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {PROCESSED_DATA_FILE}"
        )

    return pd.read_csv(PROCESSED_DATA_FILE)


def build_dim_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the dim_customers table dataset by mapping lookup IDs.

    Args:
        df: Processed Hillstrom dataset.

    Returns:
        pd.DataFrame: Customer dimension rows ready for SQL insertion.
    """
    zip_lookup = read_table("dim_zip_code")
    channel_lookup = read_table("dim_channel")

    zip_map = dict(zip(zip_lookup["zip_code_name"], zip_lookup["zip_code_id"]))
    channel_map = dict(zip(channel_lookup["channel_name"], channel_lookup["channel_id"]))

    dim_customers = df[
        [
            "customer_id",
            "recency",
            "history_segment",
            "history",
            "mens",
            "womens",
            "newbie",
            "zip_code",
            "channel",
        ]
    ].copy()

    dim_customers["zip_code_id"] = dim_customers["zip_code"].map(zip_map)
    dim_customers["channel_id"] = dim_customers["channel"].map(channel_map)

    dim_customers = dim_customers.drop(columns=["zip_code", "channel"])

    return dim_customers


def build_fact_campaign_assignment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the fact_campaign_assignment dataset by mapping campaign IDs.

    Args:
        df: Processed Hillstrom dataset.

    Returns:
        pd.DataFrame: Campaign assignment fact rows ready for SQL insertion.
    """
    campaign_lookup = read_table("dim_campaign")
    campaign_map = dict(zip(campaign_lookup["segment"], campaign_lookup["campaign_id"]))

    fact_assignment = df[["customer_id", "segment"]].copy()
    fact_assignment["campaign_id"] = fact_assignment["segment"].map(campaign_map)
    fact_assignment = fact_assignment.drop(columns=["segment"])

    return fact_assignment


def build_fact_campaign_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the fact_campaign_outcomes dataset.

    Args:
        df: Processed Hillstrom dataset.

    Returns:
        pd.DataFrame: Outcomes fact rows ready for SQL insertion.
    """
    return df[["customer_id", "visit", "conversion", "spend"]].copy()


def validate_no_missing_foreign_keys(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Ensure that mapped foreign key columns do not contain missing values.

    Args:
        df: DataFrame to validate.
        columns: List of foreign key columns to check.

    Raises:
        ValueError: If any foreign key column contains missing values.
    """
    for column in columns:
        if df[column].isna().any():
            raise ValueError(f"Missing values found in mapped foreign key column: {column}")


def load_tables_to_mysql() -> None:
    """
    Load processed data into the normalized MySQL tables.

    Loading order:
    1. dim_customers
    2. fact_campaign_assignment
    3. fact_campaign_outcomes
    """
    df = load_processed_data()

    dim_customers = build_dim_customers(df)
    fact_assignment = build_fact_campaign_assignment(df)
    fact_outcomes = build_fact_campaign_outcomes(df)

    validate_no_missing_foreign_keys(dim_customers, ["zip_code_id", "channel_id"])
    validate_no_missing_foreign_keys(fact_assignment, ["campaign_id"])

    engine = get_engine()

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

    print("MySQL load completed successfully.")
    print(f"dim_customers rows: {len(dim_customers)}")
    print(f"fact_campaign_assignment rows: {len(fact_assignment)}")
    print(f"fact_campaign_outcomes rows: {len(fact_outcomes)}")


def main() -> None:
    """
    Run the MySQL loading pipeline for the processed dataset.
    """
    load_tables_to_mysql()


if __name__ == "__main__":
    main()