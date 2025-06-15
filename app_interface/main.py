import sys
import os

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
from DB_module.getter import *
from DB_module.loader import *

# Настройка Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    years = list(range(2003, 2025))

    selected_year = None
    selected_race_round = None
    races = []
    race_results = []
    if request.method == "POST":
        
        selected_year = int(request.form.get("year"))
        selected_race_round = request.form.get("race")
        races = get_races_by_year(selected_year)

        if selected_year and selected_race_round:
            race_results = get_race_result_by_year_and_round(
                selected_year, int(selected_race_round)
            )

    return render_template("index.html",
                           years=years,
                           selected_year=selected_year,
                           selected_race_round=selected_race_round,
                           races=races,
                           race_results=race_results)

if __name__ == "__main__":
    app.run(debug=True)
