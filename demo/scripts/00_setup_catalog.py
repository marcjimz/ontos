"""Create Unity Catalog structure for Healthcare Payor Demo."""

import sys
import os
from pathlib import Path

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config
from lib.databricks_client import get_client, create_catalog, create_schema


def setup_catalog(config_path: str, dry_run: bool = False) -> None:
    """
    Create Unity Catalog and schemas for the demo.

    Args:
        config_path: Path to settings.yaml
        dry_run: If True, only print what would be done
    """
    print("=" * 80)
    print("STEP 0: Setting up Unity Catalog Structure")
    print("=" * 80)

    # Load configuration
    config = load_config(config_path)
    catalog_name = config['catalog']['name']
    schemas = config['catalog']['schemas']

    print(f"\nCatalog: {catalog_name}")
    print(f"Schemas to create: {len(schemas)}")

    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]")
        print(f"\nWould create catalog: {catalog_name}")
        for schema_config in schemas:
            print(f"  - {catalog_name}.{schema_config['name']}: {schema_config['comment']}")
        return

    # Initialize Databricks client
    print("\nConnecting to Databricks...")
    client = get_client(config)

    # Create catalog
    print(f"\nCreating catalog: {catalog_name}")
    create_catalog(
        client,
        name=catalog_name,
        comment=config['catalog'].get('comment', 'Healthcare Payor Demo')
    )

    # Create schemas
    print(f"\nCreating schemas:")
    for schema_config in schemas:
        schema_name = schema_config['name']
        schema_comment = schema_config.get('comment', '')

        create_schema(
            client,
            catalog=catalog_name,
            name=schema_name,
            comment=schema_comment
        )

    print("\n" + "=" * 80)
    print(f"✓ Catalog setup complete!")
    print("=" * 80)
    print(f"\nCreated:")
    print(f"  - Catalog: {catalog_name}")
    print(f"  - Schemas: {', '.join([s['name'] for s in schemas])}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup Unity Catalog for Healthcare Payor Demo")
    parser.add_argument(
        "--config",
        default="demo/settings.yaml",
        help="Path to settings.yaml (default: demo/settings.yaml)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making changes"
    )

    args = parser.parse_args()

    try:
        setup_catalog(args.config, dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
