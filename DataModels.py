from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship
from typing import Union, List, Optional


class SessionItem(BaseModel):
    filename: str
    username: str
    duration: int
    machine: int


class QSession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    filename: str
    duration: int 
    start: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="quser.id")
    machine_id: Optional[int] = Field(default=None, foreign_key="qmachine.id")

    quser: Union["QUser", None] = Relationship(back_populates="qsession", sa_relationship_kwargs={'uselist': False})
    qmachine: Union["QMachine", None] = Relationship(back_populates="qsession", sa_relationship_kwargs={'uselist': False})


class QUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    fullname: str
    year: int = Field(default=None)

    qsession: Union[QSession, None] = Relationship(back_populates="quser")
    

class QMachine(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    workarea: str

    qsession: Union[QSession, None] = Relationship(back_populates="qmachine")
