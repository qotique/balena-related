import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataBase:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    @contextmanager
    def session(self):
        session = self.session_factory()
        try:
            yield session
        except BaseException as error:
            session.rollback()
            logging.error(error)
        finally:
            session.close()
