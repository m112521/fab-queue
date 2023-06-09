from datetime import datetime, timedelta
from typing import Union, Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

from fastapi.middleware.cors import CORSMiddleware
from QSession import QueueSession
from DataModels import SessionItem, QSession, QUser, QMachine, UserInDB, Token, TokenData, User
from sqlmodel import Field, Session, SQLModel, create_engine, select

# TBD
# 1. Auth
# 2. DEL, UPD

SECRET_KEY = "cc63bf05b567447d1abf75c88033c953e9ba1a04b95b85417c13ad4a7f2bb4de"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


@app.post("/add-session-related")
async def add_related_db(item: QSession):
    with Session(engine) as session:
        qu = QUser(username="Peter", fullname="Rojer", year="2")
        qm = QMachine(name="PRUSA", workarea="200x200x200")
        qs = QSession(filename=item.filename, duration=item.duration, start=item.start, quser=qu, qmachine=qm) # start=datetime.now()

        session.add(qs)
        session.commit()

    return item


@app.get("/all")
async def get_all_sessions():
    json_sessions = []
    with Session(engine) as session:
        sessions = session.exec(select(QSession)) 
        json_sessions = [{"username": s.user_id, "filename": s.filename, "duration": s.duration, "machine_id": s.machine_id} for s in sessions]

    print(json_sessions)
    return json_sessions


@app.get("/select-by-machine/{machine_id}")
async def get_sessions_by_machine(machine_id: int):
    json_sessions = []
    with Session(engine) as session:
        statement = select(QSession).where(QSession.machine_id == machine_id)
        sessions = session.exec(statement)
        json_sessions = [{"username": s.quser.username, "filename": s.filename, "duration": s.duration, "machine": s.qmachine.name} for s in sessions]

    return json_sessions


@app.get("/delete/{id}")
async def delete_item(id: int):
    with Session(engine) as session:
        statement = select(QSession).where(QSession.id == id)
        results = session.exec(statement)
        item = results.one()
        #print("Item deleted: ", item)

        session.delete(item)
        session.commit()


# auth

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: Annotated[User, Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]

