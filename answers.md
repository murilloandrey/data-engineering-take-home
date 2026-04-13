
# Answers

## 1. SIM Card with Highest Usage
- **SIM Card (asset_id):** 1001
- **Total Usage:** 165 MB

---

## 2. Number of 3G Usage Events
- **Count:** 0

---

## 3. Number of Duplicate Usage Events
- **Count:** 0

---

## 4. Total Cost of All Usage
- **Total Cost:** 15.83 USD

---

## Notes

- Duplicate detection was based on full row comparison
- Technology values were standardized before counting 3G events
- Cost calculation was based on `mb * rt_amt`
- Rate selection used both matching logic and priority rules


## Data qualities and issues found 

### 1. Inconsistent Technology Values
- Examples: `LTE`, `lte`, `4g`, `5g`
- Issue: prevents reliable joins with rate_card
- Fix: standardized using `.str.upper().strip()`

---

### 2. Null Values in Key Fields
- `tech` contains nulls
- `rate_card.tech_cd` contains nulls (fallback rates)
- Fix:
  - usage_events → filled with empty string for comparison
  - rate_card → null treated as fallback condition

---

### 3. Open-Ended Date Ranges
- `end_dttm` and `x_dttm` frequently null
- Interpretation: record is still active
- Fix: used logic:

---

### 4. Multiple Matching Rates
During the join with `rate_card`, multiple rows can match a single usage event.

Example:
- Event: `tech = 4G`
- Matches:
- `tech_cd = 4G` (specific rate)
- `tech_cd = null` (fallback rate)

This created an issue on join 3. 

### Problem
A single usage event can match multiple rate records:
- Exact match (e.g., 4G = 4G)
- Fallback match (tech_cd is null)

Without handling this:
- Duplicate rows are created
- Cost calculations are inflated

---

### Solution

1. Allow both matches:
 - Exact match (`tech_clean == tech_cd_clean`)
 - Fallback (`tech_cd IS NULL`)

2. Apply priority logic:
 - Sort by `prio_nbr`
 - Keep best match per event

```python
merged = merged.sort_values("prio_nbr")
merged = merged.drop_duplicates(subset=["sid"], keep="first")
```