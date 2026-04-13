# Telecom Usage Data Analysis

## Overview
This project analyzes telecom usage data to answer business questions, generate a usage trend visualization, and evaluate the current data model.

The solution focuses on:
- Data cleaning and standardization
- Time-based joins across multiple tables
- Rate resolution logic using priority and fallback rules
- Business metric calculations

---
## Tech Stack
- Python 3.11+
- pandas
- matplotlib

---
## How to Run

### Option 1 — GitHub Codespaces (Recommended)
1. Open the repository in GitHub
2. Click **Code → Codespaces → Create Codespace**
3. Wait for environment setup
4. Run on the terminal:

``` bash
python src/main.py
```

### Option 2 — Local Environment
``` bash
pip install pandas pyarrow matplotlib
```

Run:
``` bash
python src/main.py
```

---
## Expected Output

Running the script will:

- Generate a line chart:
    - outputs/usage_mb_per_day.png
- Print:
-    Top SIM card by usage
-    Total cost of usage
-    Count of 3G events
-    Duplicate event count


---
## Summary
1. Data Load
    - Inspected schema, null values, and duplicates 

2. Data Cleaning
    - Standardized timestamp fields

3. Normalized technology values (e.g., LTE, 4g → uppercase)
    - Handled null values in key fields

4. Data Integration
- Joined tables using both keys and time validity windows:
-     usage_events → profile_installation
-     profile_installation → sim_card_plan_history
-     sim_card_plan_history → rate_card

5. Rate Resolution Logic
    - Allowed both exact tech matches and fallback (null tech)
    - Selected best rate using prio_nbr

6. Analysis and answers