from typing import List, Callable

from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

import configparser


import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
import aiofiles
# import os
import urllib


conf = configparser.ConfigParser()
conf.read('config.ini')
server = conf["SERVER"]
userinf = conf["USERINFO"]


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = server["ORIGIN"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index():
    return {"message": "FinPlat API helped financial planners made millions!"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/email/{user_email}", response_model=schemas.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_user


@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}


@app.get("/upload/")
async def upload():
    content = """
<body>
<form action="""+server["API_URL"]+"""/files/ enctype="multipart/form-data" method="post">files
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="""+server["API_URL"]+"""/uploadfiles/ enctype="multipart/form-data" method="post">uploadfiles
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="""+server["API_URL"]+"""/endpoint1/ enctype="multipart/form-data" method="post">endpoint1
<input name="in_file" type="file" accept="image/png">
<input type="submit">
</form>
<form action="""+server["API_URL"]+"""/endpoint2/ enctype="multipart/form-data" method="post">endpoint2
<input name="in_file" type="file" accept="image/*">
<input type="submit">
</form>
<form action="""+server["API_URL"]+"""/endpoint3/ enctype="multipart/form-data" method="post">endpoint3
<input name="in_file" type="file" multiple accept="image/*">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/endpoint1/")
async def post_endpoint1(in_file: UploadFile = File(...)):
    # ...
    async with aiofiles.open(server["FILE_PATH"]+in_file.filename, 'wb') as out_file:
        content = await in_file.read()  # async read
        await out_file.write(content)  # async write

    return {"Result": "OK"}


@app.post("/endpoint2/")
async def post_endpoint2(in_file: UploadFile = File(...)):
    # ...
    async with aiofiles.open(server["FILE_PATH"]+in_file.filename, 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return {"Result": "OK"}


@app.post("/endpoint3/")
async def post_endpoint3(in_file: List[UploadFile] = File(...)):

    for file in in_file:
        async with aiofiles.open(server["FILE_PATH"]+file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    return {"filenames": [file.filename for file in in_file]}


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path


def handle_upload_file(
    upload_file: UploadFile, handler: Callable[[Path], None]
) -> None:
    tmp_path = save_upload_file_tmp(upload_file)
    try:
        handler(tmp_path)  # Do something with the saved temp file
    finally:
        tmp_path.unlink()  # Delete the temp file
