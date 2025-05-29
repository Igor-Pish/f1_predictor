import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, KFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.base import clone
import joblib

from model.data_collector import collect_all_data

def train_stacked_predictor(years, model_path="model/stacked_rf_logreg.pkl"):
    # --- Загружаем и делим
    df = collect_all_data(years)
    X = df[["q1_norm", "q2_norm", "q3_norm", "quali_position", "driver", "team"]]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # --- Препроцессинг
    numeric = ["q1_norm", "q2_norm", "q3_norm", "quali_position"]
    categorical = ["driver", "team"]

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
    ])

    prep = preprocessor.fit(X_train)

    # --- K-фолдов и леса
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    rf_base = RandomForestClassifier(n_estimators=500, random_state=42)
    rf_models = []

    meta_train = np.zeros((len(X_train), 10))

    for i, (train_idx, val_idx) in enumerate(kf.split(X_train)):
        X_fold_train = prep.transform(X_train.iloc[train_idx])
        y_fold_train = y_train.iloc[train_idx]
        X_fold_val = prep.transform(X_train.iloc[val_idx])

        rf = clone(rf_base)
        rf.fit(X_fold_train, y_fold_train)
        rf_models.append(rf)
        meta_train[val_idx, i] = rf.predict_proba(X_fold_val)[:, 1]

    # --- Обучаем логрег
    meta_model = LogisticRegression(random_state=42)
    meta_model.fit(meta_train, y_train)

    # --- Сохраняем модель
    joblib.dump({
        "rf_models": rf_models,
        "meta_model": meta_model,
        "preprocessor": prep
    }, model_path)

    # --- Тестовая часть
    X_test_proc = prep.transform(X_test)
    meta_test = np.column_stack([
        rf.predict_proba(X_test_proc)[:, 1] for rf in rf_models
    ])
    y_pred = meta_model.predict(meta_test)
    y_proba = meta_model.predict_proba(meta_test)[:, 1]

    print("✅ Модель обучена и сохранена")

    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred))

    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    print("=== ROC AUC Score ===")
    print(roc_auc_score(y_test, y_proba))
