import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =====================================================
# CONFIG
# =====================================================
np.random.seed(42)
NUM_TRANSACTIONS = 100
MONTH = 3   # March

# =====================================================
# STEP 1: GENERATE TRANSACTIONS DATA
# =====================================================
def generate_transactions():
    transactions = pd.DataFrame({
        "txn_id": [f"T{i}" for i in range(NUM_TRANSACTIONS)],
        "amount": np.round(np.random.uniform(100, 1000, NUM_TRANSACTIONS), 2),
        "date": [
            datetime(2024, MONTH, 1) + timedelta(days=np.random.randint(0, 30))
            for _ in range(NUM_TRANSACTIONS)
        ],
        "type": "payment"
    })

    # Add refund with no original transaction
    refund = pd.DataFrame({
        "txn_id": ["T_refund"],
        "amount": [-200.00],
        "date": [datetime(2024, MONTH, 15)],
        "type": ["refund"]
    })

    transactions = pd.concat([transactions, refund], ignore_index=True)

    return transactions


# =====================================================
# STEP 2: GENERATE SETTLEMENT DATA
# =====================================================
def generate_settlements(transactions):
    settlements = transactions.copy()

    # Settlement delay (1–2 days)
    settlements["settlement_date"] = settlements["date"] + pd.to_timedelta(
        np.random.randint(1, 3, len(settlements)), unit='D'
    )

    # --- Inject anomalies ---

    # 1. Missing settlement
    settlements = settlements.drop(index=5)

    # 2. Duplicate entry
    duplicate_row = settlements.iloc[[10]]
    settlements = pd.concat([settlements, duplicate_row], ignore_index=True)

    # 3. Rounding mismatch
    settlements.loc[0, "amount"] += 0.03

    # 4. Cross-month settlement
    settlements.loc[1, "settlement_date"] = datetime(2024, 4, 2)

    # 5. Remove refund → simulate invalid refund (KEY FIX)
    settlements = settlements[settlements["txn_id"] != "T_refund"]

    # Keep only required columns
    settlements = settlements[["txn_id", "amount", "settlement_date"]]

    return settlements


# =====================================================
# STEP 3: RECONCILIATION LOGIC
# =====================================================
def reconcile(transactions, settlements):

    merged = pd.merge(
        transactions,
        settlements,
        on="txn_id",
        how="outer",
        indicator=True,
        suffixes=("_txn", "_settle")
    )

    issues = {}

    # Missing settlement
    issues["missing_settlement"] = merged[merged["_merge"] == "left_only"]

    # Extra settlement
    issues["extra_settlement"] = merged[merged["_merge"] == "right_only"]

    # Amount mismatch
    issues["amount_mismatch"] = merged[
        (merged["_merge"] == "both") &
        (np.round(merged["amount_txn"], 2) != np.round(merged["amount_settle"], 2))
    ]

    # Cross-month settlement
    issues["cross_month"] = merged[
        (merged["_merge"] == "both") &
        (merged["date"].dt.month != merged["settlement_date"].dt.month)
    ]

    # Duplicate settlements
    duplicates = settlements[settlements.duplicated(subset=["txn_id"], keep=False)]
    issues["duplicates"] = duplicates

    # Refund without original match
    issues["invalid_refunds"] = transactions[
        (transactions["type"] == "refund") &
        (~transactions["txn_id"].isin(settlements["txn_id"]))
    ]

    return issues


# =====================================================
# STEP 4: PRINT RESULTS
# =====================================================
def print_report(issues):
    print("\n========== RECONCILIATION REPORT ==========\n")

    for issue, df in issues.items():
        print(f"\n--- {issue.upper()} ({len(df)} cases) ---")
        if df.empty:
            print("No issues found")
        else:
            print(df.head())

    print("\n========== SUMMARY ==========")
    for issue, df in issues.items():
        print(f"{issue}: {len(df)}")


# =====================================================
# MAIN EXECUTION
# =====================================================
def main():
    print("Generating test data...\n")

    transactions = generate_transactions()
    settlements = generate_settlements(transactions)

    # Save CSVs (for demo/submission)
    transactions.to_csv("transactions.csv", index=False)
    settlements.to_csv("settlements.csv", index=False)

    print("Running reconciliation...\n")

    issues = reconcile(transactions, settlements)

    print_report(issues)


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    main()