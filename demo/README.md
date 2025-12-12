# Healthcare Payor Demo - Synthetic Data Notebooks

This directory contains Databricks notebooks to create synthetic healthcare data for the Ontos demo.

## Prerequisites

1. **Unity Catalog Access**: Ensure you have permissions to create catalogs, schemas, and tables
2. **Databricks Runtime**: DBR 13.3 LTS or higher
3. **Python Libraries**: `faker`, `databricks-sdk` (pre-installed on DBR)

## Setup Instructions

### Step 1: Create Unity Catalog Structure

Run this SQL in a Databricks SQL warehouse or notebook:

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS healthcare_payor
COMMENT 'Healthcare Payor Demo - HealthCare Plus Insurance';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS healthcare_payor.claims
COMMENT 'Claims processing and adjudication data';

CREATE SCHEMA IF NOT EXISTS healthcare_payor.members
COMMENT 'Member enrollment and demographics';

CREATE SCHEMA IF NOT EXISTS healthcare_payor.providers
COMMENT 'Provider network directory';

CREATE SCHEMA IF NOT EXISTS healthcare_payor.clinical
COMMENT 'Clinical events and diagnoses';

CREATE SCHEMA IF NOT EXISTS healthcare_payor.quality
COMMENT 'HEDIS quality measures and Star Ratings';

CREATE SCHEMA IF NOT EXISTS healthcare_payor.analytics
COMMENT 'Aggregated analytical datasets (Member 360, etc.)';

-- Grant permissions
GRANT USE CATALOG ON CATALOG healthcare_payor TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.claims TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.members TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.providers TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.clinical TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.quality TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.analytics TO `account users`;
```

### Step 2: Run Data Generation Notebooks

Execute notebooks in this order:

1. **01_create_claims_tables.py** - Creates claims data (100K records)
2. **02_create_member_tables.py** - Creates member profiles (50K members)
3. **03_create_provider_tables.py** - Creates provider network (5K providers)
4. **04_create_clinical_tables.py** - Creates clinical events (500K events)
5. **05_create_quality_tables.py** - Creates HEDIS measures (50K records)
6. **06_create_analytics_tables.py** - Creates Member 360 aggregate table

**Execution Time**: ~10-15 minutes total on a medium-sized cluster

### Step 3: Verify Tables

```sql
-- List all tables
SHOW TABLES IN healthcare_payor.claims;
SHOW TABLES IN healthcare_payor.members;

-- Sample data
SELECT * FROM healthcare_payor.claims.adjudicated_claims LIMIT 10;
SELECT * FROM healthcare_payor.members.member_profiles LIMIT 10;

-- Check row counts
SELECT COUNT(*) FROM healthcare_payor.claims.adjudicated_claims;
SELECT COUNT(*) FROM healthcare_payor.members.member_profiles;
```

### Step 4: Link to Ontos

After tables are created:

1. Navigate to Ontos → **Data Products → Contracts**
2. Update Data Contracts with `physicalName`:
   - Claims Contract: `healthcare_payor.claims.adjudicated_claims`
   - Members Contract: `healthcare_payor.members.member_profiles`
   - etc.

3. Navigate to **Data Products → Products**
4. Update Output Ports with `assetIdentifier` matching UC table names

5. Navigate to **Settings → Jobs**
6. Run **UC Tag Sync** job to apply governed tags

7. Verify tags:
```sql
SHOW TAGS ON TABLE healthcare_payor.claims.adjudicated_claims;
```

## Synthetic Data Details

### Claims (`adjudicated_claims`)
- **Rows**: 100,000 claims
- **Date Range**: 2023-01-01 to 2024-12-31
- **Claim Types**: Professional, Institutional, Dental, Pharmacy
- **ICD-10 Codes**: Realistic distribution (Diabetes, Hypertension, etc.)
- **CPT Codes**: Common procedures (Office visits, Labs, Imaging)
- **Amounts**: Realistic billed/allowed/paid distributions
- **Network Status**: 80% in-network, 20% out-of-network

### Members (`member_profiles`)
- **Rows**: 50,000 members
- **Demographics**: Realistic age/gender distribution
- **Plans**: HMO, PPO, EPO, POS
- **Enrollment**: Active and terminated members
- **Risk Scores**: HCC RAF scores 0.5 - 3.0

### Providers (`provider_directory`)
- **Rows**: 5,000 providers
- **Types**: Physicians, Facilities, Organizations
- **Specialties**: 50+ specialties (Primary Care, Cardiology, etc.)
- **NPI**: Valid 10-digit NPIs
- **Network Status**: 90% in-network
- **Geographic Distribution**: US states

### Clinical Events (`member_clinical_events`)
- **Rows**: 500,000 events
- **Types**: Diagnoses, Procedures, Medications, Labs
- **Codes**: ICD-10, CPT, NDC, LOINC
- **Chronic Conditions**: Diabetes, HTN, CHF, COPD
- **HCC Codes**: Risk adjustment categories

### Quality Measures (`hedis_measures`)
- **Rows**: 50,000 measure records
- **Measures**: CDC (Diabetes Care), CBP (Blood Pressure), BCS (Breast Cancer Screening)
- **Compliance**: ~70% compliant rate
- **Gaps**: Identified care gaps for outreach

### Member 360 (`member_360_view`)
- **Rows**: 50,000 members
- **Data**: Integrated view of members + claims + clinical + quality
- **Aggregations**: Total costs, utilization, risk scores, care gaps

## Data Relationships

```
member_profiles (50K)
    │
    ├─→ adjudicated_claims (100K)
    │       └─→ provider_directory (5K)
    │
    ├─→ member_clinical_events (500K)
    │       └─→ provider_directory (5K)
    │
    ├─→ hedis_measures (50K)
    │
    └─→ member_360_view (50K)
```

## Customization

To adjust data volume, edit the notebook parameters:

```python
# At top of each notebook
NUM_MEMBERS = 50_000  # Adjust member count
NUM_CLAIMS = 100_000  # Adjust claim count
START_DATE = "2023-01-01"  # Adjust date range
END_DATE = "2024-12-31"
```

## Cleanup

To remove all demo data:

```sql
DROP SCHEMA healthcare_payor.analytics CASCADE;
DROP SCHEMA healthcare_payor.quality CASCADE;
DROP SCHEMA healthcare_payor.clinical CASCADE;
DROP SCHEMA healthcare_payor.providers CASCADE;
DROP SCHEMA healthcare_payor.members CASCADE;
DROP SCHEMA healthcare_payor.claims CASCADE;
DROP CATALOG healthcare_payor CASCADE;
```

## Troubleshooting

### Permission Errors
- Ensure you have `CREATE SCHEMA` and `CREATE TABLE` permissions on `healthcare_payor` catalog
- If using Unity Catalog with external locations, ensure cloud storage access

### Cluster Requirements
- **Min**: 2 nodes, 8 GB RAM each
- **Recommended**: 4 nodes, 16 GB RAM each for faster generation

### Package Issues
If `faker` is not installed:
```python
%pip install faker
dbutils.library.restartPython()
```

## Next Steps

After creating tables:
1. Update Ontos Data Contracts with `physicalName`
2. Update Ontos Data Products with `assetIdentifier` in output ports
3. Run UC Tag Sync job in Ontos
4. Verify tags in Unity Catalog
5. Test search and discovery in Ontos
6. Run Compliance checks if configured
