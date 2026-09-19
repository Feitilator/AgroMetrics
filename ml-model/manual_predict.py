import joblib
import pandas as pd




MODEL_PATHS = {
    "drought": "models/drought.joblib",
    "sukhovei": "models/sukhovei.joblib",
    "early_snow": "models/early_snow.joblib",
}




FIELDS = [
    {
        "name": "Поле №1",
        "latitude": 51.9167,
        "longitude": 70.3167,
    },


]




DATA = {
    "t_mean": 18.5,
    "t_max": 27.0,
    "t_min": 9.5,

    "rh_mean": 48.0,
    "rh_min": 25.0,

    "vpd_mean": 1.45,
    "vpd_max": 2.80,

    "precip": 2.0,
    "rain": 2.0,
    "snowfall": 0.0,

    "wind_mean": 5.2,
    "wind_max": 10.5,
    "wind_gust_max": 14.0,

    "soil_moisture": 0.22,
    "soil_temperature": 16.0,

    "precip_7d": 5.0,
    "precip_14d": 8.0,
    "precip_30d": 18.0,

    "dry_days_7d": 4,
    "dry_days_14d": 8,
    "dry_days_30d": 17,

    "hot_days_7d": 2,
    "hot_days_14d": 4,
    "hot_days_30d": 7,

    "sukhovei_days_7d": 1,
    "sukhovei_days_14d": 2,
    "sukhovei_days_30d": 4,

    "wind_mean_7d": 4.8,
    "wind_max_7d": 11.0,

    "vpd_mean_7d": 1.30,
    "vpd_max_7d": 2.70,

    "soil_moisture_7d": 0.23,
    "soil_moisture_14d": 0.24,
    "soil_moisture_30d": 0.26,

    "snowfall_7d": 0.0,
    "snowfall_14d": 0.0,
}



RISK_NAMES = {
    "drought": "Засуха",
    "sukhovei": "Суховей",
    "early_snow": "Ранний снег",
}




def get_risk_level(probability):
    """
    Пока используем простые пороги.

    >= 0.70 -> высокий
    >= 0.40 -> средний
    <  0.40 -> низкий

    В дальнейшем эти пороги можно откалибровать
    на валидационной выборке.
    """

    if probability >= 0.70:
        return "HIGH", "🔴"

    if probability >= 0.40:
        return "MEDIUM", "🟡"

    return "LOW", "🟢"




def load_models():

    models = {}

    for name, path in MODEL_PATHS.items():

        print(
            f"Loading model: {name}"
        )

        models[name] = joblib.load(path)

    return models




def make_input(model):


    feature_names = list(
        model.feature_name_
    )

    missing = [
        feature
        for feature in feature_names
        if feature not in DATA
    ]

    if missing:

        raise ValueError(
            "Не хватает признаков:\n"
            +
            "\n".join(
                f"  - {feature}"
                for feature in missing
            )
        )

    X = pd.DataFrame(
        [
            [
                DATA[feature]
                for feature in feature_names
            ]
        ],
        columns=feature_names
    )

    if X.shape[1] != model.n_features_in_:

        raise ValueError(
            f"Количество признаков не совпадает.\n"
            f"Model: {model.n_features_in_}\n"
            f"Input: {X.shape[1]}"
        )

    return X




def predict_risk(model, X):

    prediction = int(
        model.predict(X)[0]
    )

    probabilities = model.predict_proba(X)[0]

    if len(probabilities) >= 2:

        probability = float(
            probabilities[1]
        )

    else:

        probability = 1.0 if prediction == 1 else 0.0

    level, emoji = get_risk_level(
        probability
    )

    return {
        "prediction": prediction,
        "probability": probability,
        "level": level,
        "emoji": emoji,
    }




def get_factors():

    factors = []

    if DATA["precip_30d"] < 20:

        factors.append(
            f"мало осадков за 30 дней: "
            f"{DATA['precip_30d']:.1f} мм"
        )

    if DATA["dry_days_30d"] >= 15:

        factors.append(
            f"много сухих дней: "
            f"{DATA['dry_days_30d']}"
        )

    if DATA["soil_moisture"] < 0.20:

        factors.append(
            f"низкая влажность почвы: "
            f"{DATA['soil_moisture']:.2f}"
        )

    if DATA["vpd_max"] >= 2.5:

        factors.append(
            f"высокий VPD: "
            f"{DATA['vpd_max']:.2f}"
        )

    if DATA["hot_days_14d"] >= 3:

        factors.append(
            f"жарких дней за 14 дней: "
            f"{DATA['hot_days_14d']}"
        )

    if DATA["sukhovei_days_14d"] >= 1:

        factors.append(
            f"дней с условиями суховея: "
            f"{DATA['sukhovei_days_14d']}"
        )

    if DATA["snowfall_7d"] > 0:

        factors.append(
            f"снег за 7 дней: "
            f"{DATA['snowfall_7d']:.1f}"
        )

    return factors




def main():

    print()
    print("=" * 70)
    print("AGRO RISK — FIELD RISK ANALYSIS")
    print("=" * 70)

    print(
        f"Количество полей: {len(FIELDS)}"
    )



    models = load_models()



    all_results = []


    for field in FIELDS:

        print()
        print()
        print("=" * 70)
        print(
            f"ПОЛЕ: {field['name']}"
        )
        print("=" * 70)

        print(
            f"Координаты: "
            f"{field['latitude']}, "
            f"{field['longitude']}"
        )

        field_result = {
            "field": field["name"],
            "latitude": field["latitude"],
            "longitude": field["longitude"],
            "risks": {},
        }



        for name, model in models.items():

            X = make_input(model)

            result = predict_risk(
                model,
                X
            )

            field_result["risks"][name] = result

            print()
            print(
                f"{result['emoji']} "
                f"{RISK_NAMES[name]}"
            )

            print(
                f"   Вероятность: "
                f"{result['probability'] * 100:.2f}%"
            )

            if result["level"] == "HIGH":

                print(
                    "   УРОВЕНЬ: ВЫСОКИЙ"
                )

            elif result["level"] == "MEDIUM":

                print(
                    "   УРОВЕНЬ: СРЕДНИЙ"
                )

            else:

                print(
                    "   УРОВЕНЬ: НИЗКИЙ"
                )



        factors = get_factors()

        if factors:

            print()
            print("Факторы текущей погоды:")

            for factor in factors:

                print(
                    f"   • {factor}"
                )

        else:

            print()
            print(
                "Выраженных факторов риска "
                "по заданным порогам не обнаружено."
            )

        all_results.append(
            field_result
        )



    print()
    print()
    print("=" * 70)
    print("ОПАСНЫЕ ЗОНЫ")
    print("=" * 70)

    dangerous_found = False

    for field_result in all_results:

        for risk_name, result in field_result["risks"].items():

            if result["level"] in (
                "HIGH",
                "MEDIUM",
            ):

                dangerous_found = True

                print()
                print(
                    f"{result['emoji']} "
                    f"{field_result['field']}"
                )

                print(
                    f"   Координаты: "
                    f"{field_result['latitude']}, "
                    f"{field_result['longitude']}"
                )

                print(
                    f"   Риск: "
                    f"{RISK_NAMES[risk_name]}"
                )

                print(
                    f"   Вероятность: "
                    f"{result['probability'] * 100:.2f}%"
                )

                print(
                    f"   Уровень: "
                    f"{result['level']}"
                )

    if not dangerous_found:

        print()
        print(
            "🟢 Опасных зон по заданным "
            "порогам не обнаружено."
        )



    print()
    print("=" * 70)
    print("МАКСИМАЛЬНЫЙ РИСК")
    print("=" * 70)

    max_risk = None

    for field_result in all_results:

        for risk_name, result in field_result["risks"].items():

            item = {
                "field": field_result["field"],
                "latitude": field_result["latitude"],
                "longitude": field_result["longitude"],
                "risk_name": risk_name,
                "probability": result["probability"],
            }

            if (
                max_risk is None
                or item["probability"]
                > max_risk["probability"]
            ):

                max_risk = item

    if max_risk:

        print()
        print(
            f"{RISK_NAMES[max_risk['risk_name']]} "
            f"— "
            f"{max_risk['probability'] * 100:.2f}%"
        )

        print(
            f"Поле: "
            f"{max_risk['field']}"
        )

        print(
            f"Координаты: "
            f"{max_risk['latitude']}, "
            f"{max_risk['longitude']}"
        )

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
