from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field



app = FastAPI(
    title="AgroMetrics Risk API",
    description="API для оценки риска погодных сельскохозяйственных опасностей",
    version="4.0"
)



BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"




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



class RiskRequest(BaseModel):

    temperature_mean: float = Field(..., description="Средняя температура, °C")
    temperature_max: float = Field(..., description="Максимальная температура, °C")
    temperature_min: float = Field(..., description="Минимальная температура, °C")

    precipitation: float = Field(..., ge=0, description="Осадки, мм")
    snowfall: float = Field(..., ge=0, description="Снегопад, см")

    wind_speed_max: float = Field(..., ge=0, description="Максимальная скорость ветра, км/ч")
    wind_gusts_max: float = Field(..., ge=0, description="Максимальные порывы ветра, км/ч")

    et0: float = Field(..., ge=0, description="ET0, мм")

    dew_point: float = Field(..., description="Точка росы, °C")

    humidity_mean: float = Field(..., ge=0, le=100, description="Средняя влажность, %")
    humidity_min: float = Field(..., ge=0, le=100, description="Минимальная влажность, %")

    soil_moisture_0_7: float = Field(..., ge=0, le=1)
    soil_moisture_7_28: float = Field(..., ge=0, le=1)
    soil_moisture_28_100: float = Field(..., ge=0, le=1)

    soil_temperature_0_7: float
    soil_temperature_7_28: float
    soil_temperature_28_100: float

    solar_radiation: float = Field(..., ge=0, description="Солнечная радиация, MJ/m²")
    cloud_cover: float = Field(..., ge=0, le=100, description="Облачность, %")
    pressure: float = Field(..., ge=0, description="Давление, hPa")

    month: int = Field(..., ge=1, le=12, description="Месяц")



MODELS = {}


def load_models():
    model_files = {
        "drought": "drought_model.pkl",
        "sukhovey": "sukhovey_model.pkl",
        "early_snow": "early_snow_model.pkl",
    }

    for name, filename in model_files.items():

        model_path = MODEL_DIR / filename

        if not model_path.exists():
            raise FileNotFoundError(
                f"Модель не найдена: {model_path}"
            )

        MODELS[name] = joblib.load(model_path)



load_models()




def get_risk_level(probability: float) -> str:

    if probability >= 0.75:
        return "HIGH"

    if probability >= 0.45:
        return "MEDIUM"

    return "LOW"




def predict_target(name: str, data: dict):

    model = MODELS[name]

    row = pd.DataFrame([data])


    row = row[FEATURES]

    row = (
        row
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    probability = float(
        model.predict_proba(row)[0][1]
    )

    return {
        "probability": round(probability, 4),
        "probability_percent": round(probability * 100, 2),
        "threshold": 0.5,
        "alert": bool(probability >= 0.5),
        "risk": get_risk_level(probability)
    }



@app.get("/")
def root():

    return {
        "name": "AgroMetrics Risk API",
        "version": "4.0",
        "status": "online",
        "description": "Agricultural weather risk assessment API",
        "models": [
            "drought",
            "sukhovey",
            "early_snow"
        ]
    }




@app.get("/health")
def health():

    return {
        "status": "ok",
        "models_loaded": list(MODELS.keys())
    }



@app.post("/risk")
def risk(request: RiskRequest):

    try:

        data = request.model_dump()

        result = {}

        for name in [
            "drought",
            "sukhovey",
            "early_snow"
        ]:

            result[name] = predict_target(
                name,
                data
            )

        probabilities = {
            name: result[name]["probability"]
            for name in result
        }

        max_name = max(
            probabilities,
            key=probabilities.get
        )

        max_probability = probabilities[max_name]

        return {

            "status": "success",

            "risk": result,

            "overall": {
                "hazard": max_name,
                "probability": round(
                    max_probability,
                    4
                ),
                "probability_percent": round(
                    max_probability * 100,
                    2
                ),
                "risk": get_risk_level(
                    max_probability
                )
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )




@app.on_event("startup")
def startup_event():

    print("=" * 60)
    print("AGROMETRICS RISK API")
    print("=" * 60)
    print("Status: ONLINE")
    print(f"Models directory: {MODEL_DIR}")
    print(f"Loaded models: {list(MODELS.keys())}")
    print("=" * 60)