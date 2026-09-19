import numpy as np
import pandas as pd
import joblib

from config import (
    LATITUDE,
    LONGITUDE,
    TIMEZONE,
    START_DATE,
    END_DATE,
    MODEL_DIR
)

from openmeteo_client import (
    get_historical_weather,
    hourly_to_daily
)

from features import (
    create_dekad_dataset,
    FEATURES
)




def load_models():

    drought = joblib.load(
        MODEL_DIR /
        "drought.joblib"
    )

    sukhovei = joblib.load(
        MODEL_DIR /
        "sukhovei.joblib"
    )

    early_snow = joblib.load(
        MODEL_DIR /
        "early_snow.joblib"
    )

    return (
        drought,
        sukhovei,
        early_snow
    )




def risk_level(
    probability
):

    if probability < 0.25:

        return "LOW"

    if probability < 0.50:

        return "MODERATE"

    if probability < 0.75:

        return "HIGH"

    return "VERY_HIGH"




def predict():

    print()
    print("=" * 70)

    print(
        "AGRO RISK — PREDICTION"
    )

    print("=" * 70)


    hourly = get_historical_weather(

        latitude=LATITUDE,

        longitude=LONGITUDE,

        start_date=START_DATE,

        end_date=END_DATE,

        timezone=TIMEZONE

    )

    daily = hourly_to_daily(
        hourly
    )

    dekad = create_dekad_dataset(
        daily
    )



    latest = (
        dekad
        .sort_values("date")
        .iloc[-1]
        .copy()
    )

    X = pd.DataFrame(
        [
            latest[
                FEATURES
            ]
        ]
    )


    (
        drought_model,
        sukhovei_model,
        snow_model

    ) = load_models()



    drought_probability = (
        drought_model
        .predict_proba(X)[0][1]
    )

    sukhovei_probability = (
        sukhovei_model
        .predict_proba(X)[0][1]
    )

    snow_probability = (
        snow_model
        .predict_proba(X)[0][1]
    )



    result = {

        "date":
            str(
                latest["date"]
            ),

        "drought_probability":
            float(
                drought_probability
            ),

        "drought_risk":
            risk_level(
                drought_probability
            ),

        "sukhovei_probability":
            float(
                sukhovei_probability
            ),

        "sukhovei_risk":
            risk_level(
                sukhovei_probability
            ),

        "early_snow_probability":
            float(
                snow_probability
            ),

        "early_snow_risk":
            risk_level(
                snow_probability
            ),
    }



    print()

    print(
        "DEKAD:",
        result["date"]
    )

    print()

    print(
        "DROUGHT:"
    )

    print(
        f"  Probability: "
        f"{result['drought_probability']:.3f}"
    )

    print(
        f"  Risk: "
        f"{result['drought_risk']}"
    )

    print()

    print(
        "SUKHOVEI:"
    )

    print(
        f"  Probability: "
        f"{result['sukhovei_probability']:.3f}"
    )

    print(
        f"  Risk: "
        f"{result['sukhovei_risk']}"
    )

    print()

    print(
        "EARLY SNOW:"
    )

    print(
        f"  Probability: "
        f"{result['early_snow_probability']:.3f}"
    )

    print(
        f"  Risk: "
        f"{result['early_snow_risk']}"
    )

    return result


if __name__ == "__main__":

    predict()