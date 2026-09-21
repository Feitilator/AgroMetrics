import os
import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# НАСТРОЙКИ
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "ml_dataset.csv"
)

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)


os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


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


TARGETS = {
    "drought": "drought",
    "sukhovey": "sukhovey",
    "early_snow": "early_snow",
}


# ============================================================
# ЗАГРУЗКА
# ============================================================

def load_dataset():

    print("Загрузка dataset...")

    df = pd.read_csv(DATA_FILE)

    print(f"Строк: {len(df)}")
    print(f"Колонок: {len(df.columns)}")

    return df


# ============================================================
# ОБУЧЕНИЕ ОДНОЙ МОДЕЛИ
# ============================================================

def train_model(df, target_name, target_column):

    print("\n" + "=" * 60)
    print(f"ОБУЧЕНИЕ: {target_name.upper()}")
    print("=" * 60)

    X = df[FEATURES]
    y = df[target_column]

    print("\nРаспределение классов:")

    print(
        y.value_counts().rename(
            index={
                0: "Нет",
                1: "Да"
            }
        )
    )

    positive_count = int(y.sum())

    if positive_count < 20:

        print(
            "\n⚠️ ВНИМАНИЕ:"
        )

        print(
            f"Для класса '{target_name}' всего "
            f"{positive_count} положительных примеров."
        )

        print(
            "Модель будет обучена, но качество "
            "для этого класса может быть нестабильным."
        )

    # --------------------------------------------------------
    # TRAIN / TEST
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("\nTrain:", len(X_train))
    print("Test :", len(X_test))

    # --------------------------------------------------------
    # RANDOM FOREST
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=14,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\nОбучение модели...")

    model.fit(
        X_train,
        y_train
    )

    print("Модель обучена.")

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        y_pred
    )

    print("\nМЕТРИКИ:")

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1       : {f1:.4f}"
    )

    print("\nConfusion Matrix:")

    print(matrix)

    # --------------------------------------------------------
    # СОХРАНЕНИЕ МОДЕЛИ
    # --------------------------------------------------------

    model_file = os.path.join(
        MODELS_DIR,
        f"{target_name}_model.pkl"
    )

    joblib.dump(
        model,
        model_file
    )

    print(
        f"\nМодель сохранена:"
    )

    print(model_file)

    # --------------------------------------------------------
    # СОХРАНЯЕМ FEATURES
    # --------------------------------------------------------

    features_file = os.path.join(
        MODELS_DIR,
        f"{target_name}_feature_names.json"
    )

    with open(
        features_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            FEATURES,
            f,
            ensure_ascii=False,
            indent=4
        )

    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    importance = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    importance_file = os.path.join(
        RESULTS_DIR,
        f"{target_name}_feature_importance.csv"
    )

    importance.to_csv(
        importance_file,
        index=False
    )

    # --------------------------------------------------------
    # METRICS JSON
    # --------------------------------------------------------

    metrics = {
        "model": target_name,
        "samples_total": len(df),
        "samples_train": len(X_train),
        "samples_test": len(X_test),
        "positive_samples": positive_count,

        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),

        "confusion_matrix": matrix.tolist()
    }

    metrics_file = os.path.join(
        RESULTS_DIR,
        f"{target_name}_metrics.json"
    )

    with open(
        metrics_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metrics,
            f,
            ensure_ascii=False,
            indent=4
        )

    # --------------------------------------------------------
    # TOP FEATURES
    # --------------------------------------------------------

    print("\nТоп параметров:")

    print(
        importance.head(10).to_string(
            index=False
        )
    )

    return model


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("AGROMETRICS ML")
    print("ОБУЧЕНИЕ МОДЕЛЕЙ ПО ПАРАМЕТРАМ ПОГОДЫ")
    print("=" * 60)

    df = load_dataset()

    # Проверяем признаки

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in df.columns
    ]

    if missing_features:

        print(
            "\nОШИБКА! Нет признаков:"
        )

        for feature in missing_features:
            print(
                f" - {feature}"
            )

        return

    # Обучаем все три модели

    for target_name, target_column in TARGETS.items():

        train_model(
            df,
            target_name,
            target_column
        )

    print("\n" + "=" * 60)
    print("ВСЕ МОДЕЛИ ОБУЧЕНЫ")
    print("=" * 60)

    print("\nСозданы:")

    print("models/drought_model.pkl")
    print("models/sukhovey_model.pkl")
    print("models/early_snow_model.pkl")

    print("\nГотово!")


if __name__ == "__main__":
    main()