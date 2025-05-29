from db_visualizer.view_tables import preview_table
from DB_module.getter import *
from DB_module.db_setup import create_database

FILTERS_BY_TABLE = {
    "races": ["year", "round_number"],
    "drivers": [],
    "practice_sessions": ["year", "round_number", "driver_id", "session"],
    "qualifying_results": ["year", "round_number", "driver_id"],
    "race_results": ["year", "round_number", "driver_id"],
    "sprint_results": ["year", "round_number", "driver_id"],
    "sprint_qualifying_results": ["year", "round_number", "driver_id", "session"],
}

def run_menu():
    while True:
        tables = get_available_tables()
        if tables:
            print("\n=== Доступные таблицы ===")
            for idx, t in enumerate(tables, 1):
                print(f"{idx}. {t}")
            print("0. Выход")

            choice = input("\nВыбери таблицу (номер или 0 для выхода): ")
            if choice == '0':
                print("Выход из программы.")
                break

            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(tables):
                print("Некорректный ввод, попробуй снова.")
                continue

            table_name = tables[int(choice) - 1]
            print(preview_table(table_name))
        else:
            print('No available tables.')
            choice = input("\nDo you want to crate a data base? (Y/N)\n").lower()
            match choice:
                case 'y':
                    print("Creating a database f1_database.db")
                    create_database()
                case 'n':
                    print('Ending program')
                    break
                case _:
                    print("Unsupported input")