from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session

sqlite_filename = "db.sqlite"
connection_string = f"sqlite:///{sqlite_filename}"

connect_args = {"check_same_thread": False}
engine = create_engine(connection_string, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]