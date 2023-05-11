from typing import Union
from fastapi import FastAPI
import json

from fastapi.middleware.cors import CORSMiddleware
from QSession import QueueSession
from DataModels import SessionItem, QSession
from sqlmodel import Field, Session, SQLModel, create_engine, select

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

app = FastAPI()
# Text file I/O: txt, json

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/last-session/")
def get_last_session():
    return f"Test"


@app.get("/current-session/{machine_id}")
def get_current_session(machine_id: int):
    qs = QueueSession("test.gcode", "Andrew", 120, 0)
    return json.dumps(qs.__dict__)


@app.post("/add-session-txt")
async def add_session(item: SessionItem):
    with open('workfile.txt', 'a', encoding="utf-8") as f:
        #json.dump(item.json() + "\n", f) #json.load(f) 
        f.write(f"{item.filename},{item.duration},{item.username},{item.machine}\n")
    
    with open('workfile.txt', 'r', encoding="utf-8") as f:
        #print(json.load(f)) # item.dict()
        lst = f.readlines()
        print(lst)
        
    return item


@app.post("/add-session-db")
async def add_to_db(item: SessionItem):
    qs = QSession(username=item.username, filename=item.filename, duration=item.duration, machine_id = item.machine)
    
    with Session(engine) as session:
        session.add(qs)
        session.commit()

    return item


@app.get("/all")
async def get_all_sessions():
    json_sessions = []
    with Session(engine) as session:
        sessions = session.exec(select(QSession)) 
        json_sessions = [{"username": s.username, "filename": s.filename, "duration": s.duration, "machine_id": s.machine_id} for s in sessions]

    print(json_sessions)
    return json_sessions