from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'weather_app.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

