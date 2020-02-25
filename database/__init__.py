from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData

from config import Config

engine: Engine = create_engine(Config.URI_DB, echo=False)
metadata: MetaData = MetaData(bind=engine)
Base: DeclarativeMeta = declarative_base(metadata=metadata)
Session: Session = sessionmaker(bind=engine)


def create_db():
    metadata.create_all(engine)


create_db()
