#!/usr/bin/env python3
"""
Generate static synthetic data files for demo.

This script generates CSV files with synthetic healthcare data including
intentional quality issues. Run this once to create the data files that
will be uploaded to Unity Catalog.

Usage:
    python scripts/generate_static_data.py --config demo/settings.yaml
"""

import sys
import os
import csv
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, get_data_volume, get_quality_issue_rate
from lib.synthetic_data import (
    generate_member_id, generate_claim_id, generate_npi,
    generate_email, generate_address, generate_date_in_range,
    get_random_icd10, get_random_cpt, get_random_specialty,
    get_random_plan_type, generate_raf_score, generate_claim_amount,
    COMMON_ICD10_CODES, COMMON_CPT_CODES, PLAN_TYPES, CLAIM_STATUSES, NETWORK_TYPES
)
from lib.data_quality import (
    inject_missing_value, inject_invalid_code, inject_orphaned_reference,
    inject_duplicate_id, inject_future_date, inject_negative_amount,
    inject_outlier_amount, get_invalid_diagnosis_code, get_invalid_procedure_code,
    get_invalid_state_code
)


def generate_members_data(config: dict, output_path: str):
    """Generate members data CSV."""
    print("Generating members data...")

    num_members = get_data_volume(config, 'members')
    start_date = config['data_generation']['date_ranges']['enrollment_start']
    end_date = config['data_generation']['date_ranges']['enrollment_end']

    # Quality issue rates
    missing_rate = get_quality_issue_rate(config, 'missing_values')
    invalid_state_rate = get_quality_issue_rate(config, 'invalid_codes')
    duplicate_rate = get_quality_issue_rate(config, 'duplicate_records')

    members = []
    member_ids = []

    for i in range(num_members):
        member_id = generate_member_id()

        # Inject duplicates
        if i > 0 and random.random() < duplicate_rate:
            member_id = random.choice(member_ids[-100:])  # Duplicate from recent

        member_ids.append(member_id)

        first_name = f"Patient{i:05d}"
        last_name = f"Test{i:05d}"

        # Generate demographics
        dob = generate_date_in_range("1930-01-01", "2020-12-31")
        gender = random.choice(['M', 'F', 'X'])

        # Address
        street, city, state, zip_code, _ = generate_address()

        # Inject invalid state codes
        if random.random() < invalid_state_rate:
            state = get_invalid_state_code()

        # Email and phone (some missing)
        email = inject_missing_value(generate_email(first_name, last_name), missing_rate)
        phone = inject_missing_value(f"+1{random.randint(2000000000, 9999999999)}", missing_rate)

        # Enrollment
        enrollment_date = generate_date_in_range(start_date, end_date)

        # 85% active, 15% terminated
        if random.random() < 0.85:
            status = 'active'
            termination_date = None
        else:
            status = 'terminated'
            term_days = random.randint(30, 365)
            termination_date = (enrollment_date + timedelta(days=term_days)).strftime('%Y-%m-%d')

        plan_type = get_random_plan_type()
        plan_id = f"PLAN-{random.randint(1000, 9999)}"

        # PCP assignment (optional)
        pcp_npi = inject_missing_value(generate_npi(), missing_rate * 2)

        # Risk score
        risk_score = generate_raf_score()

        members.append({
            'member_id': member_id,
            'subscriber_id': member_id if random.random() < 0.7 else generate_member_id(),
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob.strftime('%Y-%m-%d'),
            'gender': gender,
            'email': email,
            'phone_number': phone,
            'address_line1': street,
            'address_line2': inject_missing_value(f"Apt {random.randint(1, 500)}", 0.7),
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'plan_id': plan_id,
            'plan_type': plan_type,
            'enrollment_date': enrollment_date.strftime('%Y-%m-%d'),
            'termination_date': termination_date,
            'member_status': status,
            'primary_care_provider_npi': pcp_npi,
            'risk_score': risk_score,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })

        if (i + 1) % 10000 == 0:
            print(f"  Generated {i + 1:,} members...")

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=members[0].keys())
        writer.writeheader()
        writer.writerows(members)

    print(f"✓ Generated {len(members):,} members -> {output_path}")
    return member_ids


def generate_providers_data(config: dict, output_path: str):
    """Generate providers data CSV."""
    print("Generating providers data...")

    num_providers = get_data_volume(config, 'providers')

    # Quality issue rates
    missing_rate = get_quality_issue_rate(config, 'missing_values')
    duplicate_rate = get_quality_issue_rate(config, 'duplicate_records')

    providers = []
    npis = []

    for i in range(num_providers):
        npi = generate_npi()

        # Inject duplicates
        if i > 0 and random.random() < duplicate_rate:
            npi = random.choice(npis[-50:])

        npis.append(npi)

        # 70% individual, 30% organization
        if random.random() < 0.7:
            provider_type = 'individual'
            first_name = f"Dr{i:05d}"
            last_name = f"Provider{i:05d}"
            org_name = None
        else:
            provider_type = 'organization'
            first_name = None
            last_name = None
            org_name = f"Medical Center {i:05d}"

        specialty = get_random_specialty()

        # Network status: 90% in-network
        if random.random() < 0.9:
            network_status = 'in_network'
            contract_start = generate_date_in_range("2020-01-01", "2023-12-31")
            contract_end = inject_missing_value(
                (contract_start + timedelta(days=365*3)).strftime('%Y-%m-%d'),
                0.3
            )
        else:
            network_status = 'out_of_network'
            contract_start = None
            contract_end = None

        accepting = random.choice([True, False])

        # Address
        street, city, state, zip_code, _ = generate_address()
        phone = f"+1{random.randint(2000000000, 9999999999)}"

        # Credentialing
        if random.random() < 0.95:
            cred_status = 'credentialed'
            cred_date = generate_date_in_range("2020-01-01", "2024-12-31")
        else:
            cred_status = random.choice(['pending', 'expired'])
            cred_date = None

        providers.append({
            'provider_id': f"PROV-{i:06d}",
            'npi': npi,
            'provider_type': provider_type,
            'first_name': first_name,
            'last_name': last_name,
            'organization_name': org_name,
            'specialty_code': f"SPC{random.randint(100, 999)}",
            'specialty_description': specialty,
            'network_status': network_status,
            'contract_start_date': contract_start.strftime('%Y-%m-%d') if contract_start else None,
            'contract_end_date': contract_end,
            'accepting_new_patients': accepting,
            'address_line1': street,
            'address_line2': inject_missing_value(f"Suite {random.randint(100, 999)}", 0.6),
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'phone_number': phone,
            'credentialing_status': cred_status,
            'credentialing_date': cred_date.strftime('%Y-%m-%d') if cred_date else None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })

        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1:,} providers...")

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=providers[0].keys())
        writer.writeheader()
        writer.writerows(providers)

    print(f"✓ Generated {len(providers):,} providers -> {output_path}")
    return npis


def generate_claims_data(config: dict, member_ids: list, provider_npis: list, output_path: str):
    """Generate claims data CSV."""
    print("Generating claims data...")

    num_claims = get_data_volume(config, 'claims')
    start_date = config['data_generation']['date_ranges']['claims_start']
    end_date = config['data_generation']['date_ranges']['claims_end']

    # Quality issue rates
    orphaned_rate = get_quality_issue_rate(config, 'orphaned_references')
    future_date_rate = get_quality_issue_rate(config, 'future_dates')
    negative_amount_rate = get_quality_issue_rate(config, 'negative_amounts')
    outlier_rate = get_quality_issue_rate(config, 'outlier_amounts')
    invalid_code_rate = get_quality_issue_rate(config, 'invalid_codes')
    missing_rate = get_quality_issue_rate(config, 'missing_values')
    duplicate_rate = get_quality_issue_rate(config, 'duplicate_records')

    claims = []
    claim_ids_used = []

    for i in range(num_claims):
        claim_id = generate_claim_id()

        # Inject duplicates
        if i > 0 and random.random() < duplicate_rate:
            claim_id = random.choice(claim_ids_used[-100:])

        claim_ids_used.append(claim_id)

        # Member ID - inject orphaned references
        member_id = inject_orphaned_reference(member_ids, orphaned_rate)

        # Provider NPI - inject orphaned references
        provider_npi = inject_orphaned_reference(provider_npis, orphaned_rate)

        # Claim type
        claim_type = random.choice(['professional', 'institutional', 'dental', 'pharmacy'])

        # Service dates
        service_from = generate_date_in_range(start_date, end_date)
        service_from = inject_future_date(service_from, future_date_rate, max_days=180)

        service_days = random.randint(1, 7)
        service_to = service_from + timedelta(days=service_days)

        received_date = service_from + timedelta(days=random.randint(1, 14))

        # Status
        status = random.choices(
            CLAIM_STATUSES,
            weights=[0.05, 0.10, 0.70, 0.10, 0.05]
        )[0]

        if status in ['approved', 'denied', 'adjusted']:
            processed_date = received_date + timedelta(days=random.randint(1, 30))
        else:
            processed_date = None

        if status == 'approved':
            paid_date = processed_date + timedelta(days=random.randint(1, 14)) if processed_date else None
        else:
            paid_date = None

        # Diagnosis and procedure codes
        dx_code, dx_desc = get_random_icd10()
        proc_code, proc_desc = get_random_cpt()

        # Inject invalid codes
        if random.random() < invalid_code_rate:
            dx_code = get_invalid_diagnosis_code()
        if random.random() < invalid_code_rate:
            proc_code = get_invalid_procedure_code()

        diagnosis_codes = f"['{dx_code}']"
        procedure_codes = f"['{proc_code}']"

        # Amounts
        billed, allowed, paid = generate_claim_amount(claim_type)

        # Inject quality issues
        billed = inject_negative_amount(billed, negative_amount_rate)
        billed = inject_outlier_amount(billed, outlier_rate)

        if status != 'approved':
            paid = 0.0

        member_responsibility = allowed * random.uniform(0.1, 0.3)

        # Network
        network = random.choice(['in_network', 'out_of_network', 'preferred'])
        place_of_service = random.choice(['11', '21', '22', '23', '81'])

        denial_reason = None
        if status == 'denied':
            denial_reason = random.choice(['NOT_COVERED', 'NO_AUTH', 'OUT_OF_NETWORK', 'DUPLICATE'])

        claims.append({
            'claim_id': claim_id,
            'claim_number': f"CLM{i:010d}",
            'claim_type': claim_type,
            'member_id': member_id,
            'provider_npi': provider_npi,
            'service_date_from': service_from.strftime('%Y-%m-%d'),
            'service_date_to': service_to.strftime('%Y-%m-%d'),
            'received_date': received_date.strftime('%Y-%m-%d'),
            'processed_date': processed_date.strftime('%Y-%m-%d') if processed_date else None,
            'paid_date': paid_date.strftime('%Y-%m-%d') if paid_date else None,
            'claim_status': status,
            'diagnosis_codes': diagnosis_codes,
            'procedure_codes': procedure_codes,
            'billed_amount': round(billed, 2),
            'allowed_amount': round(allowed, 2),
            'paid_amount': round(paid, 2),
            'member_responsibility': round(member_responsibility, 2),
            'network_status': network,
            'place_of_service': place_of_service,
            'denial_reason_code': denial_reason,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })

        if (i + 1) % 10000 == 0:
            print(f"  Generated {i + 1:,} claims...")

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=claims[0].keys())
        writer.writeheader()
        writer.writerows(claims)

    print(f"✓ Generated {len(claims):,} claims -> {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate static synthetic data files")
    parser.add_argument('--config', default='demo/settings.yaml', help='Path to settings.yaml')
    parser.add_argument('--output-dir', default='demo/data', help='Output directory for CSV files')

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Set random seed for reproducibility
    random.seed(config['data_generation']['random_seed'])

    print("=" * 80)
    print("Generating Static Synthetic Data Files")
    print("=" * 80)
    print(f"Random seed: {config['data_generation']['random_seed']}")
    print(f"Output directory: {args.output_dir}\n")

    # Generate data files
    member_ids = generate_members_data(config, f"{args.output_dir}/members.csv")
    provider_npis = generate_providers_data(config, f"{args.output_dir}/providers.csv")
    generate_claims_data(config, member_ids, provider_npis, f"{args.output_dir}/claims.csv")

    print("\n" + "=" * 80)
    print("✓ All data files generated successfully!")
    print("=" * 80)
    print(f"\nFiles created in: {args.output_dir}/")
    print("  - members.csv")
    print("  - providers.csv")
    print("  - claims.csv")
    print("\nNext step: Run upload scripts to load data into Unity Catalog")


if __name__ == "__main__":
    main()
