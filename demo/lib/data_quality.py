"""Data quality issue injection utilities for demo data."""

import random
from typing import Any, Optional, List
from datetime import datetime, timedelta


def inject_missing_value(value: Any, probability: float) -> Optional[Any]:
    """
    Randomly return None based on probability.

    Args:
        value: Original value
        probability: Probability of returning None (0.0 to 1.0)

    Returns:
        None if random check passes, otherwise original value
    """
    return None if random.random() < probability else value


def inject_invalid_code(
    valid_codes: List[str],
    invalid_codes: List[str],
    probability: float
) -> str:
    """
    Inject invalid code based on probability.

    Args:
        valid_codes: List of valid codes to choose from
        invalid_codes: List of invalid codes for injection
        probability: Probability of returning invalid code

    Returns:
        Either a valid or invalid code
    """
    if random.random() < probability:
        return random.choice(invalid_codes)
    return random.choice(valid_codes)


def inject_future_date(
    date_obj: datetime,
    probability: float,
    max_days: int = 365
) -> datetime:
    """
    Inject future date based on probability.

    Args:
        date_obj: Original date
        probability: Probability of returning future date
        max_days: Maximum days in the future

    Returns:
        Either original date or future date
    """
    if random.random() < probability:
        return date_obj + timedelta(days=random.randint(1, max_days))
    return date_obj


def inject_negative_amount(
    amount: float,
    probability: float
) -> float:
    """
    Inject negative amount based on probability.

    Args:
        amount: Original amount
        probability: Probability of making amount negative

    Returns:
        Either original amount or negative amount
    """
    if random.random() < probability:
        return -abs(amount)
    return amount


def inject_outlier_amount(
    amount: float,
    probability: float,
    min_outlier: float = 100000,
    max_outlier: float = 500000
) -> float:
    """
    Inject extreme outlier amount based on probability.

    Args:
        amount: Original amount
        probability: Probability of returning outlier
        min_outlier: Minimum outlier value
        max_outlier: Maximum outlier value

    Returns:
        Either original amount or outlier amount
    """
    if random.random() < probability:
        return random.uniform(min_outlier, max_outlier)
    return amount


def inject_duplicate_id(
    current_id: str,
    existing_ids: List[str],
    probability: float
) -> str:
    """
    Inject duplicate ID based on probability.

    Args:
        current_id: Original ID
        existing_ids: List of existing IDs to duplicate from
        probability: Probability of returning duplicate

    Returns:
        Either original ID or duplicate ID
    """
    if random.random() < probability and existing_ids:
        return random.choice(existing_ids)
    return current_id


def inject_orphaned_reference(
    valid_references: List[str],
    probability: float,
    orphan_prefix: str = "ORPHAN"
) -> str:
    """
    Inject orphaned reference (non-existent foreign key).

    Args:
        valid_references: List of valid reference IDs
        probability: Probability of returning orphaned reference
        orphan_prefix: Prefix for generated orphan IDs

    Returns:
        Either valid reference or orphaned reference
    """
    if random.random() < probability:
        return f"{orphan_prefix}-{random.randint(100000, 999999)}"
    return random.choice(valid_references)


# Invalid codes for healthcare data quality testing
INVALID_ICD10_CODES = [
    "X99.999",  # Invalid code
    "Z99.999",  # Invalid code
    "INVALID",  # Not a code
    "ABC123",   # Wrong format
]

INVALID_CPT_CODES = [
    "00000",    # Invalid code
    "99999",    # Invalid code
    "XXXXX",    # Not a code
    "123",      # Wrong length
]

INVALID_STATE_CODES = [
    "XX",       # Invalid state
    "ZZ",       # Invalid state
    "AB",       # Not a US state
]


def get_invalid_diagnosis_code() -> str:
    """Get a random invalid ICD-10 diagnosis code."""
    return random.choice(INVALID_ICD10_CODES)


def get_invalid_procedure_code() -> str:
    """Get a random invalid CPT procedure code."""
    return random.choice(INVALID_CPT_CODES)


def get_invalid_state_code() -> str:
    """Get a random invalid state code."""
    return random.choice(INVALID_STATE_CODES)
