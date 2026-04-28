from sqlalchemy import Engine
from typing import Any, Generator

from sqlmodel import create_engine, SQLModel, Session
from .models import *

sqlite_file_name = "opsai.db"
sqlite_url: str = f"sqlite:///{sqlite_file_name}"

connect_args: dict[str, bool] = {"check_same_thread": False}
engine: Engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
           yield session
