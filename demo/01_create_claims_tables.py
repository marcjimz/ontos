# Databricks notebook source
# MAGIC %md
# MAGIC # Create Healthcare Claims Tables
# MAGIC
# MAGIC This notebook creates synthetic claims data for the healthcare payor demo.
# MAGIC
# MAGIC **Tables Created:**
# MAGIC - `healthcare_payor.claims.adjudicated_claims` - Adjudicated professional and institutional claims
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog enabled
# MAGIC - `healthcare_payor` catalog and `claims` schema created
# MAGIC - Permissions to create tables

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Configuration
CATALOG = "healthcare_payor"
SCHEMA = "claims"
NUM_CLAIMS = 100_000  # Number of claims to generate
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

print(f"Generating {NUM_CLAIMS:,} claims from {START_DATE} to {END_DATE}")
print(f"Target: {CATALOG}.{SCHEMA}.adjudicated_claims")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

%pip install faker --quiet
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

spark = SparkSession.builder.appName("CreateClaimsTables").getOrCreate()
fake = Faker()
Faker.seed(42)
random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Synthetic Data Generators

# COMMAND ----------

# Healthcare code lists
CLAIM_TYPES = ["professional", "institutional", "dental", "pharmacy"]
CLAIM_STATUSES = ["submitted", "pending", "approved", "denied", "adjusted"]
NETWORK_STATUSES = ["in_network", "out_of_network", "preferred"]
PLACE_OF_SERVICE_CODES = {
    "11": "Office",
    "21": "Inpatient Hospital",
    "22": "Outpatient Hospital",
    "23": "Emergency Room",
    "31": "Skilled Nursing Facility",
    "81": "Independent Laboratory"
}

# Common ICD-10 diagnosis codes
ICD10_CODES = [
    "E11.9",   # Type 2 Diabetes
    "I10",     # Essential Hypertension
    "J44.9",   # COPD
    "I25.10",  # Coronary Artery Disease
    "M79.3",   # Myalgia
    "J06.9",   # Upper Respiratory Infection
    "K21.9",   # GERD
    "E78.5",   # Hyperlipidemia
    "M25.50",  # Joint Pain
    "R51",     # Headache
    "F41.9",   # Anxiety
    "I50.9",   # Heart Failure
    "N18.3",   # Chronic Kidney Disease Stage 3
    "E66.9",   # Obesity
    "F33.1"    # Major Depressive Disorder
]

# Common CPT procedure codes
CPT_CODES = [
    "99213",   # Office visit, established patient
    "99214",   # Office visit, detailed
    "80053",   # Comprehensive metabolic panel
    "85025",   # Complete blood count
    "93000",   # EKG
    "36415",   # Blood draw
    "99285",   # Emergency department visit
    "99223",   # Initial hospital care
    "71045",   # Chest x-ray
    "73610",   # Ankle x-ray
    "J3490",   # Unclassified drug
    "G0008",   # Admin of influenza vaccine
    "99203",   # New patient office visit
    "45378",   # Colonoscopy
    "76856"    # Ultrasound, pelvic
]

DENIAL_REASON_CODES = [
    None,           # Not denied
    "DUPLICATE",    # Duplicate claim
    "NOTCOVERED",   # Service not covered
    "AUTH",         # Prior auth required
    "TIMELY",       # Not submitted timely
    "CODING",       # Coding error
]

# COMMAND ----------

def generate_member_id():
    """Generate a synthetic member ID"""
    return f"MBR-{random.randint(100000, 999999)}"

def generate_claim_number():
    """Generate a claim number"""
    return f"CLM-{random.randint(10000000, 99999999)}"

def generate_npi():
    """Generate a 10-digit NPI"""
    return str(random.randint(1000000000, 9999999999))

def random_date_between(start_date_str, end_date_str):
    """Generate random date between two dates"""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate_claim():
    """Generate a single synthetic claim record"""
    service_date_from = random_date_between(START_DATE, END_DATE)
    service_date_to = service_date_from + timedelta(days=random.randint(0, 7))
    received_date = service_date_to + timedelta(days=random.randint(1, 30))

    claim_status = random.choices(
        CLAIM_STATUSES,
        weights=[5, 10, 70, 10, 5]  # Most claims are approved
    )[0]

    processed_date = None
    paid_date = None
    if claim_status in ["approved", "denied", "adjusted"]:
        processed_date = received_date + timedelta(days=random.randint(1, 15))
        if claim_status == "approved":
            paid_date = processed_date + timedelta(days=random.randint(1, 7))

    network_status = random.choices(
        NETWORK_STATUSES,
        weights=[80, 15, 5]  # 80% in-network
    )[0]

    # Generate amounts
    if network_status == "in_network":
        billed_amount = round(random.uniform(50, 5000), 2)
        allowed_amount = round(billed_amount * random.uniform(0.4, 0.8), 2)
    else:
        billed_amount = round(random.uniform(50, 5000), 2)
        allowed_amount = round(billed_amount * random.uniform(0.6, 0.9), 2)

    if claim_status == "approved":
        paid_amount = allowed_amount
        member_responsibility = round(allowed_amount * random.uniform(0.1, 0.3), 2)
    elif claim_status == "denied":
        paid_amount = 0.0
        member_responsibility = 0.0
    else:
        paid_amount = None
        member_responsibility = None

    denial_reason = None
    if claim_status == "denied":
        denial_reason = random.choice([d for d in DENIAL_REASON_CODES if d is not None])

    # Pick diagnosis and procedure codes
    num_diagnoses = random.randint(1, 3)
    diagnosis_codes = random.sample(ICD10_CODES, num_diagnoses)

    num_procedures = random.randint(1, 2)
    procedure_codes = random.sample(CPT_CODES, num_procedures)

    place_of_service = random.choice(list(PLACE_OF_SERVICE_CODES.keys()))

    return {
        "claim_id": str(uuid.uuid4()),
        "claim_number": generate_claim_number(),
        "claim_type": random.choice(CLAIM_TYPES),
        "member_id": generate_member_id(),
        "provider_npi": generate_npi(),
        "service_date_from": service_date_from.strftime("%Y-%m-%d"),
        "service_date_to": service_date_to.strftime("%Y-%m-%d"),
        "received_date": received_date.strftime("%Y-%m-%d"),
        "processed_date": processed_date.strftime("%Y-%m-%d") if processed_date else None,
        "paid_date": paid_date.strftime("%Y-%m-%d") if paid_date else None,
        "claim_status": claim_status,
        "diagnosis_codes": diagnosis_codes,
        "procedure_codes": procedure_codes,
        "billed_amount": float(billed_amount),
        "allowed_amount": float(allowed_amount),
        "paid_amount": float(paid_amount) if paid_amount is not None else None,
        "member_responsibility": float(member_responsibility) if member_responsibility is not None else None,
        "network_status": network_status,
        "place_of_service": place_of_service,
        "denial_reason_code": denial_reason,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Claims Data

# COMMAND ----------

print(f"Generating {NUM_CLAIMS:,} claim records...")

# Generate claims in batches for better memory management
BATCH_SIZE = 10_000
num_batches = (NUM_CLAIMS + BATCH_SIZE - 1) // BATCH_SIZE

all_claims = []
for batch in range(num_batches):
    batch_size = min(BATCH_SIZE, NUM_CLAIMS - batch * BATCH_SIZE)
    batch_claims = [generate_claim() for _ in range(batch_size)]
    all_claims.extend(batch_claims)
    print(f"  Generated batch {batch + 1}/{num_batches} ({len(all_claims):,} total)")

print(f"✓ Generated {len(all_claims):,} claims")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create DataFrame

# COMMAND ----------

# Define schema
claims_schema = StructType([
    StructField("claim_id", StringType(), False),
    StructField("claim_number", StringType(), False),
    StructField("claim_type", StringType(), False),
    StructField("member_id", StringType(), False),
    StructField("provider_npi", StringType(), False),
    StructField("service_date_from", DateType(), False),
    StructField("service_date_to", DateType(), False),
    StructField("received_date", DateType(), False),
    StructField("processed_date", DateType(), True),
    StructField("paid_date", DateType(), True),
    StructField("claim_status", StringType(), False),
    StructField("diagnosis_codes", ArrayType(StringType()), False),
    StructField("procedure_codes", ArrayType(StringType()), False),
    StructField("billed_amount", DoubleType(), False),
    StructField("allowed_amount", DoubleType(), False),
    StructField("paid_amount", DoubleType(), True),
    StructField("member_responsibility", DoubleType(), True),
    StructField("network_status", StringType(), False),
    StructField("place_of_service", StringType(), False),
    StructField("denial_reason_code", StringType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), False)
])

# Create DataFrame
claims_df = spark.createDataFrame(all_claims, schema=claims_schema)

print(f"✓ Created DataFrame with {claims_df.count():,} rows")
claims_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save to Unity Catalog

# COMMAND ----------

table_name = f"{CATALOG}.{SCHEMA}.adjudicated_claims"

print(f"Writing to {table_name}...")

claims_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

print(f"✓ Successfully created table: {table_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Table

# COMMAND ----------

# Verify table
print(f"Verifying table: {table_name}")
print(f"Row count: {spark.table(table_name).count():,}")

print("\nSample data:")
display(spark.table(table_name).limit(10))

print("\nClaim status distribution:")
display(
    spark.table(table_name)
    .groupBy("claim_status")
    .count()
    .orderBy(col("count").desc())
)

print("\nNetwork status distribution:")
display(
    spark.table(table_name)
    .groupBy("network_status")
    .count()
    .orderBy(col("count").desc())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Table Comment

# COMMAND ----------

spark.sql(f"""
COMMENT ON TABLE {table_name} IS
'Adjudicated healthcare claims including professional, institutional, dental, and pharmacy claims.
Contains claim details, diagnosis/procedure codes, financial amounts, and adjudication status.
Generated for Ontos healthcare payor demo.'
""")

print(f"✓ Added table comment")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 80)
print("CLAIMS TABLE CREATION COMPLETE")
print("=" * 80)
print(f"Table: {table_name}")
print(f"Rows: {claims_df.count():,}")
print(f"Date Range: {START_DATE} to {END_DATE}")
print()
print("Next Steps:")
print("1. Update Ontos Data Contract 'Healthcare Claims Data Contract'")
print(f"   - Set physicalName: '{table_name}'")
print("2. Update Ontos Data Product 'Claims Data Stream v1'")
print(f"   - Set output port assetIdentifier: '{table_name}'")
print("3. Run UC Tag Sync job in Ontos")
print("4. Verify tags:")
print(f"   SHOW TAGS ON TABLE {table_name};")
print("=" * 80)
