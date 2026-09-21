from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = BASE_DIR / "data" / "ml_dataset.csv"

df = pd.read_csv(FILE)

print("=" * 60)
print("AGROMETRICS LABEL CHECK")
print("=" * 60)

for target in ["drought", "sukhovey", "early_snow"]:

    print()
    print("-" * 60)
    print(target.upper())
    print("-" * 60)

    counts = df[target].value_counts().sort_index()

    print(counts)

    total = len(df)

    for value, count in counts.items():
        percent = count / total * 100
        print(
            f"{value}: {count:,} "
            f"({percent:.2f}%)"
        )

print()
print("=" * 60)
print("BY REGION")
print("=" * 60)

region_stats = df.groupby("region")[
    ["drought", "sukhovey", "early_snow"]
].sum()

print(region_stats.to_string())

print()
print("=" * 60)
print("BY MONTH")
print("=" * 60)

df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.month

month_stats = df.groupby("month")[
    ["drought", "sukhovey", "early_snow"]
].sum()

print(month_stats.to_string())