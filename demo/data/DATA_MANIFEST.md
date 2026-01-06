# Demo Data Manifest

This document describes the synthetic healthcare data files and the intentional quality issues injected for demonstration purposes.

## Data Files

### members_sample.csv
**Rows:** 15 members
**Schema:** 22 columns
**Description:** Member demographics, enrollment, and plan information

**Intentional Quality Issues:**
| Row | Issue Type | Field | Description |
|-----|------------|-------|-------------|
| 3 | Missing value | email | Email field is null |
| 5 | Missing value | primary_care_provider_npi | PCP not assigned |
| 7 | Missing value | email | Email field is null |
| 9 | Terminated member | member_status | Member status = 'terminated' |
| 12 | Missing values | phone_number, primary_care_provider_npi | Multiple missing fields |
| 13 | Invalid state code | state | State = 'XX' (invalid US state code) |

**Total Quality Issues:** 7 issues across 15 rows (~47% of rows have issues)

---

### providers_sample.csv
**Rows:** 10 providers
**Schema:** 21 columns
**Description:** Provider network directory with credentials and specialties

**Intentional Quality Issues:**
| Row | Issue Type | Field | Description |
|-----|------------|-------|-------------|
| 5 | Out-of-network | network_status | Provider not in network |

**Data Characteristics:**
- 70% individual providers, 30% organizations
- 90% in-network, 10% out-of-network
- Various specialties: Family Medicine, Cardiology, Orthopedics, Psychiatry, etc.

**Total Quality Issues:** 1 issue (intentional out-of-network for testing)

---

### claims_sample.csv
**Rows:** 15 claims
**Schema:** 21 columns
**Description:** Medical claims with diagnoses, procedures, and financial data

**Intentional Quality Issues:**
| Row | Issue Type | Field | Description |
|-----|------------|-------|-------------|
| 4 | Future date | service_date_from | Service date = 2026-06-30 (in the future) |
| 6 | Invalid code | diagnosis_codes | ICD-10 code 'Z99.999' (invalid code) |
| 6 | Denied claim | claim_status | Status = 'denied' with reason 'NOT_COVERED' |
| 7 | Orphaned reference | member_id | Member ID 'ORPHAN-999999' doesn't exist in members table |
| 10 | Negative amount | billed_amount | Billed amount = -95.00 (negative value) |
| 11 | Outlier amount | billed_amount | Billed amount = 125,000.00 (extreme outlier) |

**Claim Status Distribution:**
- approved: 10 (67%)
- denied: 1 (7%)
- submitted: 1 (7%)
- pending: 1 (7%)
- adjusted: 1 (7%)
- Status = terminated: 1 (7%)

**Network Distribution:**
- in_network: 14 (93%)
- out_of_network: 1 (7%)

**Total Quality Issues:** 6 issues across 15 rows (~40% of rows have issues)

---

## Quality Issue Summary

| Issue Category | Count | Percentage | ODCS Dimension |
|----------------|-------|------------|----------------|
| Missing values | 5 | 21% | Completeness |
| Invalid codes | 2 | 9% | Conformity |
| Orphaned references | 1 | 4% | Consistency |
| Future dates | 1 | 4% | Accuracy |
| Negative amounts | 1 | 4% | Accuracy |
| Outlier amounts | 1 | 4% | Accuracy |
| **Total** | **11** | **46%** | **Multiple** |

**Expected Quality Check Results:**
- **Members Table:**
  - Completeness: ~80% (5 missing values / 15 rows)
  - Conformity: ~93% (1 invalid state / 15 rows)
  - Overall: ~87%

- **Claims Table:**
  - Completeness: 100% (no missing required fields)
  - Accuracy: ~80% (3 accuracy issues / 15 rows)
  - Consistency: ~93% (1 orphaned reference / 15 rows)
  - Conformity: ~93% (1 invalid code / 15 rows)
  - Overall: ~92%

- **Providers Table:**
  - All checks pass: ~100%
  - (Out-of-network is valid, not a quality issue)

---

## Usage in Demo

### 1. Data Quality Checks Demonstration

These quality issues are designed to trigger specific quality checks defined in data contracts:

**Required Field Checks:**
- Will PASS (all required fields present)

**Unique Constraint Checks:**
- Will PASS (no duplicates in member_id, claim_id, npi)

**Referential Integrity Checks:**
- Will FAIL for claims row 7 (orphaned member_id)

**Date Range Checks:**
- Will FAIL for claims row 4 (future service date)

**Numeric Range Checks:**
- Will FAIL for claims row 10 (negative billed_amount)

**Statistical Outlier Checks:**
- Will FLAG claims row 11 (125K billed amount)

**Code Validation Checks:**
- Will FAIL for claims row 6 (invalid ICD-10 code)
- Will FAIL for members row 13 (invalid state code)

### 2. Compliance Monitoring

When data quality checks run:
- **Members contract quality score:** ~87%
- **Claims contract quality score:** ~92%
- **Overall compliance:** If threshold is 95%, both contracts will be NON-COMPLIANT

This triggers:
- Notifications to data stewards
- Alerts to data producers
- Compliance dashboard updates

### 3. Data Lineage

The data demonstrates relationships:
```
members (15) ──┬──> claims (14 valid + 1 orphaned)
               │
               └──> providers (10) ──> claims
```

---

## Generating Larger Datasets

To generate full-scale demo data (50K+ rows):

1. Edit `demo/settings.yaml`:
```yaml
data_generation:
  volumes:
    members: 50000
    claims: 100000
    providers: 5000
```

2. Run generation script:
```bash
python demo/scripts/generate_static_data.py --config demo/settings.yaml --output-dir demo/data
```

3. This will create:
   - `members.csv` (50,000 rows)
   - `claims.csv` (100,000 rows)
   - `providers.csv` (5,000 rows)

**Note:** Full generation takes ~5-10 minutes depending on hardware.

---

## Data Quality Issue Rates (Configurable)

Quality issues are injected at these rates (defined in `settings.yaml`):

```yaml
quality_issues:
  enabled: true
  missing_values: 0.02        # 2% of nullable fields
  invalid_codes: 0.01         # 1% of diagnosis/procedure codes
  orphaned_references: 0.005  # 0.5% of foreign key references
  duplicate_records: 0.01     # 1% of primary keys
  future_dates: 0.005         # 0.5% of date fields
  negative_amounts: 0.01      # 1% of financial amounts
  outlier_amounts: 0.03       # 3% of financial amounts (>$100K)
```

Set `enabled: false` to generate clean data without quality issues.

---

## File Format Specifications

### CSV Format
- **Encoding:** UTF-8
- **Delimiter:** Comma (,)
- **Quote Character:** Double quote (")
- **Header:** First row contains column names
- **Null Values:** Empty string or explicit null text

### Date Formats
- **DATE fields:** YYYY-MM-DD (e.g., 2024-03-15)
- **TIMESTAMP fields:** ISO 8601 (e.g., 2026-01-05T10:00:00)

### Array Fields
- **diagnosis_codes, procedure_codes:** String representation of array (e.g., "['E11.9', 'I10']")
- When loading to Delta, parse as ARRAY<STRING>

---

## License & Attribution

This synthetic data is generated for demonstration purposes only and does not represent real patients, providers, or claims. All names, identifiers, and values are fictitious.

**Data Generation Method:** Python with Faker library + custom healthcare-specific generators

**Standards Compliance:**
- ICD-10 diagnosis codes (example codes only)
- CPT procedure codes (example codes only)
- NPI format (10 digits)
- HIPAA PHI categories (for classification demonstration)

---

**Last Updated:** 2026-01-05
**Data Version:** 1.0.0
**Generator Script:** `demo/scripts/generate_static_data.py`
