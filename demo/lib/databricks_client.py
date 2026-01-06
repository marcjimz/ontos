"""Databricks SDK client wrapper for demo setup."""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from databricks.sdk.service.catalog import TableInfo, SchemaInfo, CatalogInfo
from typing import Dict, Any, Optional, List
import time


def get_client(config: Dict[str, Any]) -> WorkspaceClient:
    """
    Initialize Databricks SDK client.

    Args:
        config: Configuration dictionary with databricks.host and databricks.token

    Returns:
        Initialized WorkspaceClient
    """
    return WorkspaceClient(
        host=config['databricks']['host'],
        token=config['databricks']['token']
    )


def execute_sql(
    client: WorkspaceClient,
    warehouse_id: str,
    sql: str,
    timeout: str = "30m"
) -> Any:
    """
    Execute SQL via SQL Warehouse.

    Args:
        client: Databricks WorkspaceClient
        warehouse_id: SQL Warehouse ID
        sql: SQL statement to execute
        timeout: Timeout duration (e.g., "30m", "1h")

    Returns:
        Query result object

    Raises:
        RuntimeError: If SQL execution fails
    """
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=sql,
        wait_timeout=timeout
    )

    if response.status.state == StatementState.SUCCEEDED:
        return response.result
    else:
        error_msg = response.status.error.message if response.status.error else "Unknown error"
        raise RuntimeError(f"SQL failed: {error_msg}\nSQL: {sql}")


def table_exists(client: WorkspaceClient, catalog: str, schema: str, table: str) -> bool:
    """Check if a table exists in Unity Catalog."""
    try:
        full_name = f"{catalog}.{schema}.{table}"
        client.tables.get(full_name)
        return True
    except Exception:
        return False


def create_catalog(client: WorkspaceClient, name: str, comment: Optional[str] = None) -> CatalogInfo:
    """
    Create Unity Catalog (idempotent).

    Args:
        client: Databricks WorkspaceClient
        name: Catalog name
        comment: Optional catalog description

    Returns:
        CatalogInfo object
    """
    try:
        catalog = client.catalogs.get(name)
        print(f"✓ Catalog '{name}' already exists")
        return catalog
    except Exception:
        catalog = client.catalogs.create(name=name, comment=comment)
        print(f"✓ Created catalog: {name}")
        return catalog


def create_schema(
    client: WorkspaceClient,
    catalog: str,
    name: str,
    comment: Optional[str] = None
) -> SchemaInfo:
    """
    Create schema in Unity Catalog (idempotent).

    Args:
        client: Databricks WorkspaceClient
        catalog: Catalog name
        name: Schema name
        comment: Optional schema description

    Returns:
        SchemaInfo object
    """
    try:
        full_name = f"{catalog}.{name}"
        schema = client.schemas.get(full_name)
        print(f"✓ Schema '{full_name}' already exists")
        return schema
    except Exception:
        schema = client.schemas.create(
            catalog_name=catalog,
            name=name,
            comment=comment
        )
        print(f"✓ Created schema: {catalog}.{name}")
        return schema


def drop_table(client: WorkspaceClient, catalog: str, schema: str, table: str) -> None:
    """Drop a table if it exists."""
    warehouse_id = None  # Will be set by caller
    sql = f"DROP TABLE IF EXISTS {catalog}.{schema}.{table}"
    try:
        # For drop, we can use SQL via warehouse
        print(f"  Dropping table {catalog}.{schema}.{table}...")
    except Exception as e:
        print(f"  Warning: Could not drop table: {e}")


def get_table_count(
    client: WorkspaceClient,
    warehouse_id: str,
    catalog: str,
    schema: str,
    table: str
) -> int:
    """Get row count for a table."""
    sql = f"SELECT COUNT(*) as count FROM {catalog}.{schema}.{table}"
    result = execute_sql(client, warehouse_id, sql)

    if result and result.data_array:
        return int(result.data_array[0][0])
    return 0


def wait_for_warehouse(client: WorkspaceClient, warehouse_id: str, timeout: int = 300) -> None:
    """
    Wait for SQL Warehouse to be in RUNNING state.

    Args:
        client: Databricks WorkspaceClient
        warehouse_id: SQL Warehouse ID
        timeout: Maximum wait time in seconds
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        warehouse = client.warehouses.get(warehouse_id)
        state = warehouse.state

        if state.value == "RUNNING":
            print(f"✓ Warehouse {warehouse_id} is running")
            return
        elif state.value in ["STARTING", "STOPPED"]:
            print(f"  Waiting for warehouse to start (current state: {state.value})...")
            time.sleep(5)
        else:
            raise RuntimeError(f"Warehouse in unexpected state: {state.value}")

    raise TimeoutError(f"Warehouse did not start within {timeout} seconds")
