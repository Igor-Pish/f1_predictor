from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DB_module.tables import Base

# Путь к БД
DB_PATH = "sqlite:///f1_database.db"

# Создание движка и сессии
engine = create_engine(DB_PATH, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

# Функция создания БД
def create_database():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных создана")