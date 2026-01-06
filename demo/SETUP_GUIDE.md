# Ontos Demo Automated Setup Guide

This guide explains how to programmatically set up the Ontos healthcare demo instead of manually entering data through the UI.

## Two Approaches

### Option 1: API-Based Setup (Recommended)
✅ Uses REST API endpoints
✅ Includes business logic and validation
✅ Safer and more maintainable
✅ Works with local backend AND deployed Databricks Apps
✅ Creates all entity types (domains, teams, projects, contracts, products)

**Authentication:**
- Local: No authentication required
- Databricks Apps: Uses `databricks auth token` for identity token

### Option 2: Direct Database Access
⚠️ Bypasses API layer
⚠️ No validation
⚠️ Use only for development/testing
✅ Faster for bulk operations
✅ Works when you have direct database access
⚠️ Only creates domains, teams, projects (not contracts/products)

---

## Option 1: API-Based Setup

### For Local Development

```bash
# Start local backend
cd src/backend
hatch -e dev run uvicorn src.app:app --reload --port 8000

# Run setup (in another terminal)
python demo/setup_ontos_demo.py
```

### For Databricks Apps

```bash
# Configure Databricks CLI (one-time setup)
databricks auth login --profile e2-demo-field-eng

# Run setup with your app URL
python demo/setup_ontos_demo.py \
  --base-url https://marcin-ontos-1444828305810485.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng

# Continue on errors (don't stop at first failure)
python demo/setup_ontos_demo.py \
  --base-url https://marcin-ontos-1444828305810485.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng \
  --no-fail-fast
```

### What It Creates

The script creates via API:

1. **Data Domains** (4 domains)
   - Healthcare Core (parent)
   - Clinical
   - Claims & Operations
   - Member & Analytics

2. **Teams** (4 teams)
   - claims-engineering
   - member-analytics
   - clinical-data-science
   - governance-compliance

3. **Projects** (3 projects)
   - claims-modernization
   - member-360
   - predictive-care-mgmt

4. **Data Contracts** (from YAML files in `contracts/`)
   - Claims contract
   - Members contract
   - Providers contract
   - Clinical events contract
   - Quality measures contract

5. **Data Products** (from `src/backend/src/data/data_products.yaml`)
   - Claims Data Stream
   - Member 360 View
   - High-Risk Member Predictions
   - etc.

### Selective Creation

Skip specific entity types:

```bash
# Skip domains and teams (already created)
python demo/setup_ontos_demo.py --skip-domains --skip-teams

# Only create contracts and products
python demo/setup_ontos_demo.py --skip-domains --skip-teams --skip-projects
```

### Verify Setup

The script automatically verifies at the end. Manual verification:

```bash
curl http://localhost:8000/api/data-domains | jq length
curl http://localhost:8000/api/teams | jq length
curl http://localhost:8000/api/projects | jq length
curl http://localhost:8000/api/data-contracts | jq length
curl http://localhost:8000/api/data-products | jq length
```

---

## Option 2: Direct Database Access

### Prerequisites

Set database connection URL:

```bash
# Get from .env file in src/backend/
export DATABASE_URL="postgresql://user:password@host:5432/database"

# Or from Databricks App configuration
export DATABASE_URL="postgresql://ontos:password@your-db.postgres.database.azure.com:5432/ontos"
```

### Run Setup Script

```bash
python demo/setup_ontos_db_direct.py --db-url $DATABASE_URL

# Or using environment variable
python demo/setup_ontos_db_direct.py
```

**⚠️ Warning:** This will prompt for confirmation before modifying the database.

### What It Creates

Direct DB script creates:

1. ✅ Data Domains
2. ✅ Teams
3. ✅ Projects
4. ❌ Contracts (use API script for these)
5. ❌ Products (use API script for these)

**Why not contracts/products?** They have complex nested relationships and validation logic that's best handled by the API.

### Verify Setup

```sql
-- Connect to PostgreSQL
psql $DATABASE_URL

-- Check counts
SELECT COUNT(*) FROM data_domains;
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM projects;

-- View created entities
SELECT id, name, description FROM data_domains;
SELECT id, name, title, domain_id FROM teams;
SELECT id, name, title, owner_team_id FROM projects;
```

---

## Recommended Approach by Environment

### For Local Development
Use the API-based setup (Option 1):

```bash
# Start backend
cd src/backend && hatch -e dev run uvicorn src.app:app --reload --port 8000

# Run setup (in another terminal)
python demo/setup_ontos_demo.py
```

### For Deployed Databricks Apps
Use the API-based setup (Option 1 - **Recommended**):

```bash
# Configure Databricks CLI (one-time)
databricks auth login --profile e2-demo-field-eng

# Run setup
python demo/setup_ontos_demo.py \
  --base-url https://marcin-ontos-1444828305810485.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng
```

**Alternative:** Direct database access (Option 2) if you don't have Databricks CLI:

```bash
# Get DATABASE_URL from app configuration or .env
export DATABASE_URL="postgresql://user:password@host:5432/ontos"

# Run setup (only creates domains, teams, projects)
python demo/setup_ontos_db_direct.py
```

---

## Troubleshooting

### Script stops at first error

**Cause:** Default fail-fast behavior (by design)
**Solution:**
- This is intentional - the script stops immediately when an error occurs
- Review the error message which includes the URL and response details
- Fix the underlying issue (backend not running, wrong URL, etc.)
- To see all errors instead of stopping at the first one, use `--no-fail-fast`

### Error: "Connection refused" (API script)

**Cause:** Backend not running
**Solution:**
```bash
cd src/backend
hatch -e dev run uvicorn src.app:app --reload --port 8000
```

### Error: "could not connect to server" (DB script)

**Cause:** Incorrect database URL or PostgreSQL not accessible
**Solution:**
- Verify DATABASE_URL is correct
- Check PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### Error: "404 Not Found" for API endpoints

**Cause:** Backend routes not registered or incorrect URL
**Solution:**
- Verify backend is running: `curl http://localhost:8000/api/version`
- Check logs: `tail -f /tmp/backend.log`
- Ensure you're using the correct port (default: 8000)

### Error: "Duplicate key value violates unique constraint"

**Cause:** Entities already exist in database
**Solution:**
- Delete existing entities first
- Or use `--skip-*` flags to avoid recreating

### Contracts/Products not created (API script)

**Cause:** YAML files not found
**Solution:**
```bash
# Check files exist
ls contracts/*.yaml
ls src/backend/src/data/data_products.yaml

# Specify custom paths
python demo/setup_ontos_demo.py \
  --contracts-dir /path/to/contracts \
  --data-dir /path/to/data
```

---

## Cleanup

### Remove all demo data (API)

```bash
# Via API (if delete endpoints exist)
curl -X DELETE http://localhost:8000/api/data-domains/{id}
curl -X DELETE http://localhost:8000/api/teams/{id}
curl -X DELETE http://localhost:8000/api/projects/{id}
# ... etc
```

### Remove all demo data (Direct DB)

```sql
-- Connect to database
psql $DATABASE_URL

-- Delete in reverse order of dependencies
DELETE FROM data_products WHERE id IN (SELECT id FROM data_products LIMIT 100);
DELETE FROM data_contracts WHERE id IN (SELECT id FROM data_contracts LIMIT 100);
DELETE FROM projects WHERE name LIKE '%modernization%' OR name LIKE '%360%' OR name LIKE '%predictive%';
DELETE FROM teams WHERE name LIKE '%-engineering' OR name LIKE '%-analytics' OR name LIKE '%-science' OR name LIKE '%governance%';
DELETE FROM data_domains WHERE name LIKE '%Healthcare%' OR name LIKE '%Clinical%' OR name LIKE '%Claims%' OR name LIKE '%Member%';
```

**⚠️ WARNING:** Be very careful with DELETE statements. Consider backing up first:

```bash
pg_dump $DATABASE_URL > backup_before_cleanup.sql
```

---

## Integration with Unity Catalog Setup

After setting up Ontos demo data:

1. **Create Unity Catalog tables** (from main demo):
   ```bash
   python demo/scripts/00_setup_catalog.py --config demo/settings.yaml
   ```

2. **Upload sample data**:
   - Use Databricks UI to upload `demo/data/*_sample.csv`
   - Or use upload scripts

3. **Update Contracts with Physical Names**:
   - Edit contracts via API/UI to add `physicalName` fields
   - Link to Unity Catalog tables (e.g., `healthcare_payor.claims.adjudicated_claims`)

4. **Update Products with Asset Identifiers**:
   - Edit products via API/UI to add `assetIdentifier` in output ports
   - Link to Unity Catalog tables

5. **Run UC Tag Sync**:
   - Navigate to Settings → Jobs in Ontos UI
   - Run "UC Tag Sync" job
   - Verify tags applied to UC tables

---

## Summary: Complete Demo Setup

### For Local Development

```bash
# 1. Start local backend
cd src/backend
hatch -e dev run uvicorn src.app:app --reload --port 8000

# 2. Setup Ontos metadata (in another terminal)
python demo/setup_ontos_demo.py

# 3. Create Unity Catalog structure
python demo/scripts/00_setup_catalog.py --config demo/settings.yaml

# 4. Upload sample data to UC (via Databricks UI or script)
# ... manual step ...

# 5. Update contracts/products with UC physical names (via API or UI)
# ... manual step ...

# 6. Verify setup
curl http://localhost:8000/api/data-contracts | jq
```

### For Deployed Databricks App

```bash
# 1. Configure Databricks CLI (one-time)
databricks auth login --profile e2-demo-field-eng

# 2. Setup Ontos metadata
python demo/setup_ontos_demo.py \
  --base-url https://marcin-ontos-1444828305810485.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng

# 3-6. Same as local development (Unity Catalog steps)
```

**Estimated time:** 5-10 minutes (vs. 1-2 hours manual UI entry)

---

## Next Steps

After automated setup:

1. ✅ Log into Ontos UI and verify all entities
2. ✅ Update contract `physicalName` fields to point to UC tables
3. ✅ Update product output ports with UC `assetIdentifier`
4. ✅ Run data quality checks workflow
5. ✅ Follow the DEMO.md walkthrough for the full demo flow

---

**Created:** 2026-01-05
**Version:** 1.0.0
**Maintainer:** Data Governance Team
