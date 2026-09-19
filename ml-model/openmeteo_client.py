import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

import openmeteo_requests
import requests_cache
from retry_requests import retry


# ============================================================
# НАСТРОЙКИ
# ============================================================

HISTORICAL_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)

CACHE_DIR = Path(".cache")
DATA_CACHE_DIR = Path(".weather_cache")

CACHE_DIR.mkdir(exist_ok=True)
DATA_CACHE_DIR.mkdir(exist_ok=True)


# ============================================================
# OPEN-METEO CLIENT
# ============================================================

cache_session = requests_cache.CachedSession(
    str(CACHE_DIR),
    expire_after=3600
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.5
)

openmeteo = openmeteo_requests.Client(
    session=retry_session
)


# ============================================================
# VARIABLES
# ============================================================

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


# ============================================================
# TIMESTAMPS
# ============================================================

def build_api_timestamps(hourly):

    first_variable = hourly.Variables(0)

    values = first_variable.ValuesAsNumpy()

    n = len(values)

    start_timestamp = hourly.Time()

    interval_seconds = hourly.Interval()

    timestamps = (
        start_timestamp
        + np.arange(
            n,
            dtype=np.int64
        )
        * interval_seconds
    )

    dates = pd.to_datetime(
        timestamps,
        unit="s",
        utc=True
    )

    dates = dates.tz_localize(None)

    return dates


# ============================================================
# DOWNLOAD ONE PERIOD
# ============================================================

def download_hourly(
    latitude,
    longitude,
    start_date,
    end_date,
    timezone,
    model,
    variables,
    max_attempts=5
):

    print()
    print("=" * 70)
    print(f"DOWNLOADING {model.upper()}")
    print(f"{start_date} -> {end_date}")
    print("=" * 70)

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "start_date": start_date,

        "end_date": end_date,

        "hourly": variables,

        # API timestamps are kept in UTC.
        "timezone": "UTC",

        "temperature_unit": "celsius",

        "wind_speed_unit": "ms",

        "precipitation_unit": "mm",

        "models": model,

        "cell_selection": "land",
    }


    last_error = None


    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            f"[Open-Meteo] Attempt "
            f"{attempt}/{max_attempts}"
        )

        try:

            start_time = time.time()

            responses = openmeteo.weather_api(
                HISTORICAL_URL,
                params=params
            )

            elapsed = time.time() - start_time

            print(
                f"[Open-Meteo] Response received "
                f"in {elapsed:.1f}s"
            )

            if not responses:

                raise RuntimeError(
                    "Open-Meteo returned no responses."
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
                    f"{variable_name:45s}"
                    f"{len(values):8d}"
                )

                if len(values) != len(dates):

                    raise ValueError(
                        f"Length mismatch for "
                        f"{variable_name}: "
                        f"{len(values)} != "
                        f"{len(dates)}"
                    )

                data[
                    variable_name
                ] = values


            df = pd.DataFrame(data)


            duplicate_count = (
                df["date"]
                .duplicated()
                .sum()
            )


            if duplicate_count > 0:

                raise ValueError(
                    f"{model}: "
                    f"duplicate timestamps detected: "
                    f"{duplicate_count}"
                )


            print()

            print(
                "Shape:",
                df.shape
            )

            print(
                "Date:",
                df["date"].min(),
                "->",
                df["date"].max()
            )

            print(
                "Duplicate timestamps:",
                duplicate_count
            )


            nan_count = (
                df.isna()
                .sum()
                .sum()
            )

            print(
                "Total NaN:",
                nan_count
            )


            print()

            print(
                "[OK] Download completed."
            )


            return df


        except Exception as error:

            last_error = error

            print()
            print(
                f"[ERROR] Attempt "
                f"{attempt}/{max_attempts} failed:"
            )

            print(
                repr(error)
            )


            if attempt < max_attempts:

                wait_time = min(
                    10 * attempt,
                    60
                )

                print(
                    f"Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )


    raise RuntimeError(
        f"Failed to download "
        f"{model} data for "
        f"{start_date} -> {end_date} "
        f"after {max_attempts} attempts."
    ) from last_error


# ============================================================
# CACHE FILE NAME
# ============================================================

def get_cache_filename(
    model,
    start_date,
    end_date
):

    return (
        DATA_CACHE_DIR
        / f"{model}_{start_date}_{end_date}.csv"
    )


# ============================================================
# DOWNLOAD WITH LOCAL CACHE
# ============================================================

def download_period_cached(
    latitude,
    longitude,
    start_date,
    end_date,
    timezone,
    model,
    variables
):

    cache_file = get_cache_filename(
        model,
        start_date,
        end_date
    )


    # --------------------------------------------------------
    # USE EXISTING CACHE
    # --------------------------------------------------------

    if cache_file.exists():

        print()
        print(
            f"[CACHE] Found:"
            f" {cache_file}"
        )

        try:

            df = pd.read_csv(
                cache_file,
                parse_dates=["date"]
            )

            print(
                f"[CACHE] Loaded "
                f"{len(df)} rows."
            )

            return df

        except Exception as error:

            print(
                "[CACHE] Failed to read "
                "cache file."
            )

            print(
                repr(error)
            )

            print(
                "[CACHE] Downloading again..."
            )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    df = download_hourly(

        latitude=latitude,

        longitude=longitude,

        start_date=start_date,

        end_date=end_date,

        timezone=timezone,

        model=model,

        variables=variables
    )


    # --------------------------------------------------------
    # SAVE CACHE
    # --------------------------------------------------------

    df.to_csv(
        cache_file,
        index=False
    )

    print(
        f"[CACHE] Saved:"
        f" {cache_file}"
    )


    return df


# ============================================================
# YEAR GENERATOR
# ============================================================

def generate_periods(
    start_date,
    end_date
):

    start = pd.Timestamp(
        start_date
    )

    end = pd.Timestamp(
        end_date
    )


    current = start


    while current <= end:

        year_end = pd.Timestamp(
            year=current.year,
            month=12,
            day=31
        )

        period_end = min(
            year_end,
            end
        )


        yield (
            current.strftime("%Y-%m-%d"),
            period_end.strftime("%Y-%m-%d")
        )


        current = (
            period_end
            + pd.Timedelta(days=1)
        )


# ============================================================
# DOWNLOAD MULTIPLE YEARS
# ============================================================

def download_by_periods(
    latitude,
    longitude,
    start_date,
    end_date,
    timezone,
    model,
    variables
):

    parts = []


    periods = list(
        generate_periods(
            start_date,
            end_date
        )
    )


    print()
    print("=" * 70)
    print(
        f"{model.upper()} PERIODS: "
        f"{len(periods)}"
    )
    print("=" * 70)


    for index, (
        period_start,
        period_end
    ) in enumerate(
        periods,
        start=1
    ):

        print()
        print(
            f"[{index}/{len(periods)}] "
            f"{period_start} -> {period_end}"
        )


        part = download_period_cached(

            latitude=latitude,

            longitude=longitude,

            start_date=period_start,

            end_date=period_end,

            timezone=timezone,

            model=model,

            variables=variables
        )


        parts.append(part)


    if not parts:

        raise RuntimeError(
            f"No weather data downloaded "
            f"for {model}."
        )


    df = pd.concat(
        parts,
        ignore_index=True
    )


    df["date"] = pd.to_datetime(
        df["date"]
    )


    df = (
        df
        .sort_values("date")
        .drop_duplicates(
            subset=["date"],
            keep="first"
        )
        .reset_index(drop=True)
    )


    return df


# ============================================================
# GET HISTORICAL WEATHER
# ============================================================

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
        f"Location: "
        f"{latitude}, {longitude}"
    )

    print(
        f"Period: "
        f"{start_date} -> {end_date}"
    )


    # ========================================================
    # ERA5-LAND
    # ========================================================

    land = download_by_periods(

        latitude=latitude,

        longitude=longitude,

        start_date=start_date,

        end_date=end_date,

        timezone=timezone,

        model="era5_land",

        variables=ERA5_LAND_VARIABLES
    )


    # ========================================================
    # ERA5
    # ========================================================

    era5 = download_by_periods(

        latitude=latitude,

        longitude=longitude,

        start_date=start_date,

        end_date=end_date,

        timezone=timezone,

        model="era5",

        variables=ERA5_VARIABLES
    )


    # ========================================================
    # CHECK
    # ========================================================

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
            "ERA5-Land contains "
            "duplicate timestamps."
        )


    if era5["date"].duplicated().any():

        raise ValueError(
            "ERA5 contains "
            "duplicate timestamps."
        )


    # ========================================================
    # MERGE
    # ========================================================

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


    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


    print(
        "Merged shape:",
        df.shape
    )


    print()

    print(
        "Merged date:"
    )

    print(
        df["date"].min(),
        "->",
        df["date"].max()
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


# ============================================================
# HOURLY -> DAILY
# ============================================================

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


    # ========================================================
    # DAILY AGGREGATION
    # ========================================================

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


    # ========================================================
    # FLATTEN COLUMNS
    # ========================================================

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


    # ========================================================
    # SOIL MOISTURE
    # ========================================================

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


    # ========================================================
    # SOIL TEMPERATURE
    # ========================================================

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


    # ========================================================
    # DIAGNOSTICS
    # ========================================================

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
        "->",
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
