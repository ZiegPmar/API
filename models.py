from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(255), nullable=False)
    heure = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
