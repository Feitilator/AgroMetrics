import numpy as np
import pandas as pd

from lightgbm import LGBMClassifier
from lightgbm import early_stopping
from lightgbm import log_evaluation

from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

import joblib

from config import (

    LATITUDE,
    LONGITUDE,

    TIMEZONE,

    START_DATE,
    END_DATE,

    MODEL_DIR,

    TRAIN_END_YEAR,

    VALIDATION_END_YEAR,

    TEST_START_YEAR
)

from openmeteo_client import (

    get_historical_weather,

    hourly_to_daily
)

from features import (

    create_dekad_dataset,

    FEATURES
)

from targets import (

    create_targets
)




def check_dataset(
    df,
    name
):

    print()
    print("=" * 70)

    print(
        f"CHECK: {name}"
    )

    print("=" * 70)

    print(
        "Shape:",
        df.shape
    )

    if "year" in df.columns:

        print(
            "Years:",
            df["year"].min(),
            "→",
            df["year"].max()
        )

    print()
    print(
        "NaN:"
    )

    nan = (
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    print(
        nan[
            nan > 0
        ]
    )



def prepare_ml_data(df):
    """
    Подготовка данных для LightGBM.

    ET0 здесь НЕ используется:
    Open-Meteo в текущем источнике его не предоставляет
    в нашем наборе данных, поэтому модель работает с
    фактически доступными метеорологическими признаками.
    """

    print()
    print("=" * 70)
    print("PREPARING ML DATA")
    print("=" * 70)

    df = df.copy()

    print(
        "Initial shape:",
        df.shape
    )


    required = [
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

        "sukhovei_days_7d",
        "sukhovei_days_14d",
        "sukhovei_days_30d",

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

    targets = [
        "target_drought",
        "target_sukhovei",
        "target_early_snow",
    ]



    all_required = (
        required +
        targets
    )

    missing = [
        col
        for col in all_required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns:\n"
            +
            "\n".join(missing)
        )


    print()
    print("NaN in features:")

    nan_counts = (
        df[required]
        .isna()
        .sum()
    )

    nan_counts = (
        nan_counts[
            nan_counts > 0
        ]
        .sort_values(
            ascending=False
        )
    )

    if len(nan_counts) == 0:

        print("  None")

    else:

        for column, count in nan_counts.items():

            print(
                f"  {column}: {count}"
            )

    print()
    print(
        "Rows before dropna:",
        len(df)
    )


    df = df.dropna(
        subset=(
            required +
            targets
        )
    ).copy()

    print(
        "Rows after dropna:",
        len(df)
    )

    if len(df) == 0:

        raise ValueError(
            "После удаления NaN не осталось строк."
        )


    X = df[required].copy()

    y = {
        target: df[target].astype(int)
        for target in targets
    }
    for target in targets:

        classes = (
            df[target]
            .dropna()
            .unique()
        )

        print()
        print(target)

        print(
            df[target]
            .value_counts()
            .sort_index()
        )

        if len(classes) < 2:
            print(
                f"WARNING: {target} "
                f"contains only one class."
            )

    print()
    print(
        "X shape:",
        X.shape
    )

    print()
    print("Targets:")

    for target in targets:

        print(
            f"\n{target}:"
        )

        print(
            y[target]
            .value_counts()
            .sort_index()
        )

    return df




def create_time_split(
    dataset
):

    train = dataset[
        dataset["year"]
        <= TRAIN_END_YEAR
    ].copy()

    validation = dataset[

        (dataset["year"] > TRAIN_END_YEAR)

        &

        (dataset["year"] <= VALIDATION_END_YEAR)

    ].copy()

    test = dataset[
        dataset["year"]
        >= TEST_START_YEAR
    ].copy()

    print()
    print("=" * 70)

    print(
        "TIME SPLIT"
    )

    print("=" * 70)

    print(
        "Train:",
        train.shape
    )

    print(
        "Validation:",
        validation.shape
    )

    print(
        "Test:",
        test.shape
    )

    print()

    print(
        "Train years:",
        train["year"].min(),
        "→",
        train["year"].max()
    )

    print(
        "Validation years:",
        validation["year"].min(),
        "→",
        validation["year"].max()
    )

    print(
        "Test years:",
        test["year"].min(),
        "→",
        test["year"].max()
    )

    if len(train) == 0:

        raise ValueError(
            "TRAIN пуст."
        )

    if len(validation) == 0:

        raise ValueError(
            "VALIDATION пуст."
        )

    if len(test) == 0:

        raise ValueError(
            "TEST пуст."
        )

    return (
        train,
        validation,
        test
    )




def train_model(

    train,

    validation,

    test,

    target,

    filename

):

    print()
    print("=" * 70)

    print(
        f"TRAINING: {filename}"
    )

    print("=" * 70)


    X_train = train[
        FEATURES
    ].copy()

    y_train = train[
        target
    ].copy()

    X_val = validation[
        FEATURES
    ].copy()

    y_val = validation[
        target
    ].copy()

    X_test = test[
        FEATURES
    ].copy()

    y_test = test[
        target
    ].copy()


    print()
    print(
        "X_train:",
        X_train.shape
    )

    print(
        "X_val:",
        X_val.shape
    )

    print(
        "X_test:",
        X_test.shape
    )

    print()
    print(
        "Target distribution:"
    )

    print(
        y_train
        .value_counts()
        .sort_index()
    )


    classes = (
        y_train
        .unique()
    )

    if len(classes) < 2:

        raise ValueError(

            f"{target} содержит только "
            f"{len(classes)} класс.\n\n"

            "LightGBM binary classifier "
            "не может обучиться.\n"

            "Нужно изменить правило "
            "разметки target."

        )



    model = LGBMClassifier(

        objective="binary",

        n_estimators=1000,

        learning_rate=0.03,

        num_leaves=31,

        max_depth=-1,

        min_child_samples=15,

        subsample=0.8,

        colsample_bytree=0.8,

        reg_alpha=0.1,

        reg_lambda=0.1,

        random_state=42,

        n_jobs=-1,

        verbosity=-1
    )

    print()
    print(
        "LightGBM training..."
    )

    model.fit(

        X_train,

        y_train,

        eval_set=[
            (
                X_val,
                y_val
            )
        ],

        eval_metric="binary_logloss",

        callbacks=[

            early_stopping(
                100,
                verbose=True
            ),

            log_evaluation(
                50
            )

        ]
    )


    val_probability = (
        model.predict_proba(
            X_val
        )[:, 1]
    )

    print()
    print("=" * 70)

    print(
        "VALIDATION"
    )

    print("=" * 70)

    if len(
        np.unique(
            y_val
        )
    ) == 2:

        print(
            "ROC-AUC:",
            round(
                roc_auc_score(
                    y_val,
                    val_probability
                ),
                4
            )
        )

        print(
            "PR-AUC:",
            round(
                average_precision_score(
                    y_val,
                    val_probability
                ),
                4
            )
        )


    test_probability = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    test_prediction = (
        test_probability >= 0.5
    ).astype(int)

    print()
    print("=" * 70)

    print(
        "TEST"
    )

    print("=" * 70)

    print(
        classification_report(

            y_test,

            test_prediction,

            zero_division=0

        )
    )

    print(
        "Confusion matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            test_prediction
        )
    )

    if len(
        np.unique(
            y_test
        )
    ) == 2:

        print(
            "ROC-AUC:",
            round(
                roc_auc_score(
                    y_test,
                    test_probability
                ),
                4
            )
        )

        print(
            "PR-AUC:",
            round(
                average_precision_score(
                    y_test,
                    test_probability
                ),
                4
            )
        )



    importance = pd.DataFrame({

        "feature":
            FEATURES,

        "importance":
            model.feature_importances_

    })

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False
        )
    )

    print()
    print(
        "FEATURE IMPORTANCE"
    )

    print(
        importance
        .head(20)
        .to_string(
            index=False
        )
    )


    model_path = (
        MODEL_DIR
        /
        f"{filename}.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    print()
    print(
        "Saved:",
        model_path
    )



    importance_path = (
        MODEL_DIR
        /
        f"{filename}_importance.csv"
    )

    importance.to_csv(
        importance_path,
        index=False
    )

    return model



def main():

    print()
    print("=" * 70)

    print(
        "AGRO RISK — TRAINING"
    )

    print("=" * 70)


    hourly = get_historical_weather(

        latitude=LATITUDE,

        longitude=LONGITUDE,

        start_date=START_DATE,

        end_date=END_DATE,

        timezone=TIMEZONE

    )

    print()
    print(
        "Hourly:",
        hourly.shape
    )


    daily = hourly_to_daily(
        hourly
    )

    print()
    print(
        "Daily:",
        daily.shape
    )



    dekad = create_dekad_dataset(
        daily
    )

    print()
    print(
        "Dekad:",
        dekad.shape
    )

    check_dataset(
        dekad,
        "DEKAD"
    )


    dataset = create_targets(
        dekad
    )

    print()
    print(
        "After targets:",
        dataset.shape
    )



    dataset = prepare_ml_data(
        dataset
    )

    check_dataset(
        dataset,
        "FINAL ML DATASET"
    )



    (
        train,
        validation,
        test
    ) = create_time_split(
        dataset
    )



    train_model(

        train,

        validation,

        test,

        target="target_drought",

        filename="drought"

    )

    train_model(

        train,

        validation,

        test,

        target="target_sukhovei",

        filename="sukhovei"

    )

    train_model(

        train,

        validation,

        test,

        target="target_early_snow",

        filename="early_snow"

    )

    print()
    print("=" * 70)

    print(
        "TRAINING COMPLETE"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()