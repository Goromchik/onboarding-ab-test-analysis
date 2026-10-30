import os
import numpy as np
import pandas as pd

np.random.seed(42)

os.makedirs("data/raw", exist_ok=True)

n_users = 6000
dates = pd.date_range("2024-01-01", periods=30, freq="D")

user_ids = np.arange(1, n_users + 1)
variant = np.random.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5])

signup_dates = pd.to_datetime(np.random.choice(dates.values, size=n_users))

acquisition_channel = np.random.choice(
    ["organic", "paid_search", "referral", "social"],
    size=n_users,
    p=[0.38, 0.28, 0.18, 0.16]
)

device_type = np.random.choice(
    ["desktop", "mobile", "tablet"],
    size=n_users,
    p=[0.5, 0.45, 0.05]
)

region = np.random.choice(
    ["NA", "EU", "APAC", "LATAM"],
    size=n_users,
    p=[0.35, 0.3, 0.25, 0.1]
)

base_conversion = {
    "control": 0.22,
    "treatment": 0.27
}

data = []

for i in range(n_users):
    v = variant[i]
    channel = acquisition_channel[i]
    device = device_type[i]
    region_name = region[i]
    signup_date = pd.to_datetime(signup_dates[i])

    session_count = np.random.poisson(4 + (0.8 if v == "treatment" else 0))
    onboarding_step_completed = np.random.binomial(1, 0.7 + (0.12 if v == "treatment" else 0))
    completed_onboarding = 1 if onboarding_step_completed else 0

    prob = base_conversion[v]
    if channel == "organic":
        prob += 0.04
    if device == "mobile":
        prob -= 0.02
    if region_name == "EU":
        prob += 0.02

    converted = int(np.random.binomial(1, min(prob, 0.6)))

    if converted:
        time_to_conversion = int(np.random.normal(4.5, 2.0))
        time_to_conversion = max(1, min(time_to_conversion, 21))
    else:
        time_to_conversion = np.nan

    revenue = round(np.random.gamma(3.0, 12.0) if converted else 0, 2)

    data.append({
        "user_id": user_ids[i],
        "variant": v,
        "signup_date": signup_date.strftime("%Y-%m-%d"),
        "acquisition_channel": channel,
        "device_type": device,
        "region": region_name,
        "onboarding_step_completed": onboarding_step_completed,
        "session_count": session_count,
        "completed_onboarding": completed_onboarding,
        "converted": converted,
        "time_to_conversion": time_to_conversion,
        "revenue": revenue
    })

df = pd.DataFrame(data)
df["signup_date"] = pd.to_datetime(df["signup_date"])

df.loc[np.random.choice(df.index, 50, replace=False), "time_to_conversion"] = np.nan
df.loc[np.random.choice(df.index, 20, replace=False), "revenue"] = np.nan

out_path = "data/raw/experiment_data.csv"
df.to_csv(out_path, index=False)

print(f"Generated experiment data: {df.shape[0]} rows")
print(f"Saved to: {out_path}")
print(df.head())