from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite://")
session = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass
