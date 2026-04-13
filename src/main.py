import pandas as pd
import matplotlib.pyplot as plt

# 1. Load data
usage_events = pd.read_parquet("../data/usage_events.parquet")
profile_installation = pd.read_parquet("../data/profile_installation.parquet")
sim_card_plan_history = pd.read_parquet("../data/sim_card_plan_history.parquet")
rate_card = pd.read_parquet("../data/rate_card.parquet")

tables = {
    "usage_events": usage_events,
    "profile_installation": profile_installation,
    "sim_card_plan_history": sim_card_plan_history,
    "rate_card": rate_card,
}

#Check a sample of the data
for name, df in tables.items():
    print(f"\n=== {name} ===")
    print(df.head(10))
    print("\nColumns:", df.columns)
    print("\nShape:", df.shape)

#qc validation    
# for name, df in tables.items():
#     print(f"\n=== {name} ===")
#     print("Columns:", df.columns.tolist())
#     print("Nulls:\n", df.isnull().sum())
#     print("Duplicates:", df.duplicated().sum())





# 2. Data Quality + Cleaning
usage_events["evt_dttm"] = pd.to_datetime(usage_events["evt_dttm"])
usage_events["ld_dttm"] = pd.to_datetime(usage_events["ld_dttm"])

profile_installation["beg_dttm"] = pd.to_datetime(profile_installation["beg_dttm"])
profile_installation["end_dttm"] = pd.to_datetime(profile_installation["end_dttm"])

sim_card_plan_history["eff_dttm"] = pd.to_datetime(sim_card_plan_history["eff_dttm"])
sim_card_plan_history["x_dttm"] = pd.to_datetime(sim_card_plan_history["x_dttm"])

rate_card["beg_dttm"] = pd.to_datetime(rate_card["beg_dttm"])
rate_card["end_dttm"] = pd.to_datetime(rate_card["end_dttm"])

# Clean tech
usage_events["tech_clean"] = usage_events["tech"].str.strip().str.upper()
rate_card["tech_cd_clean"] = rate_card["tech_cd"].astype(str).str.upper()    

#Check points 
print("\n=== usage_events AFTER CLEANING ===")
print(usage_events.head())
print(rate_card.head())







# 3. Line chart

# Create date column
usage_events["date"] = usage_events["evt_dttm"].dt.date

# Aggregate
daily_usage = usage_events.groupby("date")["mb"].sum().reset_index()

# Plot
plt.figure(figsize=(8, 4))
plt.plot(daily_usage["date"], daily_usage["mb"])
plt.title("Total Usage (MB) per Day")
plt.xlabel("Date")
plt.ylabel("MB")
plt.xticks(rotation=45)
plt.tight_layout()

# Save
plt.savefig("../outputs/usage_mb_per_day.png")

print("\n Line chart saved to outputs in a png/")






# 4. Joins
# joins relationship
# usage_events.pid -> profile_installation.pid
# profile_installation.asset_id -> sim_card_plan_history.asset_id
# sim_card_plan_history.bundle_id -> rate_card.bundle_id

# --- Inspect columns before joins ---
print("\n usage_events columns:", usage_events.columns.tolist())
print("profile_installation columns:", profile_installation.columns.tolist())
print("sim_card_plan_history columns:", sim_card_plan_history.columns.tolist())
print("rate_card columns:", rate_card.columns.tolist())

# join 1 usage -> profile_installation
merged = usage_events.merge(profile_installation, on="pid", how="left")

merged = merged[
    (merged["evt_dttm"] >= merged["beg_dttm"]) &
    (
        (merged["evt_dttm"] < merged["end_dttm"]) |
        (merged["end_dttm"].isna())
    )
]

print("\n After join 1: usage -> profile_installation:", merged.shape)



# join 2 profile_installation -> sim_card_plan_history

merged = merged.merge(sim_card_plan_history, on="asset_id", how="left")

merged = merged[
    (merged["evt_dttm"] >= merged["eff_dttm"]) &
    (
        (merged["evt_dttm"] < merged["x_dttm"]) |
        (merged["x_dttm"].isna())
    )
]

print("After join 2: profile_installation -> sim_card_plan_history: ", merged.shape)


# join 3 sim_card_plan_history -> rate_card
merged = merged.merge(rate_card, on=["bundle_id", "cc1", "cc2"], how="left")

merged = merged[
    (merged["evt_dttm"] >= merged["beg_dttm_y"]) &
    (
        (merged["evt_dttm"] < merged["end_dttm_y"]) |
        (merged["end_dttm_y"].isna())
    )
]
print("After join 3: sim_card_plan_history -> rate_card: ", merged.shape)


merged["tech_match"] = (
    (merged["tech_clean"] == merged["tech_cd_clean"]) |
    (merged["tech_cd_clean"] == "")
)

merged = merged.sort_values("prio_nbr")
merged = merged.drop_duplicates(subset=["sid"], keep="first")





# 5. Final answers

#Highest usage SIM
top_sim = (
    merged.groupby("asset_id")["mb"]
    .sum()
    .sort_values(ascending=False)
    .head(1)
)

print("\n Top SIM:")
print(top_sim)


#Total Cost
merged["cost"] = merged["mb"] * merged["rt_amt"]

total_cost = merged["cost"].sum()

print("\n Total cost:", total_cost)


#3G count
count_3g = (usage_events["tech_clean"] == "3G").sum()
print("\n 3G events:", count_3g)


#Duplicate count
dup_count = usage_events.duplicated().sum()
print("\n Duplicate events:", dup_count)
