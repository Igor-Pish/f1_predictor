# F1 Race Winner Predictor

This project builds a machine learning pipeline to predict the winner of an upcoming Formula 1 race using practice and qualification data.

It demonstrates end-to-end skills in data collection, feature engineering, model training, and performance evaluation — with a focus on real-world sports analytics.

---

## The Goal

To predict the **race winner** before the Grand Prix starts, based on:

- Free Practice 1, 2, and 3 results
- Qualifying session outcomes
- Historical driver and constructor performance

---

## Stack and Tools

- **Python**, **scikit-learn**, **pandas**, **numpy**
- **FastF1** & **Ergast API** — data sources
- **SQLite** — for structured race data storage
- **XGBoost** — main classification model
- **Matplotlib** — for performance visualization

---

## Key ML Steps

1. **Data Collection**
   - Parsed race sessions from FastF1 (2021–2025)
   - Supplemented historical data from Ergast API

2. **Feature Engineering**
   - Combined practice times, qualifying results, and track metadata
   - Created per-driver datasets per race

3. **Modeling**
   - Trained **XGBoost classifier** to predict the winning driver
   - Used **recall**, **F1-score**, and **top-k accuracy** as evaluation metrics

4. **Evaluation**
   - Tested on recent races
   - Currently being tuned for generalizability across circuits

---

## Example Use

python
from predictor import predict_race
predict_race(year=2024, round=5)
