from DB_module.db_setup import SessionLocal
from DB_module.tables import *
from fastf1 import get_session, events
import pandas as pd
import requests

def to_seconds(time_str):
    if not time_str:
        return None
    if ":" in time_str:
        m, s = time_str.split(":")
        return int(m) * 60 + float(s)
    return float(time_str)
    
def load_races(year: int):
    session = SessionLocal()
    rounds = round_number_in_season(year)

    try:
        for round_data in rounds:
            round_num = int(round_data["round"])
            url = f"http://ergast.com/api/f1/{year}/{round_num}/results.json"
            r = requests.get(url)
            if r.status_code != 200:
                continue
            data = r.json()
            races = data["MRData"]["RaceTable"]["Races"]
            if not races:
                break

            race = races[0]
            results = race["Results"]
            driver_info = results[0]["Driver"]
            driver = driver_info.get("code") or driver_info["driverId"]
            winner = driver
            team = results[0]["Constructor"]["name"]
            winner_best = None
            fastest_driver = None
            best_time = 9999.0

            for result in results:
                if "FastestLap" in result:
                    lap_time = to_seconds(result["FastestLap"]["Time"]["time"])
                    if result["position"] == "1":
                        winner_best = lap_time
                    if lap_time < best_time:
                        best_time = lap_time
                        driver_info = result["Driver"]
                        driver = driver_info.get("code") or driver_info["driverId"]
                        fastest_driver = driver

            session.merge(Race(
                year=year,
                round=round_num,
                country=race["Circuit"]["Location"]["country"],
                track=race["Circuit"]["circuitName"],
                winner=winner,
                winner_best_lap=winner_best,
                fastest_lap_time=best_time,
                fastest_driver=fastest_driver,
                winning_team=team
            ))
        session.commit()
        print(f"✅ Races of year {year} downloaded.")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при загрузке races: {e}")
    finally:
        session.close()

def load_quali_results(year: int, round_num: int):
    session = SessionLocal()
    try:
        url = f"http://ergast.com/api/f1/{year}/{round_num}/qualifying.json"
        r = requests.get(url)
        if r.status_code != 200:
            return
        data = r.json()
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return

        for result in races[0]["QualifyingResults"]:
            driver_info = result["Driver"]
            driver = driver_info.get("code") or driver_info["driverId"]
            session.merge(QualifyingResult(
                year=year,
                round=round_num,
                driver=driver,
                q1=to_seconds(result.get("Q1")),
                q2=to_seconds(result.get("Q2")),
                q3=to_seconds(result.get("Q3")),
                position=int(result["position"])
            ))

        session.commit()
        print(f"✅ Quali results for round {round_num} of year {year} downloaded.")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при загрузке quali_results: {e}")
    finally:
        session.close()

def load_race_results(year: int, round_num: int):
    session = SessionLocal()
    try:
        race_url = f"http://ergast.com/api/f1/{year}/{round_num}/results.json"
        pits_url = f"http://ergast.com/api/f1/{year}/{round_num}/pitstops.json?limit=100"

        r1 = requests.get(race_url)
        r2 = requests.get(pits_url)
        if r1.status_code != 200 or r2.status_code != 200:
            return

        race_data = r1.json()
        pits_data = r2.json()

        races = race_data["MRData"]["RaceTable"]["Races"]
        if not races:
            return

        race = races[0]
        track = race["Circuit"]["circuitName"]
        country = race["Circuit"]["Location"]["country"]
        results = race["Results"]

        pit_counts = {}
        pit_races = pits_data["MRData"]["RaceTable"]["Races"]
        if pit_races:
            for pit in pit_races[0]["PitStops"]:
                code = pit["driverId"].upper()
                pit_counts[code] = pit_counts.get(code, 0) + 1

        best_lap = None
        best_driver = None
        for r in results:
            if "FastestLap" in r:
                t = to_seconds(r["FastestLap"]["Time"]["time"])
                if best_lap is None or (t is not None and t < best_lap):
                    best_lap = t
                    driver_info = r["Driver"]
                    driver = driver_info.get("code") or driver_info["driverId"]
                    best_driver = driver

        for r in results:
            driver_info = r["Driver"]
            driver = driver_info.get("code") or driver_info["driverId"]
            team = r["Constructor"]["name"]
            position = int(r["position"])
            lap_time = None
            if "FastestLap" in r:
                lap_time = to_seconds(r["FastestLap"]["Time"]["time"])
            pits = pit_counts.get(driver.lower(), 0)
            has_fastest = 1 if driver == best_driver else 0

            session.merge(RaceResult(
                year=year,
                round=round_num,
                country=country,
                track=track,
                position=position,
                driver=driver,
                best_lap_time=lap_time,
                pitstops=pits,
                team=team,
                has_fastest_lap=has_fastest
            ))

        session.commit()
        print(f"✅ Race results for round {round_num} of year {year} downloaded.")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при загрузке race_results: {e}")
    finally:
        session.close()

def load_quali_results_fastf1(year: int, round_num: int):
    session = get_session(year, round_num, 'Q')
    session.load(telemetry=False, weather=False, messages=False)

    results = session.results
    if results is None or results.empty:
        print(f"⚠️ Нет результатов квалификации за {year}/{round_num} в FastF1")
        return

    results = results.reset_index()

    session_db = SessionLocal()
    try:
        for _, row in results.iterrows():
            drv = row["Abbreviation"]
            q1 = row.get("Q1", None)
            q2 = row.get("Q2", None)
            q3 = row.get("Q3", None)
            pos = int(row["Position"])

            def to_seconds(t):
                if pd.isna(t): return None
                if isinstance(t, pd.Timedelta):
                    return t.total_seconds()
                return float(t)

            session_db.merge(QualifyingResult(
                year=year,
                round=round_num,
                driver=drv,
                q1=to_seconds(q1),
                q2=to_seconds(q2),
                q3=to_seconds(q3),
                position=pos
            ))

        session_db.commit()
        print(f"✅ FastF1: квалификация {year}/{round_num} загружена")
    except Exception as e:
        session_db.rollback()
        print(f"❌ Ошибка при записи квалификации FastF1: {e}")
    finally:
        session_db.close()

def load_race_results_fastf1(year: int, round_num: int):
    session = get_session(year, round_num, 'R')
    session.load(telemetry=False, weather=False, messages=False)

    results = session.results
    if results is None or results.empty:
        print(f"⚠️ Нет результатов гонки за {year}/{round_num} в FastF1")
        return

    results = results.reset_index()

    # Найдём гонщика с самым быстрым кругом
    best_lap_time = None
    best_driver = None
    for _, row in results.iterrows():
        lap_time = row.get("FastestLapTime")
        if pd.notna(lap_time):
            lap_time_sec = lap_time.total_seconds()
            if best_lap_time is None or lap_time_sec < best_lap_time:
                best_lap_time = lap_time_sec
                best_driver = row["Abbreviation"]

    db = SessionLocal()
    try:
        for _, row in results.iterrows():
            driver = row["Abbreviation"]
            team = row["TeamName"]
            pos = int(row["Position"])
            lap_time = row.get("FastestLapTime")
            lap_time = lap_time.total_seconds() if pd.notna(lap_time) else None
            pit_stops = row.get("NumberOfPitStops", 0)
            has_fastest = 1 if driver == best_driver else 0

            db.merge(RaceResult(
                year=year,
                round=round_num,
                country=session.event['Country'],
                track=session.event['Location'],
                position=pos,
                driver=driver,
                best_lap_time=lap_time,
                pitstops=pit_stops,
                team=team,
                has_fastest_lap=has_fastest
            ))

        db.commit()
        print(f"✅ FastF1: результаты гонки {year}/{round_num} загружены")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при записи гонки FastF1: {e}")
    finally:
        db.close()

def round_number_in_season(year):
    url = f"http://ergast.com/api/f1/{year}.json"
    response = requests.get(url)
    data = response.json()
    races = data['MRData']['RaceTable']['Races']
    return races

def round_number_in_season_fastf1(year):
    try:
        calendar = events.get_event_schedule(year)
        rounds = calendar["RoundNumber"].tolist()
        return rounds
    except Exception as e:
        print(f"❌ Ошибка при получении расписания FastF1 за {year}: {e}")
        return []
    
def update_table(table_name, year):
    match table_name:
        case "races":
            load_races(year)
        case "quali_results":
            for race in round_number_in_season(year):
                round_num = int(race["round"])
                load_quali_results(year, round_num)
        case "race_results":
            for race in round_number_in_season(year):
                round_num = int(race["round"])
                load_race_results(year, round_num)
