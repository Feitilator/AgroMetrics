import os
import pandas as pd




BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


INPUT_FILE_2024 = os.path.join(
    DATA_DIR,
    "weather_2024.csv"
)

INPUT_FILE_2025 = os.path.join(
    DATA_DIR,
    "weather_2025.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "ml_dataset.csv"
)




FEATURES = [
    "temperature_mean",
    "temperature_max",
    "temperature_min",

    "precipitation",
    "snowfall",

    "wind_speed_max",
    "wind_gusts_max",

    "et0",
    "dew_point",

    "humidity_mean",
    "humidity_min",

    "soil_moisture_0_7",
    "soil_moisture_7_28",
    "soil_moisture_28_100",

    "soil_temperature_0_7",
    "soil_temperature_7_28",
    "soil_temperature_28_100",

    "solar_radiation",
    "cloud_cover",
    "pressure",

    "month",
]




REGIONS = {
    0: "Akmola Region",
    1: "Aktobe Region",
    2: "Almaty Region",
    3: "Atyrau Region",
    4: "West Kazakhstan Region",
    5: "Zhambyl Region",
    6: "Zhetisu Region",
    7: "Karaganda Region",
    8: "Kostanay Region",
    9: "Kyzylorda Region",
    10: "Mangystau Region",
    11: "Pavlodar Region",
    12: "North Kazakhstan Region",
    13: "Turkistan Region",
    14: "Abai Region",
    15: "Ulytau Region",
    16: "East Kazakhstan Region",
}



COLUMN_RENAME = {
    "time": "date",

    "temperature_2m_mean (°C)": "temperature_mean",
    "temperature_2m_max (°C)": "temperature_max",
    "temperature_2m_min (°C)": "temperature_min",

    "precipitation_sum (mm)": "precipitation",
    "rain_sum (mm)": "rain",
    "snowfall_sum (cm)": "snowfall",

    "precipitation_hours (h)": "precipitation_hours",

    "sunshine_duration (s)": "sunshine_duration",

    "shortwave_radiation_sum (MJ/m²)": "solar_radiation",

    "wind_speed_10m_max (km/h)": "wind_speed_max",
    "wind_gusts_10m_max (km/h)": "wind_gusts_max",
    "wind_direction_10m_dominant (°)": "wind_direction",

    "et0_fao_evapotranspiration (mm)": "et0",

    "dew_point_2m_mean (°C)": "dew_point",

    "relative_humidity_2m_mean (%)": "humidity_mean",
    "relative_humidity_2m_max (%)": "humidity_max",
    "relative_humidity_2m_min (%)": "humidity_min",

    "soil_moisture_0_to_7cm_mean (m³/m³)": "soil_moisture_0_7",
    "soil_moisture_7_to_28cm_mean (m³/m³)": "soil_moisture_7_28",
    "soil_moisture_28_to_100cm_mean (m³/m³)": "soil_moisture_28_100",

    "soil_temperature_0_to_7cm_mean (°C)": "soil_temperature_0_7",
    "soil_temperature_7_to_28cm_mean (°C)": "soil_temperature_7_28",
    "soil_temperature_28_to_100cm_mean (°C)": "soil_temperature_28_100",

    "weather_code (wmo code)": "weather_code",

    "cloud_cover_mean (%)": "cloud_cover",

    "surface_pressure_mean (hPa)": "pressure",
}



def load_weather_file(file_path, year):

    print("\n" + "=" * 60)

    print(
        f"Загрузка данных за {year}..."
    )

    print(
        f"Файл: {file_path}"
    )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"\nФайл не найден:\n{file_path}"
        )



    with open(
        file_path,
        "r",
        encoding="utf-8-sig"
    ) as f:

        lines = f.readlines()

    weather_header_index = None

    for i, line in enumerate(lines):

        if line.startswith(
            "location_id,time,"
        ):

            weather_header_index = i

            break

    if weather_header_index is None:

        raise ValueError(
            f"Не удалось найти weather-таблицу в:\n{file_path}"
        )

    from io import StringIO

    weather_text = "".join(
        lines[weather_header_index:]
    )

    df = pd.read_csv(
        StringIO(weather_text)
    )

    print(
        f"Загружено строк за {year}: {len(df)}"
    )


    df = df.rename(
        columns=COLUMN_RENAME
    )


    df["source_year"] = year

    return df



def load_data():

    df_2024 = load_weather_file(
        INPUT_FILE_2024,
        2024
    )

    df_2025 = load_weather_file(
        INPUT_FILE_2025,
        2025
    )


    print("\n" + "=" * 60)
    print("ОБЪЕДИНЕНИЕ ДАННЫХ")
    print("=" * 60)

    df = pd.concat(
        [
            df_2024,
            df_2025
        ],
        ignore_index=True
    )

    print(
        f"Всего строк после объединения: {len(df)}"
    )


    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df = df.sort_values(
            [
                "location_id",
                "date"
            ]
        ).reset_index(
            drop=True
        )

    return df



def check_columns(df):

    required = [
        "temperature_mean",
        "temperature_max",
        "temperature_min",

        "precipitation",
        "snowfall",

        "wind_speed_max",
        "wind_gusts_max",

        "et0",
        "dew_point",

        "humidity_mean",
        "humidity_min",

        "soil_moisture_0_7",
        "soil_moisture_7_28",
        "soil_moisture_28_100",

        "soil_temperature_0_7",
        "soil_temperature_7_28",
        "soil_temperature_28_100",

        "solar_radiation",
        "cloud_cover",
        "pressure",

        "rain",
        "precipitation_hours",
    ]


    if "date" not in df.columns:

        raise ValueError(
            "В CSV отсутствует колонка date."
        )

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        print(
            "\nОШИБКА: отсутствуют колонки:"
        )

        for col in missing:

            print(
                f"  - {col}"
            )

        raise ValueError(
            "В исходных CSV отсутствуют необходимые колонки."
        )

    print(
        "\nВсе необходимые колонки найдены."
    )



def create_drought_label(df):

    score = (
        (df["temperature_mean"] >= 25).astype(int)
        + (df["precipitation"] <= 1).astype(int)
        + (df["et0"] >= 4.5).astype(int)
        + (df["humidity_min"] <= 35).astype(int)
        + (df["soil_moisture_0_7"] <= 0.22).astype(int)
    )

    df["drought_score"] = score

    df["drought"] = (
        score >= 3
    ).astype(int)

    return df



def create_sukhovey_label(df):

    score = (
        (df["temperature_max"] >= 30).astype(int)
        + (df["humidity_min"] <= 30).astype(int)
        + (df["wind_speed_max"] >= 30).astype(int)
        + (df["wind_gusts_max"] >= 40).astype(int)
        + (df["precipitation"] <= 1).astype(int)
    )

    df["sukhovey_score"] = score

    df["sukhovey"] = (
        score >= 3
    ).astype(int)

    return df



def create_early_snow_label(df):

    early_snow = (
        df["month"].isin([9, 10])
        & (df["snowfall"] > 0)
        & (df["temperature_mean"] <= 1)
    )

    df["early_snow_score"] = (
        early_snow.astype(int)
    )

    df["early_snow"] = (
        early_snow.astype(int)
    )

    return df


def prepare_dataset():

    print("\n")
    print("=" * 60)
    print("AGROMETRICS DATA PREPARATION")
    print("2024 + 2025")
    print("=" * 60)


    df = load_data()


    check_columns(df)

    df["month"] = df["date"].dt.month


    print("\nПериод данных:")

    print(
        f"От: {df['date'].min().date()}"
    )

    print(
        f"До: {df['date'].max().date()}"
    )

    print(
        f"Количество регионов: "
        f"{df['location_id'].nunique()}"
    )

    print(
        f"Количество строк: {len(df)}"
    )


    print("\nСоздание labels...")

    df = create_drought_label(df)

    df = create_sukhovey_label(df)

    df = create_early_snow_label(df)


    print("\nПроверка пропусков:")

    missing = df[
        FEATURES
    ].isna().sum()

    total_missing = missing.sum()

    if total_missing > 0:

        print(
            missing[
                missing > 0
            ]
        )

        for col in FEATURES:

            if df[col].isna().any():

                df[col] = df[col].fillna(
                    df[col].median()
                )

    else:

        print(
            "Пропусков нет."
        )


    output_columns = (
        FEATURES
        + [
            "drought_score",
            "drought",

            "sukhovey_score",
            "sukhovey",

            "early_snow_score",
            "early_snow",
        ]
    )

    ml_df = df[
        output_columns
    ].copy()


    ml_df.to_csv(
        OUTPUT_FILE,
        index=False
    )



    print("\n" + "=" * 60)
    print("DATASET ГОТОВ")
    print("=" * 60)

    print(
        f"Строк: {len(ml_df)}"
    )

    print(
        f"Признаков: {len(FEATURES)}"
    )

    print(
        f"Файл: {OUTPUT_FILE}"
    )


    print("\nРаспределение классов:")

    print("\nЗАСУХА:")

    print(
        ml_df[
            "drought"
        ].value_counts()
    )

    print("\nСУХОВЕЙ:")

    print(
        ml_df[
            "sukhovey"
        ].value_counts()
    )

    print("\nРАННИЙ СНЕГ:")

    print(
        ml_df[
            "early_snow"
        ].value_counts()
    )


    print("\nОжидаемый объём:")

    print(
        "2024 + 2025"
    )

    print(
        "Данные объединены успешно."
    )

    print("\nГотово!")




if __name__ == "__main__":

    prepare_dataset()