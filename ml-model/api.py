from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field




BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"




app = FastAPI(
    title="Agro Risk ML API",
    version="1.0.0",
)




MODEL_PATHS = {
    "drought": MODELS_DIR / "drought.joblib",
    "sukhovei": MODELS_DIR / "sukhovei.joblib",
    "early_snow": MODELS_DIR / "early_snow.joblib",
}


models = {}


def load_models():

    for name, path in MODEL_PATHS.items():

        if not path.exists():

            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        print(
            f"Loading {name}: {path}"
        )

        models[name] = joblib.load(path)


load_models()




class PredictRequest(BaseModel):



    field_id: str | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


    t_mean: float
    t_max: float
    t_min: float

    rh_mean: float
    rh_min: float

    vpd_mean: float
    vpd_max: float

    precip: float
    rain: float
    snowfall: float

    wind_mean: float
    wind_max: float
    wind_gust_max: float

    soil_moisture: float
    soil_temperature: float

    precip_7d: float
    precip_14d: float
    precip_30d: float

    dry_days_7d: float
    dry_days_14d: float
    dry_days_30d: float

    hot_days_7d: float
    hot_days_14d: float
    hot_days_30d: float

    sukhovei_days_7d: float
    sukhovei_days_14d: float
    sukhovei_days_30d: float

    wind_mean_7d: float
    wind_max_7d: float

    vpd_mean_7d: float
    vpd_max_7d: float

    soil_moisture_7d: float
    soil_moisture_14d: float
    soil_moisture_30d: float

    snowfall_7d: float
    snowfall_14d: float



def get_model_features(model):


    if hasattr(model, "feature_name_"):

        return list(model.feature_name_)

    if hasattr(model, "booster_"):

        return model.booster_.feature_name()

    raise RuntimeError(
        "Не удалось получить список признаков модели"
    )


def make_dataframe(data: PredictRequest, model):

    values = data.model_dump()


    values.pop("field_id", None)
    values.pop("latitude", None)
    values.pop("longitude", None)

    feature_names = get_model_features(model)

    missing = [
        feature
        for feature in feature_names
        if feature not in values
    ]

    if missing:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "Missing features",
                "features": missing,
            },
        )

    X = pd.DataFrame(
        [
            {
                feature: values[feature]
                for feature in feature_names
            }
        ],
        columns=feature_names,
    )

    return X


def get_prediction(model, X):

    prediction = int(
        model.predict(X)[0]
    )

    probabilities = model.predict_proba(X)[0]

    if len(probabilities) >= 2:

        probability = float(
            probabilities[1]
        )

    else:

        probability = (
            1.0
            if prediction == 1
            else 0.0
        )

    return prediction, probability


def get_risk_level(probability):

    if probability >= 0.70:

        return {
            "level": "HIGH",
            "label": "Высокий",
            "color": "red",
        }

    if probability >= 0.40:

        return {
            "level": "MEDIUM",
            "label": "Средний",
            "color": "yellow",
        }

    return {
        "level": "LOW",
        "label": "Низкий",
        "color": "green",
    }




@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "agro-risk-ml",
        "models": list(models.keys()),
    }




@app.get("/model-info")
def model_info():

    result = {}

    for name, model in models.items():

        features = get_model_features(model)

        result[name] = {
            "features_count": len(features),
            "features": features,
        }

    return result




@app.post("/predict")
def predict(data: PredictRequest):

    results = {}

    for name, model in models.items():

        X = make_dataframe(
            data,
            model,
        )

        prediction, probability = get_prediction(
            model,
            X,
        )

        risk = get_risk_level(
            probability
        )

        results[name] = {
            "prediction": prediction,
            "probability": round(
                probability,
                6,
            ),
            "probability_percent": round(
                probability * 100,
                2,
            ),
            "risk": risk,
        }



    max_risk_name = max(
        results,
        key=lambda name:
            results[name]["probability"]
    )

    max_risk = results[max_risk_name]

    return {
        "success": True,

        "field": {
            "id": data.field_id,
            "latitude": data.latitude,
            "longitude": data.longitude,
        },

        "results": results,

        "highest_risk": {
            "type": max_risk_name,
            "probability": max_risk[
                "probability"
            ],
            "probability_percent": max_risk[
                "probability_percent"
            ],
            "risk": max_risk[
                "risk"
            ],
        },
    }
