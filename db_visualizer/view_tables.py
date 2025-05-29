from DB_module.getter import *
from DB_module.loader import *

def preview_table(table_name, **filters):
    if is_table_empty(table_name):
        print('The table is empty')
        choice = input('Do you want to upload data to this table? (Y/N)')
        match choice:
            case 'y':
                year = int(input("Введите год\n"))
                update_table(table_name, year)
            case 'n':
                raise ValueError(f"Таблица {table_name} пуста.")
            case _:
                print("Unsupported input")
    else:
        match table_name:
            case "quali_results":
                return get_quali_results(**filters)
            case "race_results":
                return get_race_results(**filters)
            case "races":
                return get_races(**filters)
            case _:
                raise ValueError(f"Таблица {table_name} не поддерживается.")
