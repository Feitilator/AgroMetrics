import numpy as np
import pandas as pd



def create_targets(
    dekad
):

    df = dekad.copy()


    df = (
        df
        .sort_values(
            [
                "year",
                "dekad"
            ]
        )
        .reset_index(drop=True)
    )


    drought_score = (

        (
            df["precip_30d"] < 20
        ).astype(int)

        +

        (
            df["soil_moisture_30d"]
            <
            df["soil_moisture_30d"]
            .rolling(
                36,
                min_periods=5
            )
            .quantile(0.30)
        ).astype(int)

        +

        (
            df["vpd_mean_7d"] >= 1.2
        ).astype(int)

        +

        (
            df["dry_days_14d"] >= 10
        ).astype(int)

    )

    df["drought_score"] = (
        drought_score
    )

    df["target_drought"] = (
        drought_score >= 3
    ).astype(int)



    df["target_sukhovei"] = (

        (
                df["sukhovei_days_14d"] >= 1
        )

    ).astype(int)



    month = (
        pd.to_datetime(
            df["date"]
        )
        .dt.month
    )

    early_snow = (

        month.isin(
            [
                8,
                9,
                10
            ]
        )

        &

        (
            df["snowfall"]
            > 0
        )

        &

        (
            df["t_min"]
            <= 2
        )

    )

    df["target_early_snow"] = (
        early_snow
        .astype(int)
    )


    target_columns = [

        "target_drought",

        "target_sukhovei",

        "target_early_snow"
    ]

    df = df.dropna(
        subset=target_columns
    ).copy()


    print()
    print("=" * 70)
    print("TARGETS")
    print("=" * 70)

    for target in target_columns:

        print()
        print(target)

        print(
            df[target]
            .value_counts(
                dropna=False
            )
            .sort_index()
        )

    return df
