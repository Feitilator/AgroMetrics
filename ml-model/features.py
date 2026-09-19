import numpy as np
import pandas as pd




FEATURES = [


    "t_mean",
    "t_max",
    "t_min",


    "rh_mean",
    "rh_min",


    "vpd_mean",
    "vpd_max",


    "precip",
    "rain",
    "snowfall",


    "wind_mean",
    "wind_max",
    "wind_gust_max",


    "soil_moisture",


    "soil_temperature",


    "precip_7d",
    "precip_14d",
    "precip_30d",

    "dry_days_7d",
    "dry_days_14d",
    "dry_days_30d",


    "hot_days_7d",
    "hot_days_14d",
    "hot_days_30d",


    "wind_mean_7d",
    "wind_max_7d",


    "vpd_mean_7d",
    "vpd_max_7d",


    "soil_moisture_7d",
    "soil_moisture_14d",
    "soil_moisture_30d",


    "snowfall_7d",
    "snowfall_14d",
]




def create_daily_features(
    daily
):

    df = daily.copy()



    required = [

        "date",

        "t_mean",
        "t_max",
        "t_min",

        "rh_mean",
        "rh_min",

        "vpd_mean",
        "vpd_max",

        "precip",
        "rain",
        "snowfall",

        "wind_mean",
        "wind_max",
        "wind_gust_max",

        "soil_moisture",
        "soil_temperature",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns in daily data:\n"
            +
            "\n".join(missing)
        )



    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


    df["year"] = (
        df["date"]
        .dt.year
    )

    df["month"] = (
        df["date"]
        .dt.month
    )

    df["day"] = (
        df["date"]
        .dt.day
    )

    df["day_of_year"] = (
        df["date"]
        .dt.dayofyear
    )



    df["month"] = (
        df["date"]
        .dt.month
    )

    df["dekad"] = np.select(
        [
            df["day"] <= 10,
            df["day"] <= 20
        ],
        [
            1,
            2
        ],
        default=3
    )



    df["dekad_of_year"] = (
            (df["month"] - 1) * 3
            +
            df["dekad"]
    )



    df["dry_day"] = (
        df["precip"] < 1.0
    ).astype(int)


    df["hot_day"] = (
        df["t_max"] >= 30.0
    ).astype(int)



    df["sukhovei_day"] = (

        (df["t_max"] >= 30.0)

        &

        (df["rh_min"] <= 30.0)

        &

        (df["wind_mean"] >= 5.0)

        &

        (df["vpd_max"] >= 1.5)

    ).astype(int)



    df["high_vpd_day"] = (
        df["vpd_max"] >= 1.5
    ).astype(int)



    df["precip_7d"] = (
        df["precip"]
        .rolling(
            7,
            min_periods=1
        )
        .sum()
    )

    df["precip_14d"] = (
        df["precip"]
        .rolling(
            14,
            min_periods=1
        )
        .sum()
    )

    df["precip_30d"] = (
        df["precip"]
        .rolling(
            30,
            min_periods=1
        )
        .sum()
    )



    df["dry_days_7d"] = (
        df["dry_day"]
        .rolling(
            7,
            min_periods=1
        )
        .sum()
    )

    df["dry_days_14d"] = (
        df["dry_day"]
        .rolling(
            14,
            min_periods=1
        )
        .sum()
    )

    df["dry_days_30d"] = (
        df["dry_day"]
        .rolling(
            30,
            min_periods=1
        )
        .sum()
    )



    df["hot_days_7d"] = (
        df["hot_day"]
        .rolling(
            7,
            min_periods=1
        )
        .sum()
    )

    df["hot_days_14d"] = (
        df["hot_day"]
        .rolling(
            14,
            min_periods=1
        )
        .sum()
    )

    df["hot_days_30d"] = (
        df["hot_day"]
        .rolling(
            30,
            min_periods=1
        )
        .sum()
    )



    df["sukhovei_days_7d"] = (
        df["sukhovei_day"]
        .rolling(
            7,
            min_periods=1
        )
        .sum()
    )

    df["sukhovei_days_14d"] = (
        df["sukhovei_day"]
        .rolling(
            14,
            min_periods=1
        )
        .sum()
    )

    df["sukhovei_days_30d"] = (
        df["sukhovei_day"]
        .rolling(
            30,
            min_periods=1
        )
        .sum()
    )



    df["wind_mean_7d"] = (
        df["wind_mean"]
        .rolling(
            7,
            min_periods=1
        )
        .mean()
    )

    df["wind_max_7d"] = (
        df["wind_max"]
        .rolling(
            7,
            min_periods=1
        )
        .max()
    )



    df["vpd_mean_7d"] = (
        df["vpd_mean"]
        .rolling(
            7,
            min_periods=1
        )
        .mean()
    )

    df["vpd_max_7d"] = (
        df["vpd_max"]
        .rolling(
            7,
            min_periods=1
        )
        .max()
    )



    df["soil_moisture_7d"] = (
        df["soil_moisture"]
        .rolling(
            7,
            min_periods=1
        )
        .mean()
    )

    df["soil_moisture_14d"] = (
        df["soil_moisture"]
        .rolling(
            14,
            min_periods=1
        )
        .mean()
    )

    df["soil_moisture_30d"] = (
        df["soil_moisture"]
        .rolling(
            30,
            min_periods=1
        )
        .mean()
    )


    df["snowfall_7d"] = (
        df["snowfall"]
        .rolling(
            7,
            min_periods=1
        )
        .sum()
    )

    df["snowfall_14d"] = (
        df["snowfall"]
        .rolling(
            14,
            min_periods=1
        )
        .sum()
    )



    df = df.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    return df




def create_dekad_dataset(
    daily
):

    df = create_daily_features(
        daily
    )



    dekad = (

        df
        .groupby(
            [
                "year",
                "dekad_of_year"
            ],
            as_index=False
        )
        .agg({

            "date": "last",



            "t_mean": "mean",
            "t_max": "max",
            "t_min": "min",



            "rh_mean": "mean",
            "rh_min": "min",



            "vpd_mean": "mean",
            "vpd_max": "max",



            "precip": "sum",
            "rain": "sum",
            "snowfall": "sum",



            "wind_mean": "mean",
            "wind_max": "max",
            "wind_gust_max": "max",



            "soil_moisture": "mean",
            "soil_temperature": "mean",



            "precip_7d": "last",
            "precip_14d": "last",
            "precip_30d": "last",



            "dry_days_7d": "last",
            "dry_days_14d": "last",
            "dry_days_30d": "last",



            "hot_days_7d": "last",
            "hot_days_14d": "last",
            "hot_days_30d": "last",



            "sukhovei_days_7d": "last",
            "sukhovei_days_14d": "last",
            "sukhovei_days_30d": "last",



            "wind_mean_7d": "last",
            "wind_max_7d": "last",


            "vpd_mean_7d": "last",
            "vpd_max_7d": "last",



            "soil_moisture_7d": "last",
            "soil_moisture_14d": "last",
            "soil_moisture_30d": "last",


            "snowfall_7d": "last",
            "snowfall_14d": "last",

        }
        )

    )
    dekad = dekad.rename(
        columns={
            "dekad_of_year": "dekad"
        }
    )



    dekad = (
        dekad
        .sort_values(
            [
                "year",
                "dekad"
            ]
        )
        .reset_index(drop=True)
    )



    dekad["dekad_id"] = (
        (dekad["year"] - dekad["year"].min())
        * 36
        +
        (dekad["dekad"] - 1)
    )


    print()
    print("=" * 70)
    print("DEKAD DATA")
    print("=" * 70)

    print(
        "Shape:",
        dekad.shape
    )

    print(
        "Years:",
        dekad["year"].min(),
        "→",
        dekad["year"].max()
    )

    print()
    print(
        "NaN:"
    )

    print(
        dekad.isna()
        .sum()
        .sort_values(
            ascending=False
        )
        .head(30)
    )

    return dekad
