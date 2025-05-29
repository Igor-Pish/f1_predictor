from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    round = Column(Integer)
    country = Column(String)
    track = Column(String)
    winner = Column(String)
    winner_best_lap = Column(Float)
    fastest_lap_time = Column(Float)
    fastest_driver = Column(String)
    winning_team = Column(String)

class QualifyingResult(Base):
    __tablename__ = "quali_results"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    round = Column(Integer)
    driver = Column(String)
    q1 = Column(Float)
    q2 = Column(Float)
    q3 = Column(Float)
    position = Column(Integer)

class RaceResult(Base):
    __tablename__ = "race_results"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    round = Column(Integer)
    country = Column(String)
    track = Column(String)
    position = Column(Integer)
    driver = Column(String)
    best_lap_time = Column(Float)
    pitstops = Column(Integer)
    team = Column(String)
    has_fastest_lap = Column(Integer)  # 0 или 1, bool через int