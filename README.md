# 💳 Payment Reconciliation System

## 📌 Overview
This project simulates a payment platform and bank settlement system and performs reconciliation to identify mismatches.

It detects real-world financial anomalies such as:
- Missing settlements
- Amount mismatches
- Cross-month settlements
- Duplicate entries
- Invalid refunds

---

## ⚙️ How It Works
1. Generate synthetic transaction data
2. Simulate delayed bank settlements
3. Inject real-world anomalies
4. Run reconciliation logic
5. Output categorized issues

---

## ▶️ Run Locally

```bash
pip install pandas numpy
python reconciliation.py
