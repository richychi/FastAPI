# import io
# import asyncio
import io
from typing import List, Callable

from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
# from fastapi.openapi.models import Response
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
# from starlette.requests import Request

from . import crud, models, schemas
from .database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

import configparser


import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
import aiofiles

from PIL import Image, ImageFont, ImageDraw

# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse


conf = configparser.ConfigParser()
conf.read('config.ini')
server = conf["SERVER"]
userinf = conf["USERINFO"]


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [server["API_URL"], server["ORIGIN"]]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception(BaseException) as e:
#
#         return Response("Internal server error", status_code=500)
#
# app.middleware('http')(catch_exceptions_middleware)


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


@app.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_title(db, title=category.title)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already existed")
    return crud.create_category(db=db, category=category)


@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@app.get("/categories/{category_id}", response_model=schemas.Category)
def read_category_by_id(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category id not found")
    return db_category


@app.get("/categories/title/{category_title}", response_model=schemas.Category)
def read_category_by_title(category_title: str, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_title(db, title=category_title)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category title not found")
    return db_category


@app.post("/presentations/", response_model=schemas.Presentation)
def create_presentation(presentation: schemas.PresentationCreate, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation_by_title(db, presentation_title=presentation.title)
    if db_presentation:
        raise HTTPException(status_code=400, detail="Presentation already existed")
    return crud.create_presentation(db=db, presentation=presentation)


# @app.post("/presentations/delete/", response_model=schemas.Presentation)
# def delete_presentation(presentation: schemas.PresentationCreate, db: Session = Depends(get_db)):
#     db_presentation = crud.get_presentation_by_title(db, presentation_title=presentation.title)
#     if db_presentation:
#         raise HTTPException(status_code=400, detail="Presentation already existed")
#     return crud.delete_presentation(db=db, presentation=presentation)


@app.get("/presentations/", response_model=List[schemas.Presentation])
def read_presentations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    presentations = crud.get_presentations(db, skip=skip, limit=limit)
    return presentations


@app.get("/presentations/{presentation_id}", response_model=schemas.Presentation)
def read_presentation_by_id(presentation_id: int, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation(db, presentation_id=presentation_id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation id not found")
    return db_presentation


@app.get("/presentations/title/{presentation_title}", response_model=schemas.Presentation)
def read_presentation_by_title(presentation_title: str, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation_by_title(db, presentation_title=presentation_title)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation title not found")
    return db_presentation


@app.post("/slides/", response_model=schemas.Slide)
def create_slide(slide: schemas.SlideCreate, db: Session = Depends(get_db)):
    db_slide = crud.get_slide_by_title(db, slide_title=slide.title, presentation_id=slide.presentation_id)
    if db_slide:
        raise HTTPException(status_code=400, detail="Slide already existed")
    db_slide = crud.create_slide(db=db, slide=slide)
    return db_slide


@app.get("/slides/", response_model=List[schemas.Slide])
def read_slides(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_slides = crud.get_slides(db, skip=skip, limit=limit)
    return db_slides


@app.get("/slides/slide_title/{slide_title}/{presentation_id}", response_model=schemas.Slide)
def read_slide_by_title(slide_title: str, presentation_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slide_by_title(db, slide_title=slide_title, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Slide title not found")
    return db_slide


@app.get("/slides/presentation_id/{presentation_id}", response_model=List[schemas.Slide])
def read_slides_by_presentation_id(presentation_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Presentation id not found")
    return db_slide


@app.post("/slideimage/")  # , response_model=schemas.SlideImage)
def create_slideImage(slideimage: schemas.SlideImageCreate, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slideimage.slide_id)
    if db_slideimage:
        raise HTTPException(status_code=400, detail="SlideImage already existed")
    db_slideimage = crud.create_slideimage(db=db, slideimage=slideimage)
    return db_slideimage


@app.get("/slideimages/")  # , response_model=List[schemas.SlideImage])
def read_slideimages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_slideimages = crud.get_slideimages(db, skip=skip, limit=limit)
    if not db_slideimages:
        raise HTTPException(status_code=404, detail="SlideImages not found")
    return db_slideimages  # HTMLResponse(db_slideimages.image, media_type="image/png")


@app.get("/slideimage/{slide_id}", response_model=schemas.SlideImage)
def read_slideimage(slide_id: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    return HTMLResponse(db_slideimage.image, media_type="image/png")  # db_slideimage


# @app.get("/slides/presentation_title/{presentation_title}", response_model=schemas.Slide)
# def read_slide_by_presentation_title(presentation_title: str, db: Session = Depends(get_db)):
#     db_slide = crud.get_slide_by_presentation_title(db, presentation_title=presentation_title)
#     if db_slide is None:
#         raise HTTPException(status_code=404, detail="Presentation title not found")
#     return db_slide


@app.post("/imagerenders/", response_model=schemas.ImageRender)
def create_imagerender(imagerender: schemas.ImageRenderCreate, db: Session = Depends(get_db)):
    db_imagerender = crud.get_imagerender_by_title(db, title=imagerender.title, slide_id=imagerender.slide_id)
    if db_imagerender:
        raise HTTPException(status_code=400, detail="ImageRender already existed")
    return crud.create_imagerender(db=db, imagerender=imagerender)


@app.get("/imagerenders/", response_model=List[schemas.ImageRender])
def read_imagerenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_imagerenders = crud.get_imagerenders(db, skip=skip, limit=limit)
    if db_imagerenders is None:
        raise HTTPException(status_code=404, detail="ImageRender not found")
    return db_imagerenders


@app.get("/imagerender/{slide_id}", response_model=schemas.ImageRender)
def read_imagerender_by_slideid(slide_id: int, db: Session = Depends(get_db)):
    db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
    if db_imagerender is None:
        raise HTTPException(status_code=404, detail="ImageRender by slide_id not found")
    return db_imagerender


@app.get("/imagerenders/title/{imagerender_title}/{imagerender_slideid}", response_model=schemas.ImageRender)
def read_imagerender_by_title(imagerender_title: str, imagerender_slideid: int, db: Session = Depends(get_db)):
    db_imagerender = crud.get_imagerender_by_title(db, title=imagerender_title, slide_id=imagerender_slideid)
    if db_imagerender is None:
        raise HTTPException(status_code=404, detail="ImageRender title not found")
    return db_imagerender


@app.post("/textrenders/", response_model=schemas.TextRender)
def create_textrender(textrender: schemas.TextRenderCreate, db: Session = Depends(get_db)):
    db_txtrender = crud.get_textrender_by_title(db, title=textrender.title, slide_id=textrender.slide_id)
    if db_txtrender:
        raise HTTPException(status_code=400, detail="TextRender already existed")
    return crud.create_textrender(db=db, textrender=textrender)


@app.get("/textrenders/", response_model=List[schemas.TextRender])
def read_textrenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_textrenders = crud.get_textrenders(db, skip=skip, limit=limit)
    return db_textrenders


@app.get("/textrender/{slide_id}", response_model=schemas.TextRender)
def read_textrender_by_slideid(slide_id: int, db: Session = Depends(get_db)):
    db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
    if db_textrender is None:
        raise HTTPException(status_code=404, detail="TextRender by slide_id not found")
    return db_textrender


@app.get("/textrenders/title/{textrender_title}/{textrender_slideid}", response_model=schemas.TextRender)
def read_textrender_by_title(textrender_title: str, textrender_slideid: int, db: Session = Depends(get_db)):
    db_textrender = crud.get_textrender_by_title(db, title=textrender_title, slide_id=textrender_slideid)
    if db_textrender is None:
        raise HTTPException(status_code=404, detail="TextRender title not found")
    return db_textrender


@app.get("/drawslide/{slide_id}")
async def draw_slide(slide_id: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    draw = ImageDraw.Draw(newslideimage)
    db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
    if db_textrender is None:
        raise HTTPException(status_code=404, detail="Textrender not found")
    fnt = ImageFont.truetype("./api/presentation/images/"+db_textrender.font, db_textrender.size)
    draw.text(xy=(db_textrender.pos_x, db_textrender.pos_y), text=db_textrender.text, align=db_textrender.align,
              anchor=db_textrender.anchor, font=fnt, fill=(db_textrender.color_r, db_textrender.color_g,
                                                           db_textrender.color_b))
    # newslideimage.show()
    db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
    if db_imagerender is None:
        raise HTTPException(status_code=404, detail="ImageRender by slide_id not found")
    logo = Image.open("./api/presentation/images/IMT-Logo.png")
    logo = logo.resize((db_imagerender.width, db_imagerender.height))
    newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y), logo)

    newslideimage.save("./api/presentation/images/"+str(slide_id)+".png")
    return FileResponse("./api/presentation/images/"+str(slide_id)+".png")   # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/testdrawslide/{slide_id}/{text}/{font_name}/{font_size}/{text_x}/{text_y}/{color_r}/{color_g}/{color_b}"
         "/{image_x}/{image_y}/{image_width}/{image_height}")
async def testdraw_slide(slide_id: int, text: str, font_name: str, font_size: int, text_x: int, text_y: int,
                         color_r: int, color_g: int, color_b: int, image_x: int, image_y: int, image_width: int,
                         image_height: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    draw = ImageDraw.Draw(newslideimage)
    fnt = ImageFont.truetype("./api/presentation/images/" + font_name, font_size)
    draw.text(xy=(text_x, text_y), text=text, align='left', anchor='la', font=fnt, fill=(color_r, color_g, color_b))
    # newslideimage.show()
    logo = Image.open("./api/presentation/images/IMT-Logo.png")
    logo = logo.resize((image_width, image_height))
    newslideimage.paste(logo, (image_x, image_y), logo)

    newslideimage.save("./api/presentation/images/test"+str(slide_id)+".png")
    return FileResponse("./api/presentation/images/test"+str(slide_id)+".png")   # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


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
