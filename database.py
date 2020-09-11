from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session as ORMSession
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///temp.db')


def create_schema():
    Base.metadata.create_all(engine, checkfirst=True)


class Session:
    session = None

    def __init__(self) -> None:
        self.session_class = sessionmaker(bind=engine)

    def __enter__(self) -> ORMSession:
        self.session = self.session_class()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not exc_type:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()
        self.session = None