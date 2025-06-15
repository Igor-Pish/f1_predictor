import pandas as pd
from DB_module.tables import Race, QualifyingResult, RaceResult
from sqlalchemy import inspect
from DB_module.db_setup import *

TABLE_CLASSES = {
    "races": Race,
    "qualifying_results": QualifyingResult,
    "race_results": RaceResult
}

# --- Проверка таблиц ---
def get_available_tables():
    inspector = inspect(engine)
    return inspector.get_table_names()

# --- Пустая таблица? ---
def is_table_empty(table_name):
    table_cls = TABLE_CLASSES[table_name]
    with SessionLocal() as session:
        return session.query(table_cls).count() == 0

def get_races_by_year(year: int):
    with SessionLocal() as session:
        return session.query(Race).filter(Race.year == year).order_by(Race.round).all()
    
def get_race_result_by_year_and_round(year, round_number):
    with SessionLocal() as session:
        results = session.query(RaceResult).filter_by(year=year, round=round_number).all()
        return results

def get_race_results(year=None, round_num=None, driver=None):
    with SessionLocal() as session:
        query = session.query(RaceResult)
        if year:
            query = query.filter(RaceResult.year == year)
        if round_num:
            query = query.filter(RaceResult.round == round_num)
        if driver:
            query = query.filter(RaceResult.driver == driver)

        rows = query.all()
        df = pd.DataFrame([r.__dict__ for r in rows])
        if "_sa_instance_state" in df.columns:
            df = df.drop(columns="_sa_instance_state")
        return df[[
            "year", "round", "country", "track", "position",
            "driver" , "team", "best_lap_time", "pitstops", "has_fastest_lap"
        ]]

def get_quali_results(year=None, round_num=None, driver=None):
    with SessionLocal() as session:
        query = session.query(QualifyingResult)
        if year:
            query = query.filter(QualifyingResult.year == year)
        if round_num:
            query = query.filter(QualifyingResult.round == round_num)
        if driver:
            query = query.filter(QualifyingResult.driver == driver)

        rows = query.all()
        df = pd.DataFrame([r.__dict__ for r in rows])
        if "_sa_instance_state" in df.columns:
            df = df.drop(columns="_sa_instance_state")
        return df[["year", "round", "driver", "q1", "q2", "q3", "position"]]


def get_races(year=None, round_num=None):
    with SessionLocal() as session:
        query = session.query(Race)
        if year:
            query = query.filter(Race.year == year)
        if round_num:
            query = query.filter(Race.round == round_num)

        rows = query.all()
        df = pd.DataFrame([r.__dict__ for r in rows])
        if "_sa_instance_state" in df.columns:
            df = df.drop(columns="_sa_instance_state")
        return df[[
            "year", "round", "country", "track", "winner", "winning_team",
            "winner_best_lap", "fastest_lap_time", "fastest_driver"
        ]]
