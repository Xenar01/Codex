"""SQLAlchemy setup for SQLite/MySQL/PostgreSQL"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///realestate.db')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
