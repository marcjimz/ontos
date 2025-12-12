# Databricks notebook source
# MAGIC %md
# MAGIC # Create Healthcare Member Tables
# MAGIC
# MAGIC This notebook creates synthetic member/subscriber data for the healthcare payor demo.
# MAGIC
# MAGIC **Tables Created:**
# MAGIC - `healthcare_payor.members.member_profiles` - Member demographics, enrollment, and risk scores
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog enabled
# MAGIC - `healthcare_payor` catalog and `members` schema created
# MAGIC - Permissions to create tables

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Configuration
CATALOG = "healthcare_payor"
SCHEMA = "members"
NUM_MEMBERS = 50_000  # Number of members to generate
ENROLLMENT_START = "2020-01-01"
ENROLLMENT_END = "2024-12-31"

print(f"Generating {NUM_MEMBERS:,} members with enrollments from {ENROLLMENT_START} to {ENROLLMENT_END}")
print(f"Target: {CATALOG}.{SCHEMA}.member_profiles")

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

spark = SparkSession.builder.appName("CreateMemberTables").getOrCreate()
fake = Faker()
Faker.seed(42)
random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Synthetic Data Generators

# COMMAND ----------

# Member configuration
PLAN_IDS = ["HMO-001", "PPO-001", "EPO-001", "POS-001", "HDHP-001"]
MEMBER_STATUSES = ["active", "inactive", "terminated"]
GENDERS = ["M", "F", "X", "U"]
US_STATES = [
    "CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
    "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"
]

# COMMAND ----------

def generate_member_id():
    """Generate a synthetic member ID"""
    return f"MBR-{random.randint(100000, 999999)}"

def generate_npi():
    """Generate a 10-digit NPI for PCP"""
    return str(random.randint(1000000000, 9999999999))

def random_date_between(start_date_str, end_date_str):
    """Generate random date between two dates"""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate_date_of_birth():
    """Generate DOB with realistic age distribution"""
    # Age distribution: 20% under 18, 50% 18-64, 30% 65+
    age_group = random.choices(["child", "adult", "senior"], weights=[20, 50, 30])[0]

    if age_group == "child":
        years_ago = random.randint(0, 17)
    elif age_group == "adult":
        years_ago = random.randint(18, 64)
    else:  # senior
        years_ago = random.randint(65, 90)

    dob = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 364))
    return dob.strftime("%Y-%m-%d")

def generate_risk_score():
    """Generate HCC Risk Adjustment Factor (RAF) score"""
    # Distribution: mean ~1.0, range 0.5-3.0
    return round(random.triangular(0.5, 3.0, 1.0), 2)

def generate_phone():
    """Generate US phone number in E.164 format"""
    area_code = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(0, 9999)
    return f"+1{area_code}{exchange:03d}{number:04d}"

def generate_zip():
    """Generate 5-digit ZIP code"""
    return f"{random.randint(10000, 99999)}"

def generate_member():
    """Generate a single synthetic member record"""
    member_id = generate_member_id()

    # Determine if primary subscriber or dependent
    is_subscriber = random.random() < 0.7  # 70% subscribers
    subscriber_id = member_id if is_subscriber else generate_member_id()

    # Generate enrollment dates
    enrollment_date = random_date_between(ENROLLMENT_START, ENROLLMENT_END)

    # Determine if active or terminated
    member_status = random.choices(
        MEMBER_STATUSES,
        weights=[85, 5, 10]  # 85% active
    )[0]

    termination_date = None
    if member_status == "terminated":
        # Termination 30-365 days after enrollment
        term_days = random.randint(30, 365)
        termination_date = (enrollment_date + timedelta(days=term_days)).strftime("%Y-%m-%d")

    # Generate demographics
    gender = random.choice(GENDERS)
    state = random.choice(US_STATES)

    # PCP assignment (90% have PCP)
    pcp_npi = generate_npi() if random.random() < 0.9 else None

    # Risk score
    risk_score = generate_risk_score()

    return {
        "member_id": member_id,
        "subscriber_id": subscriber_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": generate_date_of_birth(),
        "gender": gender,
        "email": fake.email() if random.random() < 0.8 else None,  # 80% have email
        "phone_number": generate_phone() if random.random() < 0.9 else None,  # 90% have phone
        "address_line1": fake.street_address(),
        "address_line2": fake.secondary_address() if random.random() < 0.3 else None,
        "city": fake.city(),
        "state": state,
        "zip_code": generate_zip(),
        "plan_id": random.choice(PLAN_IDS),
        "enrollment_date": enrollment_date.strftime("%Y-%m-%d"),
        "termination_date": termination_date,
        "member_status": member_status,
        "primary_care_provider_npi": pcp_npi,
        "risk_score": risk_score,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Member Data

# COMMAND ----------

print(f"Generating {NUM_MEMBERS:,} member records...")

# Generate members in batches
BATCH_SIZE = 10_000
num_batches = (NUM_MEMBERS + BATCH_SIZE - 1) // BATCH_SIZE

all_members = []
for batch in range(num_batches):
    batch_size = min(BATCH_SIZE, NUM_MEMBERS - batch * BATCH_SIZE)
    batch_members = [generate_member() for _ in range(batch_size)]
    all_members.extend(batch_members)
    print(f"  Generated batch {batch + 1}/{num_batches} ({len(all_members):,} total)")

print(f"✓ Generated {len(all_members):,} members")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create DataFrame

# COMMAND ----------

# Define schema
members_schema = StructType([
    StructField("member_id", StringType(), False),
    StructField("subscriber_id", StringType(), False),
    StructField("first_name", StringType(), False),
    StructField("last_name", StringType(), False),
    StructField("date_of_birth", DateType(), False),
    StructField("gender", StringType(), False),
    StructField("email", StringType(), True),
    StructField("phone_number", StringType(), True),
    StructField("address_line1", StringType(), False),
    StructField("address_line2", StringType(), True),
    StructField("city", StringType(), False),
    StructField("state", StringType(), False),
    StructField("zip_code", StringType(), False),
    StructField("plan_id", StringType(), False),
    StructField("enrollment_date", DateType(), False),
    StructField("termination_date", DateType(), True),
    StructField("member_status", StringType(), False),
    StructField("primary_care_provider_npi", StringType(), True),
    StructField("risk_score", DoubleType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), False)
])

# Create DataFrame
members_df = spark.createDataFrame(all_members, schema=members_schema)

print(f"✓ Created DataFrame with {members_df.count():,} rows")
members_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save to Unity Catalog

# COMMAND ----------

table_name = f"{CATALOG}.{SCHEMA}.member_profiles"

print(f"Writing to {table_name}...")

members_df.write \
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

print("\nMember status distribution:")
display(
    spark.table(table_name)
    .groupBy("member_status")
    .count()
    .orderBy(col("count").desc())
)

print("\nAge distribution:")
display(
    spark.table(table_name)
    .selectExpr("FLOOR(DATEDIFF(CURRENT_DATE(), date_of_birth) / 365.25) AS age")
    .groupBy("age")
    .count()
    .orderBy("age")
    .limit(20)
)

print("\nPlan distribution:")
display(
    spark.table(table_name)
    .groupBy("plan_id")
    .count()
    .orderBy(col("count").desc())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Table Comment

# COMMAND ----------

spark.sql(f"""
COMMENT ON TABLE {table_name} IS
'Member enrollment profiles including demographics, plan information, and risk scores.
Contains PHI data - access restricted per HIPAA requirements.
Generated for Ontos healthcare payor demo.'
""")

print(f"✓ Added table comment")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 80)
print("MEMBER TABLE CREATION COMPLETE")
print("=" * 80)
print(f"Table: {table_name}")
print(f"Rows: {members_df.count():,}")
print(f"Enrollment Range: {ENROLLMENT_START} to {ENROLLMENT_END}")
print()
print("Next Steps:")
print("1. Update Ontos Data Contract 'Healthcare Member Data Contract'")
print(f"   - Set physicalName: '{table_name}'")
print("2. Update Ontos Data Product 'Member 360 View v1'")
print(f"   - Add input port referencing this table")
print("3. Run UC Tag Sync job in Ontos")
print("4. Verify tags:")
print(f"   SHOW TAGS ON TABLE {table_name};")
print("=" * 80)
