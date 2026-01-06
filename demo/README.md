# Healthcare Payor Demo - Setup Guide

This directory contains **static sample CSV files** and setup scripts for creating synthetic healthcare data in Databricks Unity Catalog for the Ontos demo.

## Quick Start (Static Data Upload)

**Option 1: Manual Upload via Databricks UI (Recommended for simplicity)**

1. Create Unity Catalog structure:
```bash
python scripts/00_setup_catalog.py --config settings.yaml
```

2. Upload CSV files via Databricks UI:
   - Navigate to Databricks SQL or Catalog Explorer
   - Select catalog `healthcare_payor`
   - Upload `data/members_sample.csv` → `members.member_profiles`
   - Upload `data/providers_sample.csv` → `providers.provider_directory`
   - Upload `data/claims_sample.csv` → `claims.adjudicated_claims`

**Option 2: Programmatic Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your Databricks connection
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi1234567890abcdef..."
export DATABRICKS_WAREHOUSE_ID="abc123def456"

# Create catalog and schemas
python scripts/00_setup_catalog.py --config settings.yaml

# Upload data (creates tables, ready for manual CSV import)
python scripts/01_upload_members.py --config settings.yaml --csv data/members_sample.csv
```

## What Gets Created

The setup scripts create:

### Unity Catalog Structure

- **Catalog**: `healthcare_payor`
- **Schemas**: `claims`, `members`, `providers`, `clinical`, `quality`, `analytics`

### Static Sample Data Files

**Ready-to-upload CSV files in `demo/data/`:**

| File | Rows | Description | Quality Issues |
|------|------|-------------|----------------|
| `members_sample.csv` | 15 | Member demographics and enrollment | 7 issues (missing values, invalid state) |
| `providers_sample.csv` | 10 | Provider network directory | 1 issue (out-of-network) |
| `claims_sample.csv` | 15 | Medical claims with diagnoses/procedures | 6 issues (future dates, invalid codes, orphans, negatives, outliers) |

See **[DATA_MANIFEST.md](data/DATA_MANIFEST.md)** for detailed quality issue documentation.

**Full-scale data generation (optional):**

| Table (Generated) | Rows | Description |
|-------------------|------|-------------|
| `members.csv` | 50,000 | Full member dataset |
| `claims.csv` | 100,000 | Full claims dataset |
| `providers.csv` | 5,000 | Full provider directory |

Generate with: `python scripts/generate_static_data.py --config settings.yaml`

### Intentional Data Quality Issues

The setup scripts inject configurable data quality issues to demonstrate quality checks:

| Issue Type | Default Rate | Example |
|------------|--------------|---------|
| Missing values | 2% | Null values in nullable fields |
| Invalid codes | 1% | Invalid ICD-10/CPT codes |
| Orphaned references | 0.5% | Claims with non-existent member_id |
| Duplicate records | 1% | Duplicate claim_ids |
| Future dates | 0.5% | Service dates in the future |
| Negative amounts | 1% | Negative billed_amount |
| Outlier amounts | 3% | Extreme amounts (>$100k) |

## Configuration

Edit `settings.yaml` to customize:

### Databricks Connection

```yaml
databricks:
  host: "${DATABRICKS_HOST}"
  token: "${DATABRICKS_TOKEN}"
  warehouse_id: "${DATABRICKS_WAREHOUSE_ID}"
```

### Data Volumes (for generation script)

```yaml
data_generation:
  volumes:
    members: 1000        # Set to 50000 for full demo
    claims: 2000         # Set to 100000 for full demo
    providers: 500       # Set to 5000 for full demo
    clinical_events: 5000    # Set to 500000 for full demo (not yet implemented)
    quality_measures: 1000   # Set to 50000 for full demo (not yet implemented)
```

**Note:** Sample files (`*_sample.csv`) contain 10-15 rows each and are ready to use immediately.

### Data Quality Issues

```yaml
data_generation:
  quality_issues:
    enabled: true
    missing_values: 0.02        # 2%
    invalid_codes: 0.01         # 1%
    orphaned_references: 0.005  # 0.5%
    duplicate_records: 0.01     # 1%
    future_dates: 0.005         # 0.5%
    negative_amounts: 0.01      # 1%
    outlier_amounts: 0.03       # 3%
```

Set `enabled: false` to generate clean data without quality issues.

## Usage Examples

### Working with Static Sample Files

**1. Create Catalog Structure:**
```bash
python scripts/00_setup_catalog.py --config settings.yaml
```

**2. Upload Sample Data via Databricks UI:**
- Open Databricks Catalog Explorer
- Navigate to `healthcare_payor` catalog
- For each schema, create table and upload corresponding CSV:
  - `members.member_profiles` ← `data/members_sample.csv`
  - `providers.provider_directory` ← `data/providers_sample.csv`
  - `claims.adjudicated_claims` ← `data/claims_sample.csv`

**3. Verify Data:**
```sql
SELECT COUNT(*) FROM healthcare_payor.members.member_profiles;  -- Should return 15
SELECT COUNT(*) FROM healthcare_payor.providers.provider_directory;  -- Should return 10
SELECT COUNT(*) FROM healthcare_payor.claims.adjudicated_claims;  -- Should return 15
```

### Generating Larger Datasets

**Create full-scale data files (50K-100K rows):**
```bash
# Edit settings.yaml to increase volumes
# Then generate:
python scripts/generate_static_data.py --config settings.yaml --output-dir data

# This creates:
# - data/members.csv (50K rows)
# - data/claims.csv (100K rows)
# - data/providers.csv (5K rows)
```

**Upload generated files:**
```bash
# Use COPY INTO or Databricks UI to load the larger CSV files
# Or use pandas via Databricks Connect
```

### Cleanup

```bash
# Remove all demo data
python scripts/00_setup_catalog.py --clean
# Or via SQL:
DROP CATALOG healthcare_payor CASCADE;
```

## Directory Structure

```
demo/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── settings.yaml             # Configuration file
├── setup_workspace.py        # Main orchestrator script
├── lib/                      # Shared utilities
│   ├── __init__.py
│   ├── config.py            # Configuration loading
│   ├── databricks_client.py # Databricks SDK wrapper
│   ├── data_quality.py      # DQ issue injection utilities
│   └── synthetic_data.py    # Synthetic data generators
├── scripts/                  # Individual setup scripts
│   ├── __init__.py
│   ├── 00_setup_catalog.py # Create catalog and schemas
│   ├── 01_create_claims.py # Claims table (TODO)
│   ├── 02_create_members.py # Members table (TODO)
│   ├── 03_create_providers.py # Providers table (TODO)
│   ├── 04_create_clinical.py # Clinical events table (TODO)
│   ├── 05_create_quality.py # Quality measures table (TODO)
│   ├── 06_create_analytics.py # Member 360 table (TODO)
│   └── 99_verify_setup.py  # Verification script (TODO)
└── data/                     # Reference data (TODO)
    ├── icd10_codes.json
    ├── cpt_codes.json
    ├── specialties.json
    └── place_of_service.json
```

## Implementation Status

- ✅ Configuration management (`settings.yaml`, `lib/config.py`)
- ✅ Databricks SDK client wrapper (`lib/databricks_client.py`)
- ✅ Data quality injection utilities (`lib/data_quality.py`)
- ✅ Synthetic data generators (`lib/synthetic_data.py`)
- ✅ Catalog setup script (`scripts/00_setup_catalog.py`)
- ✅ **Static sample data files** (`data/*_sample.csv`) - Ready to use!
- ✅ Data quality manifest (`data/DATA_MANIFEST.md`)
- ✅ Data generation script (`scripts/generate_static_data.py`)
- ⏳ Upload automation scripts (01-06) - **Optional** (manual upload via UI is simpler)
- ⏳ Clinical events & quality measures data - **TODO**
- ⏳ Member 360 aggregation - **TODO**

## Next Steps (Optional Enhancements)

The demo is **ready to use** with the sample CSV files. Optional improvements:

1. **Add clinical events & quality measures data**
   - Extend `generate_static_data.py` to create these files
   - Follow same pattern as members/claims/providers

2. **Create automated upload scripts**
   - Alternative to manual UI upload
   - Use Databricks Connect or SQL warehouse bulk loading
   - Handle large CSV files efficiently

3. **Add member 360 aggregation**
   - SQL script to create `analytics.member_360_view`
   - Join members + claims + clinical + quality data

4. **Integrate with Synthea**
   - Use Synthea-generated FHIR data
   - Convert to our schema format
   - More realistic clinical data

5. **Add data validation**
   - Verification script to check quality issue counts
   - Compare actual vs. expected issues
   - Generate test reports

## Troubleshooting

### Error: "Configuration file not found"

Ensure `settings.yaml` exists in the `demo/` directory.

### Error: "Missing required config: databricks.host"

Set environment variables or edit `settings.yaml` with your Databricks connection details.

### Error: "SQL Warehouse not found"

Verify your `DATABRICKS_WAREHOUSE_ID` is correct and the warehouse is running.

### Error: "Permission denied"

Ensure your Databricks token has permissions to:
- Create catalogs and schemas
- Create tables
- Execute SQL queries via SQL Warehouse

### Tables take a long time to create

Adjust `data_generation.volumes` in `settings.yaml` to reduce the number of rows generated.

## Support

For issues or questions:
- See main [DEMO.md](../DEMO.md) for full walkthrough
- Check [UC_INTEGRATION.md](../UC_INTEGRATION.md) for Unity Catalog integration details
- Review individual script files for implementation details
