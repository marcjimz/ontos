#!/usr/bin/env python3
"""
Healthcare Payor Demo - Workspace Setup Orchestrator

This script orchestrates the setup of demo data in a Databricks workspace
for the Ontos Healthcare Payor demo.

Usage:
    # Full setup (all tables)
    python demo/setup_workspace.py --config demo/settings.yaml --all

    # Setup specific tables
    python demo/setup_workspace.py --config demo/settings.yaml --tables claims,members

    # Dry run (validate without creating)
    python demo/setup_workspace.py --config demo/settings.yaml --dry-run

    # Skip catalog creation (already exists)
    python demo/setup_workspace.py --config demo/settings.yaml --skip-catalog

    # Clean up (drop all tables/schemas)
    python demo/setup_workspace.py --config demo/settings.yaml --clean
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_config
from lib.databricks_client import get_client


AVAILABLE_SCRIPTS = [
    "00_setup_catalog.py",
    "01_create_claims.py",
    "02_create_members.py",
    "03_create_providers.py",
    "04_create_clinical.py",
    "05_create_quality.py",
    "06_create_analytics.py",
]

TABLE_SCRIPT_MAP = {
    "claims": "01_create_claims.py",
    "members": "02_create_members.py",
    "providers": "03_create_providers.py",
    "clinical": "04_create_clinical.py",
    "clinical_events": "04_create_clinical.py",
    "quality": "05_create_quality.py",
    "quality_measures": "05_create_quality.py",
    "analytics": "06_create_analytics.py",
    "member_360": "06_create_analytics.py",
}


def print_banner(message: str) -> None:
    """Print a formatted banner message."""
    print("\n" + "=" * 80)
    print(message.center(80))
    print("=" * 80 + "\n")


def run_script(script_name: str, config_path: str, dry_run: bool = False) -> bool:
    """
    Run a setup script.

    Args:
        script_name: Name of the script file
        config_path: Path to settings.yaml
        dry_run: If True, run in dry-run mode

    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / "scripts" / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False

    print(f"Running: {script_name}")

    cmd = [sys.executable, str(script_path), "--config", config_path]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {script_name}")
        print(f"   Error: {e}")
        return False


def setup_all(config_path: str, skip_catalog: bool = False, dry_run: bool = False) -> None:
    """
    Run all setup scripts in sequence.

    Args:
        config_path: Path to settings.yaml
        skip_catalog: If True, skip catalog creation
        dry_run: If True, run in dry-run mode
    """
    print_banner("Healthcare Payor Demo - Full Setup")

    config = load_config(config_path)
    catalog_name = config['catalog']['name']

    print(f"Catalog: {catalog_name}")
    print(f"Dry Run: {dry_run}")
    print(f"Skip Catalog: {skip_catalog}\n")

    scripts_to_run = AVAILABLE_SCRIPTS.copy()
    if skip_catalog:
        scripts_to_run = [s for s in scripts_to_run if not s.startswith("00_")]

    success_count = 0
    for script in scripts_to_run:
        if run_script(script, config_path, dry_run):
            success_count += 1
        else:
            print(f"\n⚠️  Setup incomplete. {success_count}/{len(scripts_to_run)} scripts succeeded.")
            sys.exit(1)

    print_banner(f"✓ Setup Complete! ({success_count}/{len(scripts_to_run)} scripts succeeded)")


def setup_tables(config_path: str, tables: List[str], dry_run: bool = False) -> None:
    """
    Setup specific tables.

    Args:
        config_path: Path to settings.yaml
        tables: List of table names to create
        dry_run: If True, run in dry-run mode
    """
    print_banner(f"Healthcare Payor Demo - Setup Tables: {', '.join(tables)}")

    scripts_to_run = set()
    for table in tables:
        script = TABLE_SCRIPT_MAP.get(table)
        if script:
            scripts_to_run.add(script)
        else:
            print(f"⚠️  Unknown table: {table}")

    # Always run catalog setup first if not already done
    scripts_to_run.add("00_setup_catalog.py")

    # Sort scripts to run in order
    scripts_to_run = sorted(list(scripts_to_run))

    success_count = 0
    for script in scripts_to_run:
        if run_script(script, config_path, dry_run):
            success_count += 1
        else:
            print(f"\n⚠️  Setup incomplete. {success_count}/{len(scripts_to_run)} scripts succeeded.")
            sys.exit(1)

    print_banner(f"✓ Table Setup Complete! ({success_count}/{len(scripts_to_run)} scripts succeeded)")


def cleanup(config_path: str, confirm: bool = False) -> None:
    """
    Clean up demo data (drop catalog and all schemas).

    Args:
        config_path: Path to settings.yaml
        confirm: If True, skip confirmation prompt
    """
    print_banner("Healthcare Payor Demo - Cleanup")

    config = load_config(config_path)
    catalog_name = config['catalog']['name']

    print(f"⚠️  This will DROP the catalog: {catalog_name}")
    print("   All schemas and tables will be permanently deleted!\n")

    if not confirm:
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != "yes":
            print("Cleanup cancelled.")
            return

    print(f"\nDropping catalog: {catalog_name}...")

    try:
        client = get_client(config)
        warehouse_id = config['databricks']['warehouse_id']

        # Drop catalog (CASCADE will drop all schemas and tables)
        from lib.databricks_client import execute_sql
        execute_sql(client, warehouse_id, f"DROP CATALOG IF EXISTS {catalog_name} CASCADE")

        print(f"✓ Catalog dropped: {catalog_name}")
        print_banner("✓ Cleanup Complete!")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        sys.exit(1)


def verify_setup(config_path: str) -> None:
    """
    Verify the demo setup.

    Args:
        config_path: Path to settings.yaml
    """
    print_banner("Healthcare Payor Demo - Verification")

    # Run verification script
    if run_script("99_verify_setup.py", config_path, dry_run=False):
        print_banner("✓ Verification Complete!")
    else:
        print_banner("⚠️  Verification Failed!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Healthcare Payor Demo - Workspace Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--config",
        default="demo/settings.yaml",
        help="Path to settings.yaml (default: demo/settings.yaml)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all setup scripts"
    )

    parser.add_argument(
        "--tables",
        help="Comma-separated list of tables to create (e.g., claims,members)"
    )

    parser.add_argument(
        "--skip-catalog",
        action="store_true",
        help="Skip catalog creation (use if catalog already exists)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making changes"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up (drop catalog and all data)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify demo setup"
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    try:
        if args.clean:
            cleanup(args.config, confirm=args.yes)
        elif args.verify:
            verify_setup(args.config)
        elif args.all:
            setup_all(args.config, skip_catalog=args.skip_catalog, dry_run=args.dry_run)
        elif args.tables:
            tables = [t.strip() for t in args.tables.split(",")]
            setup_tables(args.config, tables, dry_run=args.dry_run)
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
