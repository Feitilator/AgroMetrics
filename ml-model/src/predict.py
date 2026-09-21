import os
import json

import joblib
import pandas as pd


# ============================================================
# НАСТРОЙКИ
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# ============================================================
# ПРИЗНАКИ
# ============================================================

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


# ============================================================
# ВВОД ЧИСЛА
# ============================================================

def ask_float(name, unit=""):

    while True:

        value = input(
            f"{name}"
            + (f" ({unit})" if unit else "")
            + ": "
        )

        value = value.replace(",", ".")

        try:
            return float(value)

        except ValueError:

            print(
                "❌ Введи число."
            )


def ask_int(name, min_value=None, max_value=None):

    while True:

        value = input(
            f"{name}: "
        )

        try:

            value = int(value)

            if min_value is not None and value < min_value:
                print(
                    f"❌ Значение должно быть не меньше {min_value}."
                )
                continue

            if max_value is not None and value > max_value:
                print(
                    f"❌ Значение должно быть не больше {max_value}."
                )
                continue

            return value

        except ValueError:

            print(
                "❌ Введи целое число."
            )


# ============================================================
# УРОВЕНЬ РИСКА
# ============================================================

def get_risk(probability):

    if probability >= 0.75:
        return "ВЫСОКИЙ"

    elif probability >= 0.45:
        return "СРЕДНИЙ"

    else:
        return "НИЗКИЙ"


# ============================================================
# ВВОД ПОГОДНЫХ ПАРАМЕТРОВ
# ============================================================

def get_weather_parameters():

    print("\n" + "=" * 60)
    print("ВВЕДИТЕ ПАРАМЕТРЫ ПОГОДЫ")
    print("=" * 60)

    print(
        "\nТемпература:"
    )

    temperature_mean = ask_float(
        "Средняя температура",
        "°C"
    )

    temperature_max = ask_float(
        "Максимальная температура",
        "°C"
    )

    temperature_min = ask_float(
        "Минимальная температура",
        "°C"
    )

    print(
        "\nОсадки:"
    )

    precipitation = ask_float(
        "Осадки",
        "мм"
    )

    snowfall = ask_float(
        "Снег",
        "см"
    )

    print(
        "\nВетер:"
    )

    wind_speed_max = ask_float(
        "Максимальная скорость ветра",
        "км/ч"
    )

    wind_gusts_max = ask_float(
        "Максимальные порывы ветра",
        "км/ч"
    )

    print(
        "\nИспарение и влажность:"
    )

    et0 = ask_float(
        "ET0 / испаряемость",
        "мм"
    )

    dew_point = ask_float(
        "Точка росы",
        "°C"
    )

    humidity_mean = ask_float(
        "Средняя влажность",
        "%"
    )

    humidity_min = ask_float(
        "Минимальная влажность",
        "%"
    )

    print(
        "\nВлажность почвы:"
    )

    soil_moisture_0_7 = ask_float(
        "Влажность почвы 0-7 см",
        "м³/м³"
    )

    soil_moisture_7_28 = ask_float(
        "Влажность почвы 7-28 см",
        "м³/м³"
    )

    soil_moisture_28_100 = ask_float(
        "Влажность почвы 28-100 см",
        "м³/м³"
    )

    print(
        "\nТемпература почвы:"
    )

    soil_temperature_0_7 = ask_float(
        "Температура почвы 0-7 см",
        "°C"
    )

    soil_temperature_7_28 = ask_float(
        "Температура почвы 7-28 см",
        "°C"
    )

    soil_temperature_28_100 = ask_float(
        "Температура почвы 28-100 см",
        "°C"
    )

    print(
        "\nДополнительные параметры:"
    )

    solar_radiation = ask_float(
        "Солнечная радиация",
        "MJ/m²"
    )

    cloud_cover = ask_float(
        "Облачность",
        "%"
    )

    pressure = ask_float(
        "Давление",
        "hPa"
    )

    print(
        "\nСезонный параметр:"
    )

    month = ask_int(
        "Месяц (1-12)",
        1,
        12
    )

    # --------------------------------------------------------
    # Формируем словарь
    # --------------------------------------------------------

    data = {

        "temperature_mean": temperature_mean,
        "temperature_max": temperature_max,
        "temperature_min": temperature_min,

        "precipitation": precipitation,
        "snowfall": snowfall,

        "wind_speed_max": wind_speed_max,
        "wind_gusts_max": wind_gusts_max,

        "et0": et0,
        "dew_point": dew_point,

        "humidity_mean": humidity_mean,
        "humidity_min": humidity_min,

        "soil_moisture_0_7": soil_moisture_0_7,
        "soil_moisture_7_28": soil_moisture_7_28,
        "soil_moisture_28_100": soil_moisture_28_100,

        "soil_temperature_0_7": soil_temperature_0_7,
        "soil_temperature_7_28": soil_temperature_7_28,
        "soil_temperature_28_100": soil_temperature_28_100,

        "solar_radiation": solar_radiation,
        "cloud_cover": cloud_cover,
        "pressure": pressure,

        "month": month,
    }

    return data


# ============================================================
# ЗАГРУЗКА МОДЕЛИ
# ============================================================

def load_model(name):

    model_file = os.path.join(
        MODELS_DIR,
        f"{name}_model.pkl"
    )

    if not os.path.exists(model_file):

        raise FileNotFoundError(
            f"\nНе найдена модель:\n{model_file}\n"
            f"\nСначала запусти:\n"
            f"python -m src.train"
        )

    return joblib.load(
        model_file
    )


# ============================================================
# ПОЛУЧЕНИЕ ВЕРОЯТНОСТИ
# ============================================================

def get_probability(model, data):

    df = pd.DataFrame(
        [data]
    )

    df = df[FEATURES]

    probability = model.predict_proba(
        df
    )[0][1]

    return float(probability)


# ============================================================
# ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА
# ============================================================

def print_result(
    title,
    probability
):

    percent = probability * 100

    risk = get_risk(
        probability
    )

    print(
        f"\n{title}"
    )

    print(
        f"Вероятность: {percent:.1f}%"
    )

    print(
        f"Риск: {risk}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("             AGROMETRICS ML")
    print("       АНАЛИЗ ПО ПАРАМЕТРАМ ПОГОДЫ")
    print("=" * 60)

    print(
        "\nМодель не требует даты."
    )

    print(
        "Введите текущие погодные параметры."
    )

    # --------------------------------------------------------
    # Получаем параметры
    # --------------------------------------------------------

    data = get_weather_parameters()

    print(
        "\nПараметры получены."
    )

    # --------------------------------------------------------
    # Загружаем модели
    # --------------------------------------------------------

    print(
        "\nЗагрузка моделей..."
    )

    drought_model = load_model(
        "drought"
    )

    sukhovey_model = load_model(
        "sukhovey"
    )

    early_snow_model = load_model(
        "early_snow"
    )

    print(
        "Модели загружены."
    )

    # --------------------------------------------------------
    # Предсказания
    # --------------------------------------------------------

    drought_probability = get_probability(
        drought_model,
        data
    )

    sukhovey_probability = get_probability(
        sukhovey_model,
        data
    )

    early_snow_probability = get_probability(
        early_snow_model,
        data
    )

    # --------------------------------------------------------
    # Результаты
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("                 РЕЗУЛЬТАТ")
    print("=" * 60)

    print_result(
        "🌵 ЗАСУХА",
        drought_probability
    )

    print_result(
        "🌬 СУХОВЕЙ",
        sukhovey_probability
    )

    print_result(
        "❄ РАННИЙ СНЕГ",
        early_snow_probability
    )

    # --------------------------------------------------------
    # Общий риск
    # --------------------------------------------------------

    overall = max(
        drought_probability,
        sukhovey_probability,
        early_snow_probability
    )

    print("\n" + "-" * 60)

    print(
        f"МАКСИМАЛЬНЫЙ РИСК: {overall * 100:.1f}%"
    )

    print(
        f"ОБЩИЙ УРОВЕНЬ: {get_risk(overall)}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()