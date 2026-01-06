"""Synthetic data generation utilities for healthcare demo."""

from faker import Faker
import random
from typing import List, Tuple
from datetime import datetime, timedelta

fake = Faker()


def generate_npi() -> str:
    """Generate 10-digit National Provider Identifier."""
    return str(random.randint(1000000000, 9999999999))


def generate_member_id() -> str:
    """Generate member ID in format MBR-XXXXXX."""
    return f"MBR-{random.randint(100000, 999999)}"


def generate_claim_id() -> str:
    """Generate claim ID in format CLM-XXXXXXXXXX."""
    return f"CLM-{random.randint(1000000000, 9999999999)}"


def generate_phone() -> str:
    """Generate E.164 format phone number."""
    return fake.phone_number()


def generate_email(first_name: str, last_name: str) -> str:
    """Generate email address based on name."""
    return f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"


def generate_address() -> Tuple[str, str, str, str, str]:
    """
    Generate US address.

    Returns:
        Tuple of (street, city, state, zip, country)
    """
    return (
        fake.street_address(),
        fake.city(),
        fake.state_abbr(),
        fake.zipcode(),
        "USA"
    )


def generate_date_in_range(start_date: str, end_date: str) -> datetime:
    """
    Generate random date within range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Random datetime within range
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


# Common ICD-10 diagnosis codes for chronic conditions
COMMON_ICD10_CODES = {
    "E11.9": "Type 2 Diabetes Mellitus",
    "I10": "Essential Hypertension",
    "J44.9": "COPD",
    "I25.10": "Coronary Artery Disease",
    "E78.5": "Hyperlipidemia",
    "N18.3": "Chronic Kidney Disease, Stage 3",
    "F41.9": "Anxiety Disorder",
    "I50.9": "Heart Failure",
    "E66.9": "Obesity",
    "F33.1": "Major Depressive Disorder",
    "M79.3": "Chronic Pain",
    "G43.909": "Migraine",
    "K21.9": "GERD",
    "J45.909": "Asthma",
    "M17.9": "Osteoarthritis of Knee",
}

# Common CPT procedure codes
COMMON_CPT_CODES = {
    "99213": "Office Visit, Level 3",
    "99214": "Office Visit, Level 4",
    "99215": "Office Visit, Level 5",
    "99285": "Emergency Visit, High Severity",
    "80053": "Comprehensive Metabolic Panel",
    "85025": "Complete Blood Count",
    "93000": "Electrocardiogram",
    "71045": "Chest X-Ray",
    "45378": "Colonoscopy",
    "G0008": "Influenza Vaccine",
    "90837": "Psychotherapy, 60 minutes",
    "97110": "Physical Therapy",
    "36415": "Blood Draw",
    "87804": "Influenza Test",
}

# HCC (Hierarchical Condition Category) codes for risk adjustment
HCC_CODES = {
    "E11.9": "HCC 19",  # Diabetes
    "I10": "HCC 85",    # Hypertension
    "J44.9": "HCC 111", # COPD
    "I50.9": "HCC 85",  # Heart Failure
    "N18.3": "HCC 137", # CKD Stage 3
}

# Medical specialties
SPECIALTIES = [
    "Family Medicine",
    "Internal Medicine",
    "Cardiology",
    "Endocrinology",
    "Pulmonology",
    "Nephrology",
    "Orthopedic Surgery",
    "General Surgery",
    "Psychiatry",
    "Emergency Medicine",
    "Radiology",
    "Pathology",
    "Anesthesiology",
    "Obstetrics & Gynecology",
    "Pediatrics",
]

# Plan types
PLAN_TYPES = ["HMO", "PPO", "EPO", "POS", "HDHP"]

# Claim statuses
CLAIM_STATUSES = ["submitted", "pending", "approved", "denied", "adjusted"]

# Network types
NETWORK_TYPES = ["in_network", "out_of_network", "preferred"]


def get_random_icd10() -> Tuple[str, str]:
    """Get random ICD-10 code and description."""
    code = random.choice(list(COMMON_ICD10_CODES.keys()))
    return code, COMMON_ICD10_CODES[code]


def get_random_cpt() -> Tuple[str, str]:
    """Get random CPT code and description."""
    code = random.choice(list(COMMON_CPT_CODES.keys()))
    return code, COMMON_CPT_CODES[code]


def get_random_specialty() -> str:
    """Get random medical specialty."""
    return random.choice(SPECIALTIES)


def get_random_plan_type() -> str:
    """Get random insurance plan type."""
    return random.choice(PLAN_TYPES)


def generate_raf_score() -> float:
    """
    Generate Risk Adjustment Factor (RAF) score.
    Typical range: 0.5 to 3.0, mean ~1.0
    """
    return round(random.gauss(1.0, 0.5), 3)


def generate_claim_amount(service_type: str = "office_visit") -> Tuple[float, float, float]:
    """
    Generate realistic claim amounts.

    Args:
        service_type: Type of service (affects amount distribution)

    Returns:
        Tuple of (billed_amount, allowed_amount, paid_amount)
    """
    # Base amounts by service type
    if service_type == "emergency":
        billed = random.lognormvariate(7.0, 1.5)  # Mean ~$1100
    elif service_type == "surgery":
        billed = random.lognormvariate(8.5, 1.0)  # Mean ~$5000
    elif service_type == "lab":
        billed = random.lognormvariate(4.5, 1.0)  # Mean ~$90
    else:  # office_visit
        billed = random.lognormvariate(5.5, 1.0)  # Mean ~$245

    # Allowed is typically 40-80% of billed for in-network
    allowed = billed * random.uniform(0.4, 0.8)

    # Paid is allowed minus member responsibility (10-30%)
    member_responsibility_pct = random.uniform(0.1, 0.3)
    paid = allowed * (1 - member_responsibility_pct)

    return round(billed, 2), round(allowed, 2), round(paid, 2)
