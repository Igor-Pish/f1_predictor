from DB_module.db_setup import *
from DB_module.loader import *
from db_visualizer.interactive_viewer import *
from model.data_collector import *
from model.train_model import *
from model.use_model import *

def db_manual_update():
    for year in range(2003, 2025):
        print(f"loading year {year}")
        load_races(year)
        for round in round_number_in_season(year):
            round_num = int(round["round"])
            load_quali_results(year, round_num)
            load_race_results(year, round_num)
            
if __name__ == "__main__":
    #print(is_table_empty(Race))
    #print(len(round_number_in_season(2022)) + len(round_number_in_season(2023)) + len(round_number_in_season(2024)))
    years = range(2003, 2025)
    df = collect_all_data(years)
    print(len(df[df.isna().any(axis=1)]))
    print(len(df))
    train_stacked_predictor(years)