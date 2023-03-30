from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jarvis_db.db_config import Base


class DbContext:
    def __init__(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.session = session
