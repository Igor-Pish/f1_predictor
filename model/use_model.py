import joblib
from model.data_collector import get_gp_input

def use_predictor(year, round):
    model = joblib.load("model/f1_win_predictor.pkl")
    print("📦 Модель загружена")

    X_gp = get_gp_input(year, round)
    probas = model.predict_proba(X_gp)

    X_gp["win_proba"] = probas[:, 1]
    print(X_gp[["driver", "team", "win_proba"]].sort_values("win_proba", ascending=False))
