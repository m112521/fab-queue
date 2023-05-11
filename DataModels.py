from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class SessionItem(BaseModel):
    filename: str
    username: str
    duration: int
    machine: int


class QSession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    filename: str
    duration: int = None
    machine_id: int