from pathlib import Path
import pandas as pd

# ============================================================
# PERSONAL FINANCE ANALYTICS - DATA QUALITY VALIDATION
# ============================================================
# Purpose:
# Validate financial transaction data before loading it
# into the Snowflake RAW layer.
#
# Checks:
# 1. Dataset structure and column names
# 2. Data types
# 3. Missing values
# 4. Duplicate transactions
# 5. Invalid dates
# 6. Invalid transaction amounts
# 7. Invalid transaction types
# 8. Overall PASS/FAIL status
# 9. Export data quality report
# ============================================================


# ------------------------------------------------------------
# 1. DEFINE PROJECT FILE PATHS
# ------------------------------------------------------------

# Locate the project folder automatically.
# This works regardless of where the script is executed.
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "sample_transactions.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "data_quality_report.csv"


# ------------------------------------------------------------
# 2. DEFINE EXPECTED DATA STRUCTURE
# ------------------------------------------------------------

# Expected columns based on our Snowflake RAW table.
EXPECTED_COLUMNS = [
    "Date",
    "Year",
    "Month",
    "Description",
    "Category",
    "Subcategory",
    "Type",
    "Payment Method",
    "Fixed/Variable",
    "Needs/Wants",
    "Amount"
]

# Allowed transaction types.
VALID_TYPES = ["Income", "Expense"]


# ------------------------------------------------------------
# 3. CREATE REUSABLE VALIDATION FUNCTION
# ------------------------------------------------------------

def validate_transactions(file_path):

    # Read CSV data into a pandas DataFrame.
    df = pd.read_csv(file_path)

    print("========== DATASET INFORMATION ==========")

    # Display total rows and columns.
    print("Dataset shape:", df.shape)

    # Display column data types before conversion.
    print("\nOriginal data types:")
    print(df.dtypes)

    # Check whether all required columns are present.
    missing_columns = [
        col for col in EXPECTED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # 4. VALIDATE DATA TYPES
    # --------------------------------------------------------

    # Convert Date into datetime.
    # Invalid date values become NaT.
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        format="%Y-%m-%d"
    )

    # Convert Amount into numeric format.
    # Invalid text values become NaN.
    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    # Check data types after conversion.
    print("\nData types after conversion:")
    print(df.dtypes)

    # --------------------------------------------------------
    # 5. CHECK MISSING VALUES
    # --------------------------------------------------------

    # Count missing values across all columns.
    missing_values = int(df.isnull().sum().sum())

    # Count invalid or missing dates.
    invalid_dates = int(df["Date"].isna().sum())

    # Count invalid or missing amounts.
    invalid_amount_format = int(df["Amount"].isna().sum())

    # --------------------------------------------------------
    # 6. CHECK DUPLICATE TRANSACTIONS
    # --------------------------------------------------------

    # Identify exact duplicate rows.
    duplicate_count = int(df.duplicated().sum())

    # --------------------------------------------------------
    # 7. VALIDATE TRANSACTION AMOUNTS
    # --------------------------------------------------------

    # Amounts must be greater than zero.
    # Missing/non-numeric amounts are counted separately.
    invalid_amounts = int(
        (df["Amount"] <= 0).sum()
    ) + invalid_amount_format

    # --------------------------------------------------------
    # 8. VALIDATE TRANSACTION TYPES
    # --------------------------------------------------------

    # Only Income and Expense are permitted.
    invalid_types = int(
        (~df["Type"].isin(VALID_TYPES)).sum()
    )

    # --------------------------------------------------------
    # 9. GENERATE DATA QUALITY REPORT
    # --------------------------------------------------------

    # Store validation results in a dictionary.
    report = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "missing_values": missing_values,
        "duplicate_records": duplicate_count,
        "invalid_dates": invalid_dates,
        "invalid_amounts": invalid_amounts,
        "invalid_types": invalid_types
    }

    # Missing values already include invalid dates and
    # non-numeric amounts after conversion.
    # Check each metric for PASS/FAIL without double counting.
    quality_checks = [
        missing_values,
        duplicate_count,
        invalid_dates,
        invalid_amounts,
        invalid_types
    ]

    # Overall validation status.
    report["status"] = (
        "PASS" if all(count == 0 for count in quality_checks)
        else "FAIL"
    )

    # --------------------------------------------------------
    # 10. DISPLAY VALIDATION RESULTS
    # --------------------------------------------------------

    print("\n========== DATA QUALITY REPORT ==========")

    for key, value in report.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # 11. EXPORT REPORT TO CSV
    # --------------------------------------------------------

    # Convert dictionary into a one-row DataFrame.
    report_df = pd.DataFrame([report])

    # Save report as CSV without pandas index.
    report_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nReport saved to: {OUTPUT_FILE}")

    # --------------------------------------------------------
    # 12. PREVENT INVALID DATA FROM PROCEEDING
    # --------------------------------------------------------

    if report["status"] == "FAIL":
        print("\nValidation failed. Review data before loading.")
    else:
        print("\nValidation passed. Data is ready for review.")

    # Return results for reuse in other Python scripts.
    return report


# ------------------------------------------------------------
# 13. RUN VALIDATION
# ------------------------------------------------------------

# Execute only when this file is run directly.
if __name__ == "__main__":
    validate_transactions(INPUT_FILE)