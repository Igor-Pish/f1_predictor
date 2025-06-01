import joblib
import numpy as np
from model.data_collector import get_gp_input

def use_logreg_predictor(year, round_num):
    # --- Загрузка модели
    model = joblib.load("model/f1_win_logreg.pkl")
    print("📦 Модель загружена")

    # --- Получение входных данных
    X_gp = get_gp_input(year, round_num)

    # --- Предсказание
    probas = model.predict_proba(X_gp)[:, 1]
    X_gp["win_proba"] = probas

    # --- Вывод
    table = X_gp[["driver", "team", "quali_position", "win_proba"]]
    table = table.sort_values("win_proba", ascending=False)
    print("\n=== Вероятности победы ===")
    print(table.to_string(index=False))

def use_rf_predictor(year, round_num):
    # --- Загрузка модели
    model = joblib.load("model/f1_win_rf.pkl")
    print("📦 Модель загружена")

    # --- Получение входных данных
    X_gp = get_gp_input(year, round_num)

    # --- Предсказание
    probas = model.predict_proba(X_gp)[:, 1]
    X_gp["win_proba"] = probas

    # --- Вывод
    table = X_gp[["driver", "team", "quali_position", "win_proba"]]
    table = table.sort_values("win_proba", ascending=False)
    print("\n=== Вероятности победы ===")
    print(table.to_string(index=False))

def use_stacked_predictor(year, round):
    model_dict = joblib.load("model/stacked_rf_logreg.pkl")
    print("📦 Модель загружена")

    rf_models = model_dict["rf_models"]
    meta_model = model_dict["meta_model"]
    preprocessor = model_dict["preprocessor"]

    # Получаем данные
    X_gp = get_gp_input(year, round)

    # Препроцессинг
    X_proc = preprocessor.transform(X_gp)

    # Получаем вероятности от каждого леса
    meta_features = np.column_stack([
        rf.predict_proba(X_proc)[:, 1] for rf in rf_models
    ])

    # Предсказания финальной логистической модели
    probas = meta_model.predict_proba(meta_features)

    X_gp["win_proba"] = probas[:, 1]
    print(X_gp[["driver", "team", "win_proba"]].sort_values("win_proba", ascending=False))
