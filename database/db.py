from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedAsDataclass
from os import path


from utils.utils import LoggingCtxManager

module_dir = path.dirname(__file__)
path_to_db = f"{path.abspath(path.join(module_dir, '..', 'waga.db'))}"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{path_to_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False})

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase, MappedAsDataclass):
    ...


def configure_database() -> None:
    from models.forecast import Forecast
    """
    Creates the database tables according to
    the metadata found in the specified classes.

    Returns:
        None
    """
    with LoggingCtxManager():
        Forecast.metadata.create_all(bind=engine)

