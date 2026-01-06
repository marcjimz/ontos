"""Configuration management for demo setup scripts."""

import yaml
import os
from typing import Dict, Any


def load_config(path: str) -> Dict[str, Any]:
    """
    Load and expand environment variables in YAML config.

    Args:
        path: Path to YAML configuration file

    Returns:
        Dictionary containing parsed configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, 'r') as f:
        content = f.read()
        # Expand environment variables (e.g., ${DATABRICKS_HOST})
        content = os.path.expandvars(content)
        config = yaml.safe_load(content)

    # Validate required fields
    _validate_config(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate that required configuration fields are present."""
    required_fields = [
        ('databricks', 'host'),
        ('databricks', 'token'),
        ('databricks', 'warehouse_id'),
        ('catalog', 'name'),
    ]

    for *path, field in required_fields:
        obj = config
        for key in path:
            if key not in obj:
                raise ValueError(f"Missing required config: {'.'.join(path + [field])}")
            obj = obj[key]

        if field not in obj:
            raise ValueError(f"Missing required config: {'.'.join(path + [field])}")


def get_table_config(config: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """Get configuration for a specific table."""
    tables = config.get('tables', {})
    return tables.get(table_name, {})


def get_data_volume(config: Dict[str, Any], table_name: str) -> int:
    """Get the number of rows to generate for a table."""
    volumes = config.get('data_generation', {}).get('volumes', {})
    return volumes.get(table_name, 1000)


def get_quality_issue_rate(config: Dict[str, Any], issue_type: str) -> float:
    """Get the probability of injecting a specific quality issue."""
    quality_issues = config.get('data_generation', {}).get('quality_issues', {})
    if not quality_issues.get('enabled', False):
        return 0.0
    return quality_issues.get(issue_type, 0.0)
