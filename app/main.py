import time
import asyncio
import httpx

from fastapi import Depends, BackgroundTasks, FastAPI, HTTPException, WebSocket, Query
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app import crud, schemas


Base.metadata.create_all(bind = engine)
app = FastAPI()


"""
BASIC USAGE
Params and query params
"""


@app.get("/", tags=["Basic usage"])
def index():
    return {"message": "Hello World"}


@app.get("/place/{place}/", tags=["Basic usage"])
def place(place: str):
    return {"message": f"Hello {place}"}


@app.get("/weather/{place}/", tags=["Basic usage"])
def weather(place: str, rain: bool = False):
    if rain:
        return {"Hello": f"Hello {place}, today is a rainy day"}
    return {"Hello": f"Hello {place}, today is a sunny day"}


"""
EXTRA DOCS?
It allows md in the docstrings
"""

@app.get("/custom", tags=["Docs"])
def custom_docs(days: int = Query(default=1, gt=0, le=10, description="Number of days")):
    """
    ### Return the following info:

    - **message**: a message to say hello world
    
    ### This allow md
    - *Line 1*: Lorem ipsum dolor sit amet, consectetur adipisicing elit, 
    - **Line 2**: sed do eiusmod tempor incididunt ut labore et dolore 
    - *Line 3*: magna aliqua. Ut enim ad minim veniam.
    """
    return {"message": "Hello World"}


"""
USING DATABASES
SqlAlchemy
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User, tags=['Users'])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User], tags=['Users'])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, tags=['Users'])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/pets/", response_model=list[schemas.Pet], tags=['Pets'])
def read_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pets = crud.get_pets(db, skip=skip, limit=limit)
    return pets


@app.post("/users/{user_id}/pets/", response_model=schemas.Pet, tags=['Pets'])
def create_user_pet(user_id: int, pet: schemas.PetCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_user_pet(db=db, pet=pet, user_id=user_id)


""" 
ASYNC AND AWAIT?
Sure 
"""


@app.get("/waiting/", tags=['Async'])
async def get_resource():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://httpstat.us/201?sleep=5000", timeout=None)
        return {'status_code': response.status_code}


async def make_request(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=None)
        return response


@app.get("/sleep", tags=['Async'])
async def sleep_response(ms: int):
    urls = [
        f"https://httpstat.us/200?sleep={ms}",
        f"https://httpstat.us/200?sleep={ms}",
        f"https://httpstat.us/200?sleep={ms}"
    ]
    tasks = [make_request(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    return {'status_code': response.status_code}


"""
WEBSOCKETS

"""


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/chat", tags=['Sockets'])
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


def get_name_with_age(name: str, age: int):
    name_with_age = name + " is this old: " + age
    return name_with_age
    

"""
BACKGROUND TASKS

"""


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.get("/background/{email}", tags=['Background'])
async def background(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}