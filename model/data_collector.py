import pandas as pd
from DB_module.getter import get_quali_results, get_race_results
from DB_module.loader import *

def build_gp_dataset(year, round_num):
    quali_df = get_quali_results(year=year, round_num=round_num)
    race_df = get_race_results(year=year, round_num=round_num)

    if quali_df.empty or race_df.empty:
        print(f"⚠️ Пропуск: нет данных за {year} / {round_num}")
        return None
    
    quali_df["q1"] = quali_df["q1"].astype(float)
    quali_df["q2"] = quali_df["q2"].astype(float)
    quali_df["q3"] = quali_df["q3"].astype(float)

    quali_df["q2"] = quali_df["q2"].fillna(quali_df["q1"])
    quali_df["q3"] = quali_df["q3"].fillna(quali_df["q2"])
    quali_df["q1"] = quali_df.apply(lambda row: max([row["q2"], row["q3"]]) if pd.isna(row["q1"]) and pd.notna(row["q2"]) and pd.notna(row["q3"]) else row["q1"], axis=1)

    # нормализация по минимальному времени
    for q in ["q1", "q2", "q3"]:
        best = quali_df[q].min()
        quali_df[f"{q}_norm"] = quali_df[q] / best

    merged = pd.merge(quali_df, race_df, how="inner", on=["year", "round", "driver"])
    merged["target"] = merged["position_y"].apply(lambda pos: 1 if pos == 1 else 0)
    merged = merged[[
        "year", "round", "driver", "team",
        "q1_norm", "q2_norm", "q3_norm",
        "position_x", "target"
    ]]
    merged.rename(columns={"position_x": "quali_position"}, inplace=True)
    merged = merged.dropna()
    return merged

def collect_all_data(years: list[int]):
    all_rows = []

    for year in years:
        print(f"Собираю {year}...")
        rounds = round_number_in_season(year)

        for r in rounds:
            round_num = int(r["round"])
            df = build_gp_dataset(year, round_num)
            if df is not None:
                all_rows.append(df)

    if not all_rows:
        print("❌ Нет данных.")
        return None

    return pd.concat(all_rows, ignore_index=True)

def get_gp_input(year, round_num):
    quali_df = get_quali_results(year=year, round_num=round_num)

    if quali_df.empty:
        print(f"⚠️ Нет квалификационных данных за {year} / {round_num}")
        return None

    quali_df["q1"] = quali_df["q1"].astype(float)
    quali_df["q2"] = quali_df["q2"].astype(float)
    quali_df["q3"] = quali_df["q3"].astype(float)

    quali_df["q2"] = quali_df["q2"].fillna(quali_df["q1"])
    quali_df["q3"] = quali_df["q3"].fillna(quali_df["q2"])
    quali_df["q1"] = quali_df.apply(lambda row: max([row["q2"], row["q3"]]) if pd.isna(row["q1"]) and pd.notna(row["q2"]) and pd.notna(row["q3"]) else row["q1"], axis=1)

    # нормализация по минимальному времени
    for q in ["q1", "q2", "q3"]:
        best = quali_df[q].min()
        quali_df[f"{q}_norm"] = quali_df[q] / best

    # Добавим заглушку на команду — если нужно, подставь реальную
    driver_team_map = {
        "VER": "Red Bull",
        "TSU": "Red Bull",
        "LEC": "Ferrari",
        "HAM": "Ferrari",
        "NOR": "McLaren",
        "PIA": "McLaren",
        "SAI": "Williams",
        "ALB": "Williams",
        "RUS": "Mercedes",
        "ANT": "Mercedes",
        "ALO": "Aston Martin",
        "STR": "Aston Martin",
        "OCO": "Haas",
        "BER": "Haas",
        "COL": "Alpine",
        "GAS": "Alpine",
        "BOR": "Sauber",
        "HUL": "Sauber",
        "HAD": "RB",
        "LAW": "RB",
    }
    team_df = pd.DataFrame(driver_team_map.items(), columns=["driver", "team"])
    merged = pd.merge(quali_df, team_df, on="driver", how="left")
    merged = merged.dropna()

    X = merged[[
        "driver", "team", "q1_norm", "q2_norm", "q3_norm", "position"
    ]].rename(columns={"position": "quali_position"})

    return X