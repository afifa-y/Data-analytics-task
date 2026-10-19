"""
Customer Churn Dataset Cleaning
Input: customer_churn_raw_v2.csv
Output: customer_churn_cleaned.csv

Cleaning decisions:
1. Standardize column names to lowercase snake_case.
2. Remove exact duplicate rows (duplicate records contain no new information).
3. Strip leading/trailing spaces from text fields; convert blank text to missing.
4. Convert numeric columns to numeric types; the literal 'unknown' in total charges
   becomes missing during conversion.
5. Fill missing region with 'Unknown' rather than guessing a customer's region.
6. Fill missing total charges with the median of valid total charges to preserve rows
   while reducing sensitivity to extreme values.
7. No date columns exist in this dataset, so no date-format conversion is needed.
"""
import pandas as pd

INPUT_FILE = "customer_churn_raw_v2.csv"
OUTPUT_FILE = "customer_churn_cleaned.csv"

df = pd.read_csv(INPUT_FILE)

df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace(r"([a-z0-9])([A-Z])", r"\1_\2", regex=True)
    .str.replace(r"[^A-Za-z0-9]+", "_", regex=True)
    .str.strip("_")
    .str.lower()
)

start_rows = len(df)
exact_duplicates = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
for col in text_cols:
    df[col] = df[col].astype("string").str.strip()
    df[col] = df[col].replace("", pd.NA)

numeric_cols = [
    "age", "tenure_months", "monthly_charges_inr",
    "total_charges_inr", "support_tickets", "late_payments"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

missing_region_before = int(df["region"].isna().sum())
df["region"] = df["region"].fillna("Unknown").astype("string")

missing_total_before = int(df["total_charges_inr"].isna().sum())
median_total = float(df["total_charges_inr"].median())
df["total_charges_inr"] = df["total_charges_inr"].fillna(median_total)

for col in ["region", "subscription_type", "contract_type",
            "payment_method", "auto_pay", "churn"]:
    df[col] = df[col].astype("string").str.strip()

df.to_csv(OUTPUT_FILE, index=False)

print("Cleaning complete")
print(f"Rows before cleaning: {start_rows}")
print(f"Exact duplicate rows removed: {exact_duplicates}")
print(f"Missing regions filled as 'Unknown': {missing_region_before}")
print(f"Missing total charges median-imputed: {missing_total_before}")
print(f"Median used for total_charges_inr: {median_total:.2f}")
print(f"Rows after cleaning: {len(df)}")
print(f"Saved cleaned data to: {OUTPUT_FILE}")
print("\\nRemaining missing values:")
print(df.isna().sum())
print("\\nFinal data types:")
print(df.dtypes)
