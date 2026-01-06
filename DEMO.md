# Ontos Healthcare Payor Demo Setup

This demo showcases Ontos in a **healthcare payor** (insurance provider) context, demonstrating how to manage data products, contracts, semantic models, and governance workflows for a modern health insurance organization.

## Important Note on Features

**Semantic Models vs. Business Glossaries:**
- The current version uses **Semantic Models** (under Governance) for exploring ontologies and taxonomies
- Semantic Models provides **read-only** access to concepts loaded from RDF/SKOS files
- **Custom Business Glossaries** (user-created terminology via UI) is planned but not yet implemented
- For now, embed business terminology directly in Data Contract descriptions and schema fields

## Demo Scenario Overview

**HealthCare Plus Insurance** is a regional health insurance payor serving 2 million members. They're implementing a data mesh architecture to improve member experience, reduce claim processing times, and enable analytics-driven care management programs.

This demo includes:
- **3 Data Domains** (Clinical, Operations, Analytics)
- **4 Teams** (Claims Engineering, Member Analytics, Clinical Data Science, Data Governance)
- **3 Projects** (Claims Modernization, Member 360, Predictive Care Management)
- **5 Data Contracts** (Claims, Members, Providers, Clinical Events, Quality Measures)
- **Healthcare terminology reference** (clinical, financial, and regulatory terms for use in contracts)
- **3 Data Products** demonstrating source-aligned, aggregate, and consumer-aligned patterns

## Prerequisites

- Ontos application deployed to Databricks Apps
- Admin access to the application
- PostgreSQL database configured and accessible
- Unity Catalog with appropriate permissions
- Databricks SQL Warehouse (for running setup scripts)
- Permissions to create catalogs, schemas, and tables in Unity Catalog
- Python 3.9+ installed locally (for running setup scripts)

## Quick Setup (Automated)

For a fast setup with synthetic data in Unity Catalog, use the automated setup scripts:

### Step 1: Install Dependencies

```bash
# From the project root
cd demo
pip install -r requirements.txt
```

### Step 2: Configure Settings

Edit `demo/settings.yaml` and set your Databricks connection details:

```yaml
databricks:
  host: "https://your-workspace.cloud.databricks.com"
  token: "dapi1234567890abcdef..."  # Your personal access token
  warehouse_id: "abc123def456"      # Your SQL Warehouse ID
```

You can also use environment variables:
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi1234567890abcdef..."
export DATABRICKS_WAREHOUSE_ID="abc123def456"
```

### Step 3: Run Full Setup

```bash
# Run all setup steps (creates catalog, schemas, and loads synthetic data)
python setup_workspace.py --config settings.yaml --all

# Or run in dry-run mode to validate first
python setup_workspace.py --config settings.yaml --all --dry-run
```

This will create:
- Unity Catalog: `healthcare_payor`
- Schemas: `claims`, `members`, `providers`, `clinical`, `quality`, `analytics`
- Tables with synthetic data:
  - **50,000 members** with demographics and enrollment
  - **100,000 claims** with diagnoses and procedures
  - **5,000 providers** in the network directory
  - **500,000 clinical events** (diagnoses, medications, labs)
  - **50,000 HEDIS quality measures**
  - **Member 360** aggregated view

### Step 4: Verify Setup

```bash
python setup_workspace.py --config settings.yaml --verify
```

### Step 5: Optional - Setup Specific Tables Only

```bash
# Create just claims and members
python setup_workspace.py --config settings.yaml --tables claims,members

# Skip catalog creation if it already exists
python setup_workspace.py --config settings.yaml --all --skip-catalog
```

### Step 6: Clean Up (Optional)

```bash
# Remove all demo data and catalog
python setup_workspace.py --config settings.yaml --clean --yes
```

**Note**: The setup scripts inject intentional data quality issues (configurable in `settings.yaml`) to demonstrate data quality checks. See the "Data Quality Checks Walkthrough" section below.

---

## Manual Setup Steps (Detailed)

### Step 1: Configure Data Domains

Navigate to **Settings → Data Domains** and create the following domains:

#### 1. **Healthcare Core** (Parent Domain)
- **Name**: `Healthcare Core`
- **Description**: `Foundational healthcare concepts applicable across all business functions`
- **Tags**: `healthcare`, `enterprise`, `core`

#### 2. **Clinical Domain**
- **Name**: `Clinical`
- **Description**: `Clinical data including diagnoses, procedures, medications, and care events`
- **Parent Domain**: `Healthcare Core`
- **Tags**: `clinical`, `hipaa`, `phi`

#### 3. **Claims & Operations**
- **Name**: `Claims & Operations`
- **Description**: `Claims processing, provider networks, and operational data`
- **Parent Domain**: `Healthcare Core`
- **Tags**: `claims`, `operations`, `financial`

#### 4. **Member & Analytics**
- **Name**: `Member & Analytics`
- **Description**: `Member profiles, engagement data, and analytical insights`
- **Parent Domain**: `Healthcare Core`
- **Tags**: `member`, `analytics`, `engagement`

### Step 2: Create Teams

Navigate to **Settings → Teams** and create the following teams:

#### 1. **Claims Data Engineering**
- **Name**: `claims-engineering`
- **Title**: `Claims Data Engineering Team`
- **Domain**: `Claims & Operations`
- **Description**: `Responsible for claims data pipelines, EDI processing, and provider data integration`
- **Tags**: `claims`, `engineering`, `etl`
- **Metadata**:
  - Slack Channel: `#claims-data-eng`
  - Lead: `claims-lead@healthcareplus.com`
- **Members**:
  - Add your engineering group
  - Assign role: `Data Producer`

#### 2. **Member Analytics**
- **Name**: `member-analytics`
- **Title**: `Member Analytics Team`
- **Domain**: `Member & Analytics`
- **Description**: `Member experience analytics, segmentation, and engagement analysis`
- **Tags**: `analytics`, `member`, `reporting`
- **Metadata**:
  - Slack Channel: `#member-analytics`
  - Tools: `["Tableau", "Databricks SQL", "dbt"]`
- **Members**:
  - Add your analytics group
  - Assign role: `Data Consumer`

#### 3. **Clinical Data Science**
- **Name**: `clinical-data-science`
- **Title**: `Clinical Data Science Team`
- **Domain**: `Clinical`
- **Description**: `Predictive modeling for care management, risk adjustment, and utilization forecasting`
- **Tags**: `data-science`, `ml`, `clinical`, `predictive`
- **Metadata**:
  - Slack Channel: `#clinical-ds`
  - Research Areas: `["Risk Stratification", "Readmission Prediction", "Cost Forecasting"]`
- **Members**:
  - Add your data science group
  - Assign role: `Data Producer`

#### 4. **Data Governance & Compliance**
- **Name**: `governance-compliance`
- **Title**: `Data Governance & Compliance Team`
- **Domain**: `Healthcare Core`
- **Description**: `HIPAA compliance, data quality, and governance oversight`
- **Tags**: `governance`, `compliance`, `hipaa`, `quality`
- **Metadata**:
  - Slack Channel: `#data-governance`
  - Responsibilities: `["HIPAA Compliance", "Data Quality", "PHI Access Control"]`
- **Members**:
  - Add your governance group
  - Assign role: `Data Steward`

### Step 3: Create Projects

Navigate to **Settings → Projects** and create the following projects:

#### 1. **Claims Processing Modernization**
- **Name**: `claims-modernization`
- **Title**: `Claims Processing Modernization`
- **Project Type**: `TEAM`
- **Owner Team**: `claims-engineering`
- **Description**: `Modernize claims processing pipeline from EDI 837/835 to real-time adjudication`
- **Tags**: `claims`, `modernization`, `automation`
- **Metadata**:
  - Budget: `$800K`
  - Timeline: `9 months`
  - Stakeholders: `["Claims Operations", "Finance", "Provider Relations"]`
  - Priority: `high`
- **Assigned Teams**: `claims-engineering`, `governance-compliance`

#### 2. **Member 360 Platform**
- **Name**: `member-360`
- **Title**: `Member 360 Platform`
- **Project Type**: `TEAM`
- **Owner Team**: `member-analytics`
- **Description**: `Unified member data platform integrating claims, clinical, and engagement data`
- **Tags**: `member`, `platform`, `360-view`
- **Metadata**:
  - Budget: `$600K`
  - Timeline: `8 months`
  - Stakeholders: `["Member Services", "Care Management", "Marketing"]`
  - Priority: `high`
- **Assigned Teams**: `member-analytics`, `claims-engineering`, `clinical-data-science`

#### 3. **Predictive Care Management**
- **Name**: `predictive-care-mgmt`
- **Title**: `Predictive Care Management`
- **Project Type**: `TEAM`
- **Owner Team**: `clinical-data-science`
- **Description**: `ML models for identifying high-risk members and reducing hospital readmissions`
- **Tags**: `ml`, `predictive`, `care-management`, `risk`
- **Metadata**:
  - Budget: `$450K`
  - Timeline: `6 months`
  - Technologies: `["MLflow", "Databricks ML", "SHAP"]`
  - Compliance: `["HIPAA", "Model Risk Management"]`
  - Priority: `medium`
- **Assigned Teams**: `clinical-data-science`, `governance-compliance`

### Step 4: Understand Semantic Models (Instead of Business Glossary)

**Note:** The current version of Ontos uses **Semantic Models** (not Business Glossaries) for managing terminology. Semantic Models provides read-only access to ontologies and taxonomies loaded from RDF/SKOS files. Custom business glossary creation via UI is planned for a future release.

For this demo, you can use **Semantic Models** to explore healthcare concepts from loaded ontologies:

Navigate to **Governance → Semantic Models**:

**What You Can Do:**

1. **Explore Existing Ontologies:**
   - View the tree of concepts on the left panel
   - Click on concepts to see details, hierarchy, and relationships
   - Click "Knowledge Graph" to visualize concept relationships

2. **Search Concepts:**
   - Use the search bar to find healthcare-related concepts
   - Search for terms like "patient", "diagnosis", "treatment", etc.

3. **View Concept Hierarchies:**
   - Click any concept to see its parent-child relationships in the lineage view

**Healthcare Terminology Reference (for Data Contracts):**

Since custom business glossary creation is not yet available in the UI, you can reference these healthcare terms when defining your data contracts:

- **Member**: Individual covered under a health insurance plan
- **Claim**: Payment request from provider for services rendered
- **Provider**: Healthcare professional or facility
- **ICD-10**: Diagnosis code (e.g., E11.9 = Type 2 Diabetes)
- **CPT**: Procedure code (e.g., 99213 = Office visit)
- **Prior Authorization (PA)**: Pre-approval for certain services
- **Allowed Amount**: Maximum plan payment for a service
- **Member Responsibility**: Patient's cost-sharing (copay, coinsurance, deductible)
- **HEDIS**: Quality measure from NCQA
- **HCC/RAF Score**: Risk adjustment factor for member risk
- **PHI**: Protected Health Information (HIPAA)
- **Network Status**: Provider relationship to plan (in/out of network)

**Alternative for Now:**

You can embed this terminology directly into your Data Contract descriptions and schema field descriptions to provide business context until custom glossary features are added.

### Step 5: Create Data Contracts

Navigate to **Data Contracts** and create the following contracts:

#### 1. **Claims Data Contract**

```yaml
id: "healthcare-claims-v1"
name: "Healthcare Claims Data Contract"
version: "1.0.0"
owner_team: "claims-engineering"
status: "active"
kind: "DataContract"
apiVersion: "v3.0.2"
domain_name: "Claims & Operations"
description:
  purpose: "Standardized claims data including professional and institutional claims for adjudication and analytics"
  usage: "Claims processing, payment, reporting, fraud detection, and member cost analysis"
  limitations: "PHI data - restricted access. Retain 7 years per regulatory requirements. Diagnosis and procedure codes must be valid ICD-10/CPT."

schema:
  - name: claims
    physicalName: "claims.adjudicated_claims"
    properties:
      - name: claim_id
        logicalType: string
        required: true
        unique: true
        description: "Unique claim identifier (internal)"

      - name: claim_number
        logicalType: string
        required: true
        unique: true
        description: "External claim number (from EDI 837)"

      - name: claim_type
        logicalType: string
        required: true
        description: "Claim type: professional, institutional, dental, pharmacy"

      - name: member_id
        logicalType: string
        required: true
        description: "Member identifier (links to members table)"
        classification: "PHI"

      - name: provider_npi
        logicalType: string
        required: true
        description: "National Provider Identifier (10-digit)"

      - name: service_date_from
        logicalType: date
        required: true
        description: "Service start date (YYYY-MM-DD)"

      - name: service_date_to
        logicalType: date
        required: true
        description: "Service end date (YYYY-MM-DD)"

      - name: received_date
        logicalType: date
        required: true
        description: "Date claim received by payor"

      - name: processed_date
        logicalType: date
        required: false
        description: "Date claim was adjudicated"

      - name: paid_date
        logicalType: date
        required: false
        description: "Date claim was paid"

      - name: claim_status
        logicalType: string
        required: true
        description: "Status: submitted, pending, approved, denied, adjusted"

      - name: diagnosis_codes
        logicalType: array
        required: true
        description: "Array of ICD-10 diagnosis codes"

      - name: procedure_codes
        logicalType: array
        required: true
        description: "Array of CPT/HCPCS procedure codes"

      - name: billed_amount
        logicalType: decimal
        required: true
        description: "Total amount billed by provider (USD)"

      - name: allowed_amount
        logicalType: decimal
        required: true
        description: "Total allowed amount per contract (USD)"

      - name: paid_amount
        logicalType: decimal
        required: false
        description: "Total amount paid to provider (USD)"

      - name: member_responsibility
        logicalType: decimal
        required: false
        description: "Member cost-sharing (copay + coinsurance + deductible)"

      - name: network_status
        logicalType: string
        required: true
        description: "Provider network status: in_network, out_of_network, preferred"

      - name: place_of_service
        logicalType: string
        required: true
        description: "Place of service code (e.g., 11=Office, 21=Inpatient Hospital)"

      - name: denial_reason_code
        logicalType: string
        required: false
        description: "Reason code if claim denied"

      - name: created_at
        logicalType: timestamp
        required: true
        description: "Record creation timestamp (UTC)"

      - name: updated_at
        logicalType: timestamp
        required: true
        description: "Record last update timestamp (UTC)"
```

#### 2. **Member Data Contract**

```yaml
id: "healthcare-members-v1"
name: "Healthcare Member Data Contract"
version: "1.0.0"
owner_team: "member-analytics"
status: "active"
kind: "DataContract"
apiVersion: "v3.0.2"
domain_name: "Member & Analytics"
description:
  purpose: "Comprehensive member profiles including demographics, eligibility, and plan enrollment"
  usage: "Member services, eligibility verification, care coordination, and analytics"
  limitations: "PHI data - restricted access. HIPAA compliance required. Email/phone PII must be masked in non-production environments."

schema:
  - name: members
    physicalName: "member.member_profiles"
    properties:
      - name: member_id
        logicalType: string
        required: true
        unique: true
        description: "Unique member identifier (UUID format)"
        classification: "PHI"

      - name: subscriber_id
        logicalType: string
        required: true
        description: "Primary subscriber identifier (if dependent)"
        classification: "PHI"

      - name: first_name
        logicalType: string
        required: true
        description: "Member first name"
        classification: "PHI"

      - name: last_name
        logicalType: string
        required: true
        description: "Member last name"
        classification: "PHI"

      - name: date_of_birth
        logicalType: date
        required: true
        description: "Member date of birth (YYYY-MM-DD)"
        classification: "PHI"

      - name: gender
        logicalType: string
        required: true
        description: "Gender: M, F, X, U (unknown)"

      - name: email
        logicalType: string
        required: false
        description: "Primary email address"
        classification: "PHI"

      - name: phone_number
        logicalType: string
        required: false
        description: "Primary phone number (E.164 format)"
        classification: "PHI"

      - name: address_line1
        logicalType: string
        required: true
        description: "Street address line 1"
        classification: "PHI"

      - name: address_line2
        logicalType: string
        required: false
        description: "Street address line 2"
        classification: "PHI"

      - name: city
        logicalType: string
        required: true
        description: "City"

      - name: state
        logicalType: string
        required: true
        description: "US state code (2-letter)"

      - name: zip_code
        logicalType: string
        required: true
        description: "5 or 9-digit ZIP code"

      - name: plan_id
        logicalType: string
        required: true
        description: "Current health plan identifier"

      - name: enrollment_date
        logicalType: date
        required: true
        description: "Plan enrollment start date"

      - name: termination_date
        logicalType: date
        required: false
        description: "Plan enrollment end date (null if active)"

      - name: member_status
        logicalType: string
        required: true
        description: "Status: active, inactive, terminated, pending"

      - name: primary_care_provider_npi
        logicalType: string
        required: false
        description: "Assigned PCP's National Provider Identifier"

      - name: risk_score
        logicalType: decimal
        required: false
        description: "HCC Risk Adjustment Factor (RAF) score"

      - name: created_at
        logicalType: timestamp
        required: true
        description: "Record creation timestamp (UTC)"

      - name: updated_at
        logicalType: timestamp
        required: true
        description: "Record last update timestamp (UTC)"
```

#### 3. **Provider Network Data Contract**

```yaml
id: "healthcare-providers-v1"
name: "Healthcare Provider Network Data Contract"
version: "1.0.0"
owner_team: "claims-engineering"
status: "active"
kind: "DataContract"
apiVersion: "v3.0.2"
domain_name: "Claims & Operations"
description:
  purpose: "Provider network directory with credentials, specialties, and contract details"
  usage: "Claims processing, provider search, network adequacy analysis, credentialing"
  limitations: "Provider data must be updated quarterly. NPI validation required. Contract rates are confidential."

schema:
  - name: providers
    physicalName: "provider.provider_directory"
    properties:
      - name: provider_id
        logicalType: string
        required: true
        unique: true
        description: "Internal provider identifier"

      - name: npi
        logicalType: string
        required: true
        unique: true
        description: "National Provider Identifier (10-digit)"

      - name: provider_type
        logicalType: string
        required: true
        description: "Type: individual, facility, organization"

      - name: first_name
        logicalType: string
        required: false
        description: "Provider first name (for individuals)"

      - name: last_name
        logicalType: string
        required: false
        description: "Provider last name (for individuals)"

      - name: organization_name
        logicalType: string
        required: false
        description: "Organization/facility name"

      - name: specialty_code
        logicalType: string
        required: true
        description: "Primary specialty (taxonomy code)"

      - name: specialty_description
        logicalType: string
        required: true
        description: "Specialty description (e.g., Internal Medicine)"

      - name: network_status
        logicalType: string
        required: true
        description: "Status: in_network, out_of_network, preferred, terminated"

      - name: contract_start_date
        logicalType: date
        required: false
        description: "Network contract start date"

      - name: contract_end_date
        logicalType: date
        required: false
        description: "Network contract end date"

      - name: accepting_new_patients
        logicalType: boolean
        required: true
        description: "Whether provider is accepting new patients"

      - name: address_line1
        logicalType: string
        required: true
        description: "Primary practice address line 1"

      - name: address_line2
        logicalType: string
        required: false
        description: "Primary practice address line 2"

      - name: city
        logicalType: string
        required: true
        description: "City"

      - name: state
        logicalType: string
        required: true
        description: "US state code (2-letter)"

      - name: zip_code
        logicalType: string
        required: true
        description: "5 or 9-digit ZIP code"

      - name: phone_number
        logicalType: string
        required: true
        description: "Primary phone number"

      - name: credentialing_status
        logicalType: string
        required: true
        description: "Status: credentialed, pending, expired, suspended"

      - name: credentialing_date
        logicalType: date
        required: false
        description: "Most recent credentialing date"

      - name: created_at
        logicalType: timestamp
        required: true
        description: "Record creation timestamp (UTC)"

      - name: updated_at
        logicalType: timestamp
        required: true
        description: "Record last update timestamp (UTC)"
```

#### 4. **Clinical Events Data Contract**

```yaml
id: "healthcare-clinical-events-v1"
name: "Healthcare Clinical Events Data Contract"
version: "1.0.0"
owner_team: "clinical-data-science"
status: "active"
kind: "DataContract"
apiVersion: "v3.0.2"
domain_name: "Clinical"
description:
  purpose: "Clinical events including diagnoses, procedures, medications, and lab results for care management"
  usage: "Risk stratification, care gap analysis, predictive modeling, quality measures"
  limitations: "PHI data - highly restricted. Real-time feed has 2-hour lag. Codes must be valid per coding standards."

schema:
  - name: clinical_events
    physicalName: "clinical.member_clinical_events"
    properties:
      - name: event_id
        logicalType: string
        required: true
        unique: true
        description: "Unique clinical event identifier"
        classification: "PHI"

      - name: member_id
        logicalType: string
        required: true
        description: "Member identifier"
        classification: "PHI"

      - name: event_date
        logicalType: date
        required: true
        description: "Date of clinical event"

      - name: event_type
        logicalType: string
        required: true
        description: "Type: diagnosis, procedure, medication, lab_result, hospitalization"

      - name: icd10_code
        logicalType: string
        required: false
        description: "ICD-10 diagnosis code"

      - name: icd10_description
        logicalType: string
        required: false
        description: "Diagnosis description"

      - name: cpt_code
        logicalType: string
        required: false
        description: "CPT/HCPCS procedure code"

      - name: cpt_description
        logicalType: string
        required: false
        description: "Procedure description"

      - name: medication_ndc
        logicalType: string
        required: false
        description: "NDC (National Drug Code) for medications"

      - name: medication_name
        logicalType: string
        required: false
        description: "Medication name"

      - name: lab_loinc_code
        logicalType: string
        required: false
        description: "LOINC code for lab tests"

      - name: lab_result_value
        logicalType: string
        required: false
        description: "Lab result value"

      - name: lab_result_unit
        logicalType: string
        required: false
        description: "Lab result unit of measure"

      - name: provider_npi
        logicalType: string
        required: true
        description: "Rendering provider NPI"

      - name: facility_npi
        logicalType: string
        required: false
        description: "Facility NPI (if applicable)"

      - name: is_chronic_condition
        logicalType: boolean
        required: true
        description: "Whether event relates to chronic condition"

      - name: hcc_code
        logicalType: string
        required: false
        description: "Hierarchical Condition Category code"

      - name: hcc_weight
        logicalType: decimal
        required: false
        description: "HCC risk weight"

      - name: source_system
        logicalType: string
        required: true
        description: "Source: claims, ehr, lab, pharmacy"

      - name: created_at
        logicalType: timestamp
        required: true
        description: "Record creation timestamp (UTC)"

      - name: updated_at
        logicalType: timestamp
        required: true
        description: "Record last update timestamp (UTC)"
```

#### 5. **Quality Measures Data Contract**

```yaml
id: "healthcare-quality-measures-v1"
name: "Healthcare Quality Measures Data Contract"
version: "1.0.0"
owner_team: "clinical-data-science"
status: "active"
kind: "DataContract"
apiVersion: "v3.0.2"
domain_name: "Clinical"
description:
  purpose: "HEDIS and Star Ratings quality measure results for members"
  usage: "Quality reporting, Star Ratings submission, provider performance, care gap identification"
  limitations: "Updated monthly. NCQA specifications must be followed. Historical data retained 5 years."

schema:
  - name: quality_measures
    physicalName: "quality.hedis_measures"
    properties:
      - name: measure_id
        logicalType: string
        required: true
        unique: true
        description: "Unique measure record identifier"

      - name: member_id
        logicalType: string
        required: true
        description: "Member identifier"
        classification: "PHI"

      - name: measurement_year
        logicalType: integer
        required: true
        description: "HEDIS measurement year"

      - name: measure_code
        logicalType: string
        required: true
        description: "HEDIS measure code (e.g., CDC, CBP, BCS)"

      - name: measure_name
        logicalType: string
        required: true
        description: "Measure name (e.g., Comprehensive Diabetes Care)"

      - name: measure_category
        logicalType: string
        required: true
        description: "Category: effectiveness_of_care, access_availability, member_experience"

      - name: numerator_compliant
        logicalType: boolean
        required: true
        description: "Whether member met numerator criteria"

      - name: denominator_eligible
        logicalType: boolean
        required: true
        description: "Whether member is in denominator"

      - name: exclusion_applied
        logicalType: boolean
        required: true
        description: "Whether member was excluded"

      - name: exclusion_reason
        logicalType: string
        required: false
        description: "Reason for exclusion"

      - name: compliance_date
        logicalType: date
        required: false
        description: "Date numerator criteria met"

      - name: gap_status
        logicalType: string
        required: true
        description: "Status: compliant, gap, excluded, not_eligible"

      - name: gap_closure_date
        logicalType: date
        required: false
        description: "Expected gap closure date"

      - name: star_rating_impact
        logicalType: boolean
        required: true
        description: "Whether measure impacts Star Ratings"

      - name: provider_npi
        logicalType: string
        required: false
        description: "Attributed provider NPI"

      - name: calculated_at
        logicalType: timestamp
        required: true
        description: "When measure was calculated (UTC)"

      - name: created_at
        logicalType: timestamp
        required: true
        description: "Record creation timestamp (UTC)"

      - name: updated_at
        logicalType: timestamp
        required: true
        description: "Record last update timestamp (UTC)"
```

### Step 6: Create Data Products

Navigate to **Data Products** and create the following products:

#### 1. **Source Product: Claims Data Stream** (Source-Aligned)

- **Name**: `Claims Data Stream v1`
- **Version**: `1.0.0`
- **Domain**: `Claims & Operations`
- **Status**: `active`
- **Description**:
  - **Purpose**: Real-time claims data feed from EDI processing and adjudication systems
  - **Usage**: Source data for claims analytics, fraud detection, and reporting
  - **Limitations**: 15-minute lag from adjudication. Historical data available for 7 years.
- **Output Ports**:
  - **Name**: `claims_stream_delta`
  - **Type**: `table`
  - **Contract**: Select "Healthcare Claims Data Contract"
  - **Format**: `delta`
  - **Location**: `s3://healthcareplus-data/claims/stream/v1` (or Unity Catalog path)
  - **Contains PII**: Yes
  - **Tags**: `claims`, `source`, `real-time`
- **Team**: `claims-engineering`
- **Tags**: `source`, `claims`, `operational`
- **Support Channel**: `#claims-data-eng`

#### 2. **Aggregate Product: Member 360 View** (Aggregate)

- **Name**: `Member 360 View v1`
- **Version**: `1.0.0`
- **Domain**: `Member & Analytics`
- **Status**: `active`
- **Description**:
  - **Purpose**: Comprehensive member view integrating demographics, claims, clinical, and quality data
  - **Usage**: Member services, care coordination, analytics, and personalized engagement
  - **Limitations**: Updated daily at 3 AM EST. PHI restricted to authorized users only.
- **Input Ports**:
  - **Name**: `Claims Data`
  - **Contract**: Select "Healthcare Claims Data Contract"
  - **Name**: `Member Profile Data`
  - **Contract**: Select "Healthcare Member Data Contract"
  - **Name**: `Clinical Events`
  - **Contract**: Select "Healthcare Clinical Events Data Contract"
- **Output Ports**:
  - **Name**: `member_360_delta`
  - **Type**: `table`
  - **Format**: `delta`
  - **Location**: `s3://healthcareplus-data/member/360-view/v1`
  - **Contains PII**: Yes
  - **Tags**: `member`, `360-view`, `analytical`
- **Team**: `member-analytics`
- **Tags**: `aggregate`, `member`, `360-view`, `analytical`
- **Support Channel**: `#member-analytics`

#### 3. **Consumer-Aligned Product: High-Risk Member Predictions** (Consumer-Aligned)

- **Name**: `High-Risk Member Predictions v1`
- **Version**: `1.0.0`
- **Domain**: `Clinical`
- **Status**: `active`
- **Description**:
  - **Purpose**: ML predictions identifying members at high risk for hospitalization or readmission
  - **Usage**: Care management team uses scores to prioritize outreach and interventions
  - **Limitations**: Model updated weekly. Predictions based on 12-month lookback. Accuracy degrades for members with <6 months history.
- **Input Ports**:
  - **Name**: `Clinical Events`
  - **Contract**: Select "Healthcare Clinical Events Data Contract"
  - **Name**: `Member 360 Data`
  - **Contract**: (create or reference Member 360 contract)
- **Output Ports**:
  - **Name**: `risk_prediction_api`
  - **Type**: `api`
  - **Location**: `https://api.healthcareplus.com/care-mgmt/risk-scores/v1`
  - **Contains PII**: Yes
  - **Tags**: `api`, `predictions`, `risk`, `ml`
- **Management Ports**:
  - **Name**: `model-monitoring`
  - **Type**: `observability`
  - **URL**: `https://mlflow.healthcareplus.com/models/readmission-risk-v1`
  - **Description**: MLflow model monitoring and drift detection
- **Team**: `clinical-data-science`
- **Tags**: `consumer-aligned`, `ml`, `risk-prediction`, `care-management`
- **Support Channel**: `#clinical-ds`

### Step 7: Assign Roles and Permissions

Navigate to **Settings → RBAC** and verify the following role assignments:

1. **Admin** role → Your admin group
2. **Data Steward** role → `governance-compliance` team members
3. **Data Producer** role → `claims-engineering`, `clinical-data-science` teams
4. **Data Consumer** role → `member-analytics` team

### Step 8: Test the Demo Flow

#### As a Data Producer (Claims Engineering Team):
1. Navigate to **Data Products → Products**
2. Open "Healthcare Claims Data Contract"
3. View schema and quality checks
4. Navigate to **Data Products → Products**
5. Open "Claims Data Stream v1"
6. Review output ports and consumers

#### As a Data Consumer (Member Analytics Team):
1. Navigate to **Data Products → Products** (should see read-only view)
2. Browse "Member 360 View v1"
3. "Subscribe" to the product (track usage)
4. View dependencies and input contracts
5. Access associated data contracts

#### As a Data Steward (Governance Team):
1. Navigate to **Governance → Semantic Models**
2. Explore healthcare ontology concepts (read-only)
3. Search for clinical terms and view hierarchies
4. Navigate to **Data Products → Contracts**
5. Review compliance status
6. Navigate to **Operations → Compliance** (if enabled)
7. Check overall compliance scores

### Step 9: Optional - Create Data Asset Review Workflow

Navigate to **Data Asset Reviews** and create a review for a new data product:

1. **Asset**: Select "High-Risk Member Predictions v1"
2. **Review Type**: `New Product Launch`
3. **Requestor**: Your user (from `clinical-data-science` team)
4. **Reviewers**: Add users from `governance-compliance` team
5. **Priority**: `High`
6. **Description**: "Request approval to deploy high-risk member prediction model to production"
7. Submit the review

As a reviewer (governance team member):
1. Navigate to **Data Asset Reviews**
2. Open the pending review
3. Review the data product details
4. Add comments about HIPAA compliance requirements
5. Approve or request changes

### Step 10: Verify Search Functionality

1. Use the global search bar (top right)
2. Search for "claim" - should return:
   - Claims Data Contract
   - Claims Data Stream product
   - Any related semantic model concepts
3. Search for "member" - should return:
   - Member Data Contract
   - Member 360 View product
   - Any related semantic model concepts
4. Search for "quality" - should return:
   - Quality Measures contract
   - Any related semantic model concepts

## Demo Talking Points

### Data Mesh Architecture
- **Domain-Oriented**: Clinical, Claims/Operations, and Member/Analytics domains with clear ownership
- **Self-Serve Platform**: Teams use Ontos to publish and discover data products independently
- **Federated Governance**: Central glossary and standards, with team autonomy

### Healthcare-Specific Value
- **HIPAA Compliance**: PHI classification tracked in contracts, access controls via RBAC
- **Quality Measures**: HEDIS/Star Ratings data products for regulatory reporting
- **Interoperability**: Standard coding (ICD-10, CPT, NPI) enforced via contracts
- **Care Management**: High-risk predictions enable proactive member outreach

### Data Product Lifecycle
1. **Inception**: Clinical data science team identifies need for readmission predictions
2. **Design**: Create contracts with clinical team, define quality measures
3. **Creation**: Build ML pipeline using Member 360 and Clinical Events products
4. **Publishing**: Deploy via MLflow, register in Ontos with API endpoint
5. **Operation**: Monitor via MLflow, track usage, governance reviews compliance
6. **Consumption**: Care management team subscribes and uses API for member outreach

### Governance & Compliance
- **Semantic Models**: Healthcare ontology concepts for standardized terminology (read-only)
- **Data Contracts**: Schema validation, quality checks, PHI classification
- **RBAC**: Role-based access (Producer, Consumer, Steward, Admin)
- **Audit Trail**: Changes tracked, review workflows for sensitive data

## Troubleshooting

### Issue: Cannot create data contracts
- **Solution**: Verify you have `Data Producer` or `Admin` role assigned

### Issue: PHI data not showing proper classification
- **Solution**: Edit contract schema properties and add `classification: "PHI"` metadata

### Issue: Cannot find Business Glossaries feature
- **Solution**: Business Glossaries is not yet implemented in the UI. Use **Governance → Semantic Models** to explore ontology concepts. Custom business glossary creation will be available in a future release.

### Issue: Data products not linking to contracts
- **Solution**: Ensure contract IDs match exactly between contracts and product input/output ports

## Unity Catalog Integration

### Overview

Ontos integrates with Unity Catalog through **governed tags** that connect metadata to actual UC tables. This enables true E2E data governance:

- **Data Contracts** → Define schema standards
- **Physical Tables** → Reference UC tables via `physicalName`
- **Output Ports** → Link products to UC tables via `assetIdentifier`
- **UC Tag Sync Job** → Applies tags automatically to UC assets

See **[UC_INTEGRATION.md](UC_INTEGRATION.md)** for complete integration details.

### Demo Setup with Actual UC Tables

#### Step 1: Create Unity Catalog Structure

```sql
-- Run in Databricks SQL or notebook
CREATE CATALOG IF NOT EXISTS healthcare_payor;

CREATE SCHEMA IF NOT EXISTS healthcare_payor.claims;
CREATE SCHEMA IF NOT EXISTS healthcare_payor.members;
CREATE SCHEMA IF NOT EXISTS healthcare_payor.providers;
CREATE SCHEMA IF NOT EXISTS healthcare_payor.clinical;
CREATE SCHEMA IF NOT EXISTS healthcare_payor.quality;
CREATE SCHEMA IF NOT EXISTS healthcare_payor.analytics;

-- Grant permissions
GRANT USE CATALOG ON CATALOG healthcare_payor TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.claims TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthcare_payor.members TO `account users`;
-- ... (grant for all schemas)
```

#### Step 2: Run Automated Setup Scripts

Use the automated setup scripts described in the **"Quick Setup (Automated)"** section above:

```bash
cd demo
pip install -r requirements.txt
python setup_workspace.py --config settings.yaml --all
```

This will create all Unity Catalog tables with synthetic data:

1. **`healthcare_payor.claims.adjudicated_claims`** (100K rows)
2. **`healthcare_payor.members.member_profiles`** (50K rows)
3. **`healthcare_payor.providers.provider_directory`** (5K providers)
4. **`healthcare_payor.clinical.member_clinical_events`** (500K events)
5. **`healthcare_payor.quality.hedis_measures`** (50K measures)
6. **`healthcare_payor.analytics.member_360_view`** (Member 360 aggregate)

**Execution Time**: ~10-15 minutes total

See **"Quick Setup (Automated)"** section above for detailed instructions and configuration options.

#### Step 3: Update Data Contracts with Physical Names

After tables are created, update your Data Contracts:

**Claims Contract:**
```yaml
schema:
  - name: claims
    physicalName: "healthcare_payor.claims.adjudicated_claims"  # ← UC table FQN
    properties:
      - name: claim_id
        logicalType: string
        ...
```

**Members Contract:**
```yaml
schema:
  - name: members
    physicalName: "healthcare_payor.members.member_profiles"  # ← UC table FQN
    properties:
      - name: member_id
        logicalType: string
        ...
```

Repeat for all 5 contracts.

#### Step 4: Update Data Product Output Ports

**Claims Data Stream Product:**
```typescript
{
  "outputPorts": [{
    "name": "claims_stream_delta",
    "assetIdentifier": "healthcare_payor.claims.adjudicated_claims",  // ← UC table
    "format": "delta",
    "containsPII": true
  }]
}
```

**Member 360 View Product:**
```typescript
{
  "inputPorts": [
    { "contract": "Healthcare Claims Data Contract" },
    { "contract": "Healthcare Member Data Contract" }
  ],
  "outputPorts": [{
    "name": "member_360_delta",
    "assetIdentifier": "healthcare_payor.analytics.member_360_view",  // ← UC table
    "format": "delta"
  }]
}
```

#### Step 5: Configure and Run UC Tag Sync Job

1. Navigate to **Settings → Jobs**
2. Find "UC Tag Sync" job
3. Configure tag sync settings (if needed):
   ```yaml
   tag_sync_configs:
     - entity_type: "data_product"
       enabled: true
       tag_key_format: "x_ontos_product_{PRODUCT.NAME}"
       tag_value_format: "{PRODUCT.VERSION}"
   ```
4. Click "Run Job"
5. Monitor job progress in Databricks Workflows

#### Step 6: Verify Tags in Unity Catalog

```sql
-- Check tags on claims table
SHOW TAGS ON TABLE healthcare_payor.claims.adjudicated_claims;

-- Expected output:
-- x_ontos_product_Claims_Data_Stream_v1 = 1.0.0
-- x_ontos_contract_Healthcare_Claims_Data_Contract = 1.0.0
-- x_ontos_domain = Claims & Operations

-- Query all tagged tables
SELECT table_catalog, table_schema, table_name, tag_name, tag_value
FROM system.information_schema.table_tags
WHERE table_catalog = 'healthcare_payor'
  AND tag_name LIKE 'x_ontos_%'
ORDER BY table_name, tag_name;
```

#### Step 7: Test E2E Integration

1. **In Databricks SQL**: Query tagged table
   ```sql
   SELECT * FROM healthcare_payor.claims.adjudicated_claims LIMIT 10;
   ```

2. **In Ontos**: Search for "claims" → Find Data Contract and Product linked to UC table

3. **In Unity Catalog UI**: Browse catalog → View table tags → See Ontos metadata

4. **Bi-directional discovery**: UC → Ontos and Ontos → UC

### Tag Sync Architecture

```
Ontos (Metadata) → UC Tag Sync Job → Unity Catalog (Governed Tags) → UC Tables
     ↑                                                                    ↓
     └────────────── Search & Discovery ←───────────────────────────────┘
```

**Tags Applied:**
- Product tags: `x_ontos_product_{PRODUCT.NAME}` = `{VERSION}`
- Contract tags: `x_ontos_contract_{CONTRACT.NAME}` = `{VERSION}`
- Domain tags: `x_ontos_domain` = `{DOMAIN.NAME}`
- Semantic tags: `x_ontos_semantic_{CONCEPT}` = `{IRI}`

## Data Quality Checks Walkthrough

This section demonstrates how to define, configure, and execute data quality checks on your data products using Ontos.

### Overview: Data Quality Framework

Ontos implements the **ODCS (Open Data Contract Standard)** quality framework with support for:

- **Quality Dimensions**: accuracy, completeness, conformity, consistency, coverage, timeliness, uniqueness
- **Check Types**: library (predefined rules), SQL (custom queries), text, custom (external engines)
- **Severity Levels**: info, warning, error
- **Business Impact**: operational, regulatory
- **Automated Execution**: Scheduled Databricks workflows
- **Compliance Integration**: Quality scores feed into compliance monitoring

### Step-by-Step: Adding Quality Checks to a Data Contract

#### 1. Define Quality Checks in Your Contract

Navigate to **Data Contracts** and edit the "Healthcare Claims Data Contract". Add quality checks to schema properties:

**Example: Claims Contract with Quality Checks**

```yaml
schema:
  - name: claims
    physicalName: "healthcare_payor.claims.adjudicated_claims"
    properties:
      # Required field check
      - name: claim_id
        logicalType: string
        required: true  # ← Generates completeness check
        unique: true    # ← Generates uniqueness check
        description: "Unique claim identifier"

      # Numeric range check
      - name: billed_amount
        logicalType: decimal
        required: true
        minimum: 0      # ← Generates range check (must be >= 0)
        description: "Total amount billed (must be non-negative)"

      # String length and pattern check
      - name: provider_npi
        logicalType: string
        required: true
        pattern: "^[0-9]{10}$"  # ← Generates regex pattern check
        minLength: 10           # ← Generates length check
        maxLength: 10
        description: "10-digit National Provider Identifier"

      # Enum/categorical check
      - name: claim_status
        logicalType: string
        required: true
        enum: ["submitted", "pending", "approved", "denied", "adjusted"]
        description: "Valid claim statuses only"

      # Date range check
      - name: service_date_from
        logicalType: date
        required: true
        minimum: "2020-01-01"  # ← Historical data cutoff
        maximum: "2025-12-31"  # ← Future date limit
        description: "Service start date"
```

#### 2. Add Custom Quality Rules

For more advanced checks, add explicit quality rules to your contract:

```yaml
schema:
  - name: claims
    physicalName: "healthcare_payor.claims.adjudicated_claims"
    quality_checks:
      # Table-level check (object level)
      - name: "No Future Service Dates"
        level: "object"
        description: "Service dates cannot be in the future"
        dimension: "accuracy"
        business_impact: "operational"
        severity: "error"
        type: "sql"
        query: |
          SELECT COUNT(*) as violations
          FROM healthcare_payor.claims.adjudicated_claims
          WHERE service_date_from > CURRENT_DATE()
        must_be: "0"  # Violation count must be 0

      # Referential integrity check
      - name: "Valid Member References"
        level: "object"
        description: "All member_ids must exist in members table"
        dimension: "consistency"
        business_impact: "operational"
        severity: "error"
        type: "sql"
        query: |
          SELECT COUNT(*) as orphaned_claims
          FROM healthcare_payor.claims.adjudicated_claims c
          LEFT JOIN healthcare_payor.members.member_profiles m
            ON c.member_id = m.member_id
          WHERE m.member_id IS NULL
        must_be: "0"

      # Data freshness check
      - name: "Claims Data Freshness"
        level: "object"
        description: "Claims data should be updated within last 24 hours"
        dimension: "timeliness"
        business_impact: "operational"
        severity: "warning"
        type: "sql"
        query: |
          SELECT MAX(updated_at) as last_update
          FROM healthcare_payor.claims.adjudicated_claims
        must_be_gt: "CURRENT_TIMESTAMP() - INTERVAL 24 HOURS"

      # Statistical check
      - name: "Billed Amount Distribution"
        level: "property"
        property_name: "billed_amount"
        description: "Average billed amount should be realistic"
        dimension: "accuracy"
        severity: "warning"
        type: "sql"
        query: |
          SELECT AVG(billed_amount) as avg_billed
          FROM healthcare_payor.claims.adjudicated_claims
        must_be_ge: "100"   # At least $100 average
        must_be_le: "5000"  # At most $5000 average

    properties:
      # ... (schema properties)
```

#### 3. Configure Quality Checks in the UI

Alternatively, use the Ontos UI to add quality checks:

1. Navigate to **Data Contracts**
2. Open "Healthcare Claims Data Contract"
3. Scroll to the schema object (table)
4. Click **"Add Quality Check"**
5. Fill in the quality check form:
   - **Name**: "No Negative Billed Amounts"
   - **Level**: Property
   - **Property**: billed_amount
   - **Dimension**: Accuracy
   - **Business Impact**: Operational
   - **Severity**: Error
   - **Type**: SQL
   - **Query**:
     ```sql
     SELECT COUNT(*) as violations
     FROM healthcare_payor.claims.adjudicated_claims
     WHERE billed_amount < 0
     ```
   - **Must Be**: 0
6. Click **"Save"**

#### 4. Enable and Schedule Quality Check Workflow

1. Navigate to **Settings → Jobs**
2. Find **"Data Quality Checks"** workflow
3. Click **"Configure"**
4. Set schedule:
   ```yaml
   schedule:
     quartz_cron_expression: "0 0 2 * * ?"  # Daily at 2 AM UTC
     pause_status: "UNPAUSED"
   ```
5. Configure parameters:
   - **catalog**: `healthcare_payor`
   - **schema**: `claims,members,clinical,quality`
   - **contract_statuses**: `["active", "certified"]`
   - **verbose**: `false`
6. Click **"Save & Run Now"** to test

#### 5. Monitor Quality Check Results

After the workflow completes:

1. Navigate to **Data Contracts**
2. Open "Healthcare Claims Data Contract"
3. Scroll to **"Quality Check Results"** section
4. View the latest run:
   - **Status**: Succeeded / Failed
   - **Score**: 94.5% (checks_passed / total_checks * 100)
   - **Checks Passed**: 17 / 18
   - **Checks Failed**: 1
   - **Violations**: Summary of failures

5. Click on a failed check to see details:
   - **Check Name**: "No Future Service Dates"
   - **Violations Count**: 487
   - **Message**: "Found 487 claims with future service dates"
   - **Violation Examples**: (sample of violating records)

### Understanding Injected Quality Issues

The demo setup scripts (`demo/setup_workspace.py`) intentionally inject quality issues to demonstrate the checks. Configuration in `demo/settings.yaml`:

```yaml
data_generation:
  quality_issues:
    enabled: true
    missing_values: 0.02        # 2% of nullable fields will be null
    invalid_codes: 0.01         # 1% invalid ICD-10/CPT codes
    orphaned_references: 0.005  # 0.5% member_id references don't exist
    duplicate_records: 0.01     # 1% duplicate claim_ids
    future_dates: 0.005         # 0.5% future service_date_from
    negative_amounts: 0.01      # 1% negative billed_amount
    outlier_amounts: 0.03       # 3% extreme amounts (>$100k)
```

**Expected Quality Issues in Demo Data:**

| Quality Issue | Type | Count (approx) | Check That Catches It |
|---------------|------|----------------|-----------------------|
| Missing processed_date | Completeness | 2,000 | Required field check |
| Invalid ICD-10 codes | Conformity | 1,000 | Pattern/enum check |
| Orphaned member_ids | Consistency | 500 | Referential integrity check |
| Duplicate claim_ids | Uniqueness | 1,000 | Unique constraint check |
| Future service dates | Accuracy | 500 | Date range check |
| Negative billed amounts | Accuracy | 1,000 | Numeric range check |
| Outlier amounts (>$100k) | Accuracy | 3,000 | Statistical outlier check |

### Demonstrating the Quality Check Workflow

**Scenario**: Show how quality checks detect and report issues in the claims data.

#### Step 1: Run Initial Quality Check

```bash
# Trigger quality check workflow via Databricks API or UI
# Or wait for scheduled run (2 AM UTC daily)
```

#### Step 2: Review Results in Ontos UI

1. Navigate to **Data Contracts → Healthcare Claims Data Contract**
2. View quality score: **92.3%** (13 passed / 14 total)
3. Expand failed checks:
   - ✓ Required Fields: **PASSED** (98% complete, threshold: 95%)
   - ✓ Unique Claim IDs: **PASSED** (99% unique, threshold: 99%)
   - ✗ **No Future Dates**: FAILED (487 violations)
   - ✓ Valid Member References: **PASSED** (99.5% valid, threshold: 99%)
   - ✓ Non-Negative Amounts: **PASSED** (99% valid)
   - ... (more checks)

#### Step 3: Investigate Violations

Click on "No Future Dates" failed check:

```
Check: No Future Service Dates
Status: FAILED
Violations: 487 claims
Query Result: 487
Expected: 0
Severity: error
Business Impact: operational

Sample Violations:
- claim_id: CLM-1234567890, service_date_from: 2026-03-15 (82 days in future)
- claim_id: CLM-9876543210, service_date_from: 2026-01-10 (15 days in future)
... (showing 10 of 487)

Recommended Action:
Investigate EDI processing pipeline for timestamp errors. Contact claims-engineering team.
```

#### Step 4: Fix Quality Issues

**Option A**: Clean the data in Unity Catalog

```sql
-- Fix future dates (set to current date)
UPDATE healthcare_payor.claims.adjudicated_claims
SET service_date_from = CURRENT_DATE()
WHERE service_date_from > CURRENT_DATE();
```

**Option B**: Update quality check threshold (if intentional)

Edit the contract to adjust the threshold:
```yaml
quality_checks:
  - name: "No Future Service Dates"
    must_be_le: "500"  # Allow up to 500 violations temporarily
```

#### Step 5: Re-run Quality Checks

1. Navigate to **Settings → Jobs → Data Quality Checks**
2. Click **"Run Now"**
3. Monitor job execution in Databricks Workflows
4. Return to Data Contract to see updated score

#### Step 6: View Historical Trends

1. Navigate to **Data Contracts → Healthcare Claims Data Contract**
2. Click **"Quality History"** tab
3. View score trends over time:
   - Jan 5: 92.3% (487 future date violations)
   - Jan 4: 94.1% (325 future date violations)
   - Jan 3: 96.2% (180 future date violations)
4. Identify patterns (e.g., weekend data loads have more issues)

### Integration with Compliance

Quality check scores automatically feed into compliance monitoring:

1. Navigate to **Compliance** (if enabled)
2. View **"Data Contract Compliance"** dashboard
3. See aggregate scores:
   - Claims Contract: 92.3% (below 95% threshold) → **Non-Compliant**
   - Members Contract: 98.7% → **Compliant**
   - Providers Contract: 99.1% → **Compliant**
4. Drill down to see quality check details contributing to compliance score

### Setting Up Notifications for Quality Failures

Configure notifications to alert teams when quality checks fail:

1. Navigate to **Settings → Notifications**
2. Create notification rule:
   - **Event**: Data Quality Check Failed
   - **Condition**: Severity = "error" AND Score < 95%
   - **Recipients**: claims-engineering team, governance-compliance team
   - **Channel**: Slack (#claims-data-quality) and Email
   - **Message Template**:
     ```
     ⚠️ Data Quality Alert

     Contract: {contract_name}
     Score: {quality_score}% (threshold: 95%)
     Failed Checks: {failed_checks_count}

     Top Violations:
     {violations_summary}

     View Details: {contract_url}
     ```
3. Save and enable

### Quality Check Best Practices

**1. Start with Schema-Based Checks**
   - Use `required`, `unique`, `minimum`, `maximum`, `pattern` in schema properties
   - These auto-generate quality checks without custom SQL

**2. Add Custom SQL for Business Logic**
   - Referential integrity (foreign key constraints)
   - Cross-table consistency
   - Statistical bounds (e.g., 99th percentile thresholds)

**3. Use Appropriate Severity Levels**
   - **Error**: Data is unusable (e.g., null PKs, orphaned FKs)
   - **Warning**: Data quality degraded but usable (e.g., missing optional fields)
   - **Info**: Informational metrics (e.g., record counts)

**4. Set Realistic Thresholds**
   - Don't require 100% perfection for all checks
   - Allow small error rates (e.g., 99% threshold for some checks)
   - Adjust thresholds based on upstream data quality

**5. Schedule Checks Appropriately**
   - Run after data load jobs complete
   - Daily for production tables
   - Hourly for real-time streams (if using streaming)

**6. Monitor Trends, Not Just Point Values**
   - Track quality scores over time
   - Alert on significant degradations (e.g., >5% drop)
   - Investigate sudden changes

**7. Integrate with Data Pipelines**
   - Use quality scores as pipeline gates
   - Fail data product publishing if quality < threshold
   - Automatically create JIRA tickets for failures

### Example: End-to-End Quality Workflow

**Scenario**: Claims engineering team publishes a new version of the claims data product.

1. **Developer** updates claims ETL pipeline
2. **Pipeline** writes data to `healthcare_payor.claims.adjudicated_claims`
3. **Quality Check Workflow** runs automatically (triggered by table update)
4. **Ontos** executes all quality checks defined in contract
5. **Results**:
   - Score: 91.2% (below 95% threshold)
   - Failed checks: 3
6. **Notification** sent to #claims-data-quality Slack channel
7. **Claims Engineer** investigates failures:
   - 1,200 claims with future service dates (pipeline bug identified)
   - 800 orphaned member_ids (upstream member data delayed)
8. **Engineer** fixes pipeline bug, re-runs ETL
9. **Quality Check** re-runs, score improves to 97.8%
10. **Data Product** status updated to "active" (quality gate passed)
11. **Consumers** notified that new version is available

This workflow ensures data products maintain high quality standards before reaching consumers.

## Next Steps

After completing the demo setup:

1. **Add More Contracts**: Pharmacy claims, provider performance, member engagement
2. **Create Advanced Products**: Cost forecasting, network adequacy analysis, member churn prediction
3. **Set Up Compliance Rules**: Define rules for PHI access, data retention, quality thresholds
4. **Integrate with CI/CD**: Use Git sync to version control contracts
5. **Enable Notifications**: Configure Slack/email notifications for review workflows
6. **Add Master Data Management**: Use Zingg.ai integration for member/provider matching
7. **Explore Semantic Models**: Load healthcare ontologies (SNOMED CT, RxNorm, LOINC) into Semantic Models for standardized terminology
8. **Unity Catalog Lineage**: Explore how Ontos product lineage complements UC table lineage

## Resources

- **HIPAA Compliance**: https://www.hhs.gov/hipaa
- **HEDIS Measures**: https://www.ncqa.org/hedis
- **ICD-10 Codes**: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
- **CPT Codes**: https://www.ama-assn.org/practice-management/cpt
- **FHIR Interoperability**: https://www.hl7.org/fhir/
- **CMS Risk Adjustment**: https://www.cms.gov/medicare/health-plans/medicareadvtgspecratestats/risk-adjustors

---

**Demo Version**: 1.0.0
**Last Updated**: December 2025
**Maintained By**: HealthCare Plus Data Governance Team
