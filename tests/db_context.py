from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from jarvis_db.db_config import Base


class DbContext:
    def __init__(self, connection_sting: str = "sqlite://", echo: bool = False) -> None:
        if connection_sting.startswith("sqlite://"):

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        engine = create_engine(connection_sting, echo=echo)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session = session


def enable_sqlalchemy_logging():
    import logging

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
