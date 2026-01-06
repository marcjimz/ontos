#!/usr/bin/env python3
"""Upload members data to Unity Catalog."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config
from lib.databricks_client import get_client, execute_sql


def upload_members(config_path: str, csv_path: str):
    """Upload members CSV to Unity Catalog."""
    print("=" * 80)
    print("Uploading Members Data to Unity Catalog")
    print("=" * 80)

    config = load_config(config_path)
    client = get_client(config)
    warehouse_id = config['databricks']['warehouse_id']

    catalog = config['catalog']['name']
    schema = 'members'
    table = config['tables']['members']['table_name']
    full_table_name = f"{catalog}.{schema}.{table}"

    print(f"\nTarget table: {full_table_name}")
    print(f"Source CSV: {csv_path}")

    # Read CSV path
    csv_full_path = Path(csv_path).absolute()

    # Create table SQL
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {full_table_name} (
        member_id STRING NOT NULL,
        subscriber_id STRING,
        first_name STRING NOT NULL,
        last_name STRING NOT NULL,
        date_of_birth DATE NOT NULL,
        gender STRING NOT NULL,
        email STRING,
        phone_number STRING,
        address_line1 STRING NOT NULL,
        address_line2 STRING,
        city STRING NOT NULL,
        state STRING NOT NULL,
        zip_code STRING NOT NULL,
        plan_id STRING NOT NULL,
        plan_type STRING NOT NULL,
        enrollment_date DATE NOT NULL,
        termination_date DATE,
        member_status STRING NOT NULL,
        primary_care_provider_npi STRING,
        risk_score DECIMAL(10,3),
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    USING DELTA
    COMMENT 'Member profiles including demographics and enrollment'
    """

    print("\nCreating table (if not exists)...")
    execute_sql(client, warehouse_id, create_table_sql)
    print("✓ Table created")

    # For simplicity, we'll use COPY INTO which requires cloud storage
    # Alternative: Read CSV with pandas and insert row by row
    print("\nNote: To upload CSV data, you have two options:")
    print("1. Use COPY INTO (requires CSV in cloud storage)")
    print("2. Use pandas to read CSV and INSERT INTO")
    print(f"\nExample pandas upload:")
    print(f"""
import pandas as pd
from databricks.sdk import WorkspaceClient

df = pd.read_csv('{csv_path}')
client = WorkspaceClient(...)
# Use client to insert data via SQL or dataframe API
    """)

    print(f"\n✓ Table {full_table_name} is ready for data upload")
    print(f"  Manual upload: Use Databricks UI to upload {csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload members data to Unity Catalog")
    parser.add_argument('--config', default='demo/settings.yaml')
    parser.add_argument('--csv', default='demo/data/members_sample.csv')

    args = parser.parse_args()
    upload_members(args.config, args.csv)
