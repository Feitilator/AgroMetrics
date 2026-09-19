import numpy as np
import pandas as pd

import openmeteo_requests
import requests_cache

from retry_requests import retry




cache_session = requests_cache.CachedSession(
    ".cache",
    expire_after=3600
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo = openmeteo_requests.Client(
    session=retry_session
)


HISTORICAL_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)



ERA5_LAND_VARIABLES = [

    "temperature_2m",

    "relative_humidity_2m",

    "vapour_pressure_deficit",

    "soil_moisture_0_to_7cm",

    "soil_moisture_7_to_28cm",

    "soil_moisture_28_to_100cm",

    "soil_temperature_0_to_7cm",

    "soil_temperature_7_to_28cm",

    "soil_temperature_28_to_100cm",
]




ERA5_VARIABLES = [

    "precipitation",

    "rain",

    "snowfall",

    "wind_speed_10m",

    "wind_gusts_10m",
]



def build_api_timestamps(hourly):


    if len(ERA5_LAND_VARIABLES) > 0:

        first_variable = hourly.Variables(0)

    else:

        first_variable = hourly.Variables(0)

    values = first_variable.ValuesAsNumpy()

    n = len(values)

    start_timestamp = hourly.Time()

    interval_seconds = hourly.Interval()

    timestamps = (
        start_timestamp
        +
        np.arange(
            n,
            dtype=np.int64
        )
        *
        interval_seconds
    )

    dates = pd.to_datetime(
        timestamps,
        unit="s",
        utc=True
    )


    dates = dates.tz_localize(None)

    return dates




def download_hourly(
    latitude,
    longitude,
    start_date,
    end_date,
    timezone,
    model,
    variables
):

    print()
    print("=" * 70)
    print(
        f"Downloading {model}"
    )
    print("=" * 70)

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "start_date": start_date,

        "end_date": end_date,

        "hourly": variables,

        "timezone": "UTC",

        "temperature_unit": "celsius",

        "wind_speed_unit": "ms",

        "precipitation_unit": "mm",

        "models": model,

        "cell_selection": "land",
    }

    responses = openmeteo.weather_api(
        HISTORICAL_URL,
        params=params
    )

    response = responses[0]

    print(
        "Grid:",
        response.Latitude(),
        response.Longitude()
    )

    print(
        "Elevation:",
        response.Elevation()
    )

    hourly = response.Hourly()


    dates = build_api_timestamps(
        hourly
    )



    data = {

        "date": dates
    }

    for i, variable_name in enumerate(
        variables
    ):

        values = (
            hourly
            .Variables(i)
            .ValuesAsNumpy()
        )

        print(
            f"{variable_name:45s}",
            len(values)
        )

        if len(values) != len(dates):

            raise ValueError(
                f"Length mismatch for "
                f"{variable_name}: "
                f"{len(values)} != {len(dates)}"
            )

        data[
            variable_name
        ] = values

    df = pd.DataFrame(
        data
    )



    print()
    print(
        "Shape:",
        df.shape
    )

    duplicate_count = (
        df["date"]
        .duplicated()
        .sum()
    )

    print(
        "Duplicate timestamps:",
        duplicate_count
    )

    if duplicate_count > 0:

        duplicates = (
            df.loc[
                df["date"].duplicated(
                    keep=False
                ),
                "date"
            ]
            .drop_duplicates()
            .head(20)
        )

        print(
            duplicates.to_string(
                index=False
            )
        )

        raise ValueError(
            f"{model}: duplicate timestamps detected."
        )

    print()
    print(
        "NaN:"
    )

    print(
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    return df




def get_historical_weather(
    latitude,
    longitude,
    start_date,
    end_date,
    timezone="Asia/Almaty"
):

    print()
    print("=" * 70)
    print("DOWNLOADING WEATHER DATA")
    print("=" * 70)

    print(
        f"Location: {latitude}, {longitude}"
    )

    print(
        f"Period: {start_date} → {end_date}"
    )



    land = download_hourly(

        latitude=latitude,

        longitude=longitude,

        start_date=start_date,

        end_date=end_date,

        timezone=timezone,

        model="era5_land",

        variables=ERA5_LAND_VARIABLES
    )


    era5 = download_hourly(

        latitude=latitude,

        longitude=longitude,

        start_date=start_date,

        end_date=end_date,

        timezone=timezone,

        model="era5",

        variables=ERA5_VARIABLES
    )


    print()
    print("=" * 70)
    print("CHECKING TIMESTAMPS BEFORE MERGE")
    print("=" * 70)

    print(
        "ERA5-Land rows:",
        len(land)
    )

    print(
        "ERA5-Land unique dates:",
        land["date"].nunique()
    )

    print(
        "ERA5-Land duplicated:",
        land["date"].duplicated().sum()
    )

    print()

    print(
        "ERA5 rows:",
        len(era5)
    )

    print(
        "ERA5 unique dates:",
        era5["date"].nunique()
    )

    print(
        "ERA5 duplicated:",
        era5["date"].duplicated().sum()
    )


    if land["date"].duplicated().any():

        raise ValueError(
            "ERA5-Land contains duplicate timestamps."
        )

    if era5["date"].duplicated().any():

        raise ValueError(
            "ERA5 contains duplicate timestamps."
        )


    print()
    print(
        "Merging ERA5-Land + ERA5..."
    )

    df = pd.merge(

        land,

        era5,

        on="date",

        how="inner",

        validate="one_to_one"
    )

    print(
        "Merged shape:",
        df.shape
    )



    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


    print()
    print(
        "Merged NaN:"
    )

    print(
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    return df




def hourly_to_daily(
    hourly_df
):

    df = hourly_df.copy()

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )



    daily = (
        df
        .set_index("date")
        .resample("D")
        .agg({

            "temperature_2m": [
                "mean",
                "max",
                "min"
            ],

            "relative_humidity_2m": [
                "mean",
                "min"
            ],

            "precipitation":
                "sum",

            "rain":
                "sum",

            "snowfall":
                "sum",

            "wind_speed_10m": [
                "mean",
                "max"
            ],

            "wind_gusts_10m":
                "max",

            "vapour_pressure_deficit": [
                "mean",
                "max"
            ],

            "soil_moisture_0_to_7cm":
                "mean",

            "soil_moisture_7_to_28cm":
                "mean",

            "soil_moisture_28_to_100cm":
                "mean",

            "soil_temperature_0_to_7cm":
                "mean",

            "soil_temperature_7_to_28cm":
                "mean",

            "soil_temperature_28_to_100cm":
                "mean",
        })
    )


    daily.columns = [

        "t_mean",
        "t_max",
        "t_min",

        "rh_mean",
        "rh_min",

        "precip",
        "rain",
        "snowfall",

        "wind_mean",
        "wind_max",

        "wind_gust_max",

        "vpd_mean",
        "vpd_max",

        "soil_moisture_0_7",
        "soil_moisture_7_28",
        "soil_moisture_28_100",

        "soil_temp_0_7",
        "soil_temp_7_28",
        "soil_temp_28_100",
    ]

    daily = daily.reset_index()



    daily["soil_moisture"] = (
        daily[
            [
                "soil_moisture_0_7",
                "soil_moisture_7_28",
                "soil_moisture_28_100"
            ]
        ]
        .mean(axis=1)
    )


    daily["soil_temperature"] = (
        daily[
            [
                "soil_temp_0_7",
                "soil_temp_7_28",
                "soil_temp_28_100"
            ]
        ]
        .mean(axis=1)
    )



    print()
    print("=" * 70)
    print("DAILY DATA")
    print("=" * 70)

    print(
        "Shape:",
        daily.shape
    )

    print(
        "Date:",
        daily["date"].min(),
        "→",
        daily["date"].max()
    )

    print()
    print(
        "NaN:"
    )

    print(
        daily.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    return daily
