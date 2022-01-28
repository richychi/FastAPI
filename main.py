# import io
# import asyncio
import hashlib
import io
from typing import List, Callable

from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
# from fastapi.openapi.models import Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
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
import zipfile
from glob import iglob
import os.path
import os

# import requests

# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse


conf = configparser.ConfigParser()
conf.read('config.ini')
server = conf["SERVER"]
userinf = conf["USERINFO"]
social = conf["SOCIAL"]

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


# def send_line(message: str):
#     url = 'https://notify-api.line.me/api/notify'
#     token = social['LINE_TOKEN']
#     headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
#     msg = message
#     r = requests.post(url, headers=headers, data = {'message':msg})
#     print(r)
#     return r


@app.get("/changelog/{id}")
def read_changelog(id: int, db: Session = Depends(get_db)):
    db_changelog = crud.get_changelog(db, id=id)
    if db_changelog is None:
        raise HTTPException(status_code=404, detail="ID not found")
    return db_changelog


@app.get("/changelog/user_id/{user_id}")
def read_changelog_by_userid(user_id: int, db: Session = Depends(get_db)):
    db_changelog = crud.get_changelog_by_userid(db, user_id=user_id)
    if db_changelog is None:
        raise HTTPException(status_code=404, detail="User id not found")
    return db_changelog


@app.post("/changelog/", response_model=schemas.ChangeLog)
def create_changelog(changelog: schemas.ChangeLog, db: Session = Depends(get_db)):
    return crud.create_changelog(db=db, changelog=changelog)


@app.post("/changeimagelog/")
def create_changeimagelog(changeimagelog: schemas.ChangeImageLog, db: Session = Depends(get_db)):
    return crud.create_changeimagelog(db=db, changeimagelog=changeimagelog)


@app.get("/changeimagelog/user_id/{user_id}")
def read_changeimagelog_by_userid(user_id: int, db: Session = Depends(get_db)):
    db_changeimagelog = crud.get_changeimagelog_by_userid(db, user_id=user_id)
    if db_changeimagelog is None:
        raise HTTPException(status_code=404, detail="User id not found")
    return {"ChangeImageLog": [{cil.id, cil.when} for cil in db_changeimagelog]}


@app.get("/changeimagelog/{id}", response_model=schemas.ChangeImageLog)
def read_changeimagelog(id: int, db: Session = Depends(get_db)):
    db_changeimagelog = crud.get_changeimagelog(db, id=id)
    if db_changeimagelog is None:
        raise HTTPException(status_code=404, detail="Id not found")
    return HTMLResponse(db_changeimagelog.new, media_type="image/png")


@app.post("/bundle/", response_model=schemas.Bundle)
def create_bundle(bundle: schemas.BundleCreate, db: Session = Depends(get_db)):
    return crud.create_bundle(db=db, bundle=bundle)


@app.post("/bundle/update/", response_model=schemas.Bundle)
def update_bundle(bundle: schemas.BundleCreate, db: Session = Depends(get_db)):
    return crud.edit_bundle(db=db, bundle=bundle)


@app.post("/bundle/delete/")
def delete_bundle(bundle: schemas.Bundle, db: Session = Depends(get_db)):
    return crud.delete_bundle(db=db, bundle=bundle)


@app.get("/bundles/", response_model=List[schemas.Bundle])
def read_bundle(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bundle = crud.get_bundles(db, skip=skip, limit=limit)
    return bundle


@app.get("/bundle/title/{title}", response_model=schemas.Bundle)
def read_bundle(title: str, db: Session = Depends(get_db)):
    db_bundle = crud.get_bundle_by_title(db, title=title)
    if db_bundle is None:
        raise HTTPException(status_code=404, detail="Bundle title not found")
    return db_bundle


@app.get("/bundle/{bundle_id}", response_model=schemas.Bundle)
def read_bundle(bundle_id: int, db: Session = Depends(get_db)):
    db_bundle = crud.get_bundle(db, bundle_id=bundle_id)
    if db_bundle is None:
        raise HTTPException(status_code=404, detail="Bundle ID not found")
    return db_bundle


@app.post("/bundlepresentation/", response_model=schemas.BundlePresentation)
def create_bundlepresentation(bundlepresentation: schemas.BundlePresentationCreate, db: Session = Depends(get_db)):
    db_bundlepresentation = crud.get_bundlepresentation_by_bundleidpresentationid(db,
                                                                                  bundle_id=bundlepresentation.bundle_id,
                                                                                  presentation_id=bundlepresentation.presentation_id)
    if db_bundlepresentation:
        raise HTTPException(status_code=400, detail="Bundle ID and Presentation ID already existed")
    return crud.create_bundlepresentation(db=db, bundlepresentation=bundlepresentation)


@app.post("/bundlepresentation/delete/")
def delete_bundlepresentation(bundlepresentation: schemas.BundlePresentationCreate, db: Session = Depends(get_db)):
    return crud.delete_bundlepresentation_by_bundleid(db=db, bundle_id=bundlepresentation.bundle_id)


@app.get("/bundlepresentations/", response_model=List[schemas.BundlePresentation])
def read_bundlepresentations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bundlepresentation = crud.get_bundlepresentations(db, skip=skip, limit=limit)
    return bundlepresentation


@app.get("/bundlepresentation/{bundle_id}", response_model=List[schemas.BundlePresentation])
def read_bundlepresentation(bundle_id: int, db: Session = Depends(get_db)):
    db_bundlepresentation = crud.get_bundlepresentation_by_bundleid(db, bundle_id=bundle_id)
    if db_bundlepresentation is None:
        raise HTTPException(status_code=404, detail="Bundle ID not found")
    return db_bundlepresentation


@app.get("/bundlepresentation/{bundle_id}/{presentation_id}", response_model=schemas.BundlePresentation)
def read_bundlepresentation(bundle_id: int, presentation_id: int, db: Session = Depends(get_db)):
    db_bundlepresentation = crud.get_bundlepresentation_by_bundleidpresentationid(db, bundle_id=bundle_id,
                                                                                  presentation_id=presentation_id)
    if db_bundlepresentation is None:
        raise HTTPException(status_code=404, detail="Bundle ID not found")
    return db_bundlepresentation


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/update/", response_model=schemas.User)
def update_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.edit_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/column/", response_model=List[str])
def read_user_column(db: Session = Depends(get_db)):
    users = crud.get_user_column(db)
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


@app.post("/presentations/update/", response_model=schemas.Presentation)
def update_presentation(presentation: schemas.PresentationCreate, db: Session = Depends(get_db)):
    return crud.edit_presentation(db=db, presentation=presentation)


@app.post("/presentations/delete/")
def delete_presentation(presentation: schemas.PresentationCreate, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation(db, presentation_id=presentation.id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation not found")
    return crud.delete_presentation(db=db, presentation=presentation)


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


@app.get("/presentations/title/{presentation_title}", response_model=List[schemas.Presentation])
def read_presentation_by_title(presentation_title: str, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation_by_title(db, presentation_title=presentation_title)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation title not found")
    return db_presentation


@app.get("/presentations/email/{email}", response_model=List[schemas.Presentation])
def read_presentation_by_email(email: str, db: Session = Depends(get_db)):
    db_presentation = crud.get_presentation_by_email(db, email=email)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation by email not found")
    return db_presentation


@app.post("/slides/", response_model=schemas.Slide)
def create_slide(slide: schemas.SlideCreate, db: Session = Depends(get_db)):
    # db_slide = crud.get_slide_by_title(db, slide_title=slide.title, presentation_id=slide.presentation_id)
    # if db_slide:
    #     raise HTTPException(status_code=400, detail="Slide already existed")
    db_slide = crud.create_slide(db=db, slide=slide)
    # await draw_thumb(slide_id=db_slide.id,email="xxx",db=db)
    return db_slide


@app.post("/slide/update/", response_model=schemas.Slide)
async def update_slide(slide: schemas.Slide, db: Session = Depends(get_db)):
    db_slide = crud.edit_slide(db=db, slide=slide)
    await draw_thumb(slide_id=slide.id,email="xxx",db=db)
    return db_slide


@app.post("/slide/delete/")
def update_slide(slide: schemas.Slide, db: Session = Depends(get_db)):
    return crud.delete_slide(db=db, slide=slide)


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


@app.get("/slide/{slide_id}", response_model=schemas.Slide)
def read_slide_by_slideid(slide_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slide_by_slideid(db, id=slide_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    return db_slide


@app.get("/slides/presentation_id/{presentation_id}/{column}")
def read_slides_by_presentation_id(presentation_id: int, column: str, db: Session = Depends(get_db)):
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Presentation id not found")
    db_column = ''
    for i in db_slide:
        db_column += str(i.id) + ',' + str(i(column))
    return db_column


@app.post("/slideimage/")  # , response_model=schemas.SlideImage)
def create_slideimage(slideimage: schemas.SlideImageCreate, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slideimage.slide_id)
    if db_slideimage:
        raise HTTPException(status_code=400, detail="SlideImage already existed")
    db_slideimage = crud.create_slideimage(db=db, slideimage=slideimage)
    # await draw_thumb(slide_id=slideimage.slide_id,email="xxx",db=db)
    return db_slideimage


@app.post("/slideimage/update/")
async def update_slideimage(slideimage: schemas.SlideImage, db: Session = Depends(get_db)):
    db_slideimage = crud.edit_slideimage(db=db, slideimage=slideimage)
    await draw_thumb(slide_id=slideimage.slide_id,email="xxx@xxx.xxx",db=db)
    return db_slideimage # HTMLResponse(db_slideimage.image, media_type="image/png")


@app.get("/slideimages/")  # , response_model=List[schemas.SlideImage])
def read_slideimages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_slideimages = crud.get_slideimages(db, skip=skip, limit=limit)
    if not db_slideimages:
        raise HTTPException(status_code=404, detail="SlideImages not found")
    return db_slideimages  # HTMLResponse(db_slideimages.image, media_type="image/png")


@app.get("/slideimageid/{slide_id}")
def read_slideimage(slide_id: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    return db_slideimage.id


@app.get("/slideimage/{slide_id}", response_model=schemas.SlideImage)
def read_slideimage(slide_id: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    return HTMLResponse(db_slideimage.image, media_type="image/png")  # db_slideimage


@app.get("/slideimage/presentation_id/{presentation_id}")  # , response_model=schemas.SlideImage)
async def read_slideimage(presentation_id: int, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage_by_presentation_id(db, presentation_id=presentation_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="SlideImage not found")
    return await get_thumb(slide_id=db_slideimage.slide_id,email="xxx@xxx.xxx",db=db)
    # return HTMLResponse(db_slideimage.image, media_type="image/png")


@app.post("/image/")  # , response_model=schemas.SlideImage)
def create_image(logoimage: schemas.LogoImageCreate, db: Session = Depends(get_db)):
    db_image = crud.get_image_by_user_id(db, user_id=logoimage.user_id)
    if db_image:
        raise HTTPException(status_code=400, detail="User have image already")
    db_image = crud.create_image(db=db, logoimage=logoimage)
    # crud.create_changeimagelog_by_new(db,)
    return db_image


@app.post("/image/{email}")  # , response_model=schemas.SlideImage)
def create_image_by_email(email: str, logoimage: schemas.LogoImageCreate, db: Session = Depends(get_db)):
    userid = crud.get_user_by_email(db, email=email)
    if not userid:
        raise HTTPException(status_code=404, detail="Email not found")
    db_image = crud.get_image_by_user_id(db, user_id=userid.id)
    if db_image:
        raise HTTPException(status_code=400, detail="User have image already")
    db_image = crud.create_image(db=db, logoimage=logoimage)
    return db_image


@app.post("/image/update/", response_model=schemas.LogoImage)
def update_image(logoimage: schemas.LogoImageCreate, db: Session = Depends(get_db)):
    db_image = crud.edit_image(db=db, logoimage=logoimage)
    return HTMLResponse(db_image.image, media_type="image/png")


@app.post("/image/update/email/{email}", response_model=schemas.LogoImage)
def update_image_by_email(email: str, logoimage: schemas.LogoImageCreate, db: Session = Depends(get_db)):
    db_image = crud.edit_image_by_email(email=email, db=db, logoimage=logoimage)
    return HTMLResponse(db_image.image, media_type="image/png")


@app.get("/images/")  # , response_model=List[schemas.SlideImage])
def read_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_images = crud.get_images(db, skip=skip, limit=limit)
    if not db_images:
        raise HTTPException(status_code=404, detail="Images not found")
    return db_images  # HTMLResponse(db_slideimages.image, media_type="image/png")


@app.get("/image/{image_id}", response_model=schemas.LogoImage)
def read_image(image_id: int, db: Session = Depends(get_db)):
    db_image = crud.get_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image id not found")
    return HTMLResponse(db_image.image, media_type="image/png")


@app.get("/image/user_id/{user_id}", response_model=schemas.LogoImage)
def read_image(user_id: int, db: Session = Depends(get_db)):
    db_image = crud.get_image_by_user_id(db, user_id=user_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="User id not found")
    return HTMLResponse(db_image.image, media_type="image/png")


@app.get("/image/email/{email}", response_model=schemas.LogoImage)
def read_image(email: str, db: Session = Depends(get_db)):
    db_image = crud.get_image_by_email(db, email=email)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return HTMLResponse(db_image.image, media_type="image/png")


@app.post("/imagerenders/", response_model=schemas.ImageRender)
async def create_imagerender(imagerender: schemas.ImageRenderCreate, db: Session = Depends(get_db)):
    db_imagerender = crud.get_imagerender_by_title(db, title=imagerender.title, slide_id=imagerender.slide_id)
    if db_imagerender:
        raise HTTPException(status_code=400, detail="ImageRender already existed")
    db_imagerender = crud.create_imagerender(db=db, imagerender=imagerender)
    await draw_thumb(slide_id=imagerender.slide_id,email="xxx",db=db)
    return db_imagerender


@app.post("/imagerender/update/", response_model=schemas.ImageRender)
async def update_imagerender(imagerender: schemas.ImageRenderCreate, db: Session = Depends(get_db)):
    db_imagerender =crud.edit_imagerender(db=db, imagerender=imagerender)
    await draw_thumb(slide_id=imagerender.slide_id,email="xxx",db=db)
    return db_imagerender


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
async def create_textrender(textrender: schemas.TextRenderCreate, db: Session = Depends(get_db)):
    db_txtrender = crud.get_textrender_by_title(db, title=textrender.title, slide_id=textrender.slide_id)
    if db_txtrender:
        raise HTTPException(status_code=400, detail="TextRender already existed")
    db_txtrender = crud.create_textrender(db=db, textrender=textrender)
    await draw_thumb(slide_id=textrender.slide_id,email="xxx",db=db)
    return db_txtrender


@app.post("/textrender/update/", response_model=schemas.TextRender)
async def update_textrender(textrender: schemas.TextRenderCreate, db: Session = Depends(get_db)):
    db_txtrender = crud.edit_textrender(db=db, textrender=textrender)
    await draw_thumb(slide_id=textrender.slide_id,email="xxx",db=db)
    return db_txtrender


@app.get("/textrenders/", response_model=List[schemas.TextRender])
def read_textrenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_textrenders = crud.get_textrenders(db, skip=skip, limit=limit)
    return db_textrenders


@app.get("/textrenders/{slide_id}", response_model=List[schemas.TextRender])
def read_textrenders_by_slideid(slide_id: int, db: Session = Depends(get_db)):
    db_textrenders = crud.get_textrenders_by_slideid(db, slide_id=slide_id)
    if db_textrenders is None:
        raise HTTPException(status_code=404, detail="TextRender by slide_id not found")
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


@app.get("/fonts/")
def get_fonts():
    path = server["FONT_PATH"]
    result = iglob(path + "*.ttf")
    return [res.replace(path, "") for res in sorted(result)]


@app.get("/imagefiles/")
def get_imagefiles():
    path = server["SLIDE_PATH"]
    result = iglob(path + "*.png")
    return [res.replace(path, "") for res in sorted(result)]


@app.get("/imagefile/{name}")
async def get_imagefile(name: str):
    return FileResponse(server["SLIDE_PATH"] + name)


@app.get("/thumbfile/{name}/{email}")
async def get_thumbfile(name: str, email: str, db: Session = Depends(get_db)):
    if os.path.exists(server["IMAGE_PATH"] + name + ".png"):
        return FileResponse(server["IMAGE_PATH"] + name + ".png")
    else:
        try:
            return await draw_thumb(slide_id=int(name), email=email, db=db)
        except Exception:
            return Exception
    # return FileResponse(server["IMAGE_PATH"] + name +".png")


@app.get("/logofiles/")
def get_logofiles():
    path = server["LOGO_PATH"]
    result = iglob(path + "*.png")
    return [res.replace(path, "") for res in sorted(result)]


@app.get("/logofile/{name}")
async def get_logofile(name: str):
    return FileResponse(server["LOGO_PATH"] + name)


@app.get("/drawslideimage/{slide_id}/{email}")
async def draw_slideimage(slide_id: int, email: str, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    usr = crud.get_user_by_email(db,email=email)
    print('user: '+usr)
    draw = ImageDraw.Draw(newslideimage)
    db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
    print('db_textrender.text')
    if db_textrender:
        txt = ""
        if usr:
            if db_textrender.text == "email":
                txt = usr.email
            else:
                if db_textrender.text == "firstname":
                    txt = usr.firstname
                else:
                    if db_textrender.text == "lastname":
                        txt = usr.lastname
                    else:
                        if db_textrender.text == "fullname":
                            txt = usr.firstname + " " + usr.lastname
                        else:
                            if db_textrender.text == "contact_no":
                                txt = usr.contact_no
                            else:
                                if db_textrender.text == "contact_info":
                                    txt = usr.contact_info
                                else:
                                    txt = db_textrender.text
        fnt = ImageFont.truetype(server["FONT_PATH"] + db_textrender.font, db_textrender.size)
        draw.text(xy=(db_textrender.pos_x, db_textrender.pos_y), text=txt, align=db_textrender.align,
                  anchor=db_textrender.anchor, font=fnt, fill=(db_textrender.color_r,
                                                               db_textrender.color_g, db_textrender.color_b))
    # newslideimage.show()
    db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
    if db_imagerender:
        db_logo = crud.get_image_by_email(db, email=email)
        if db_logo:
            logo = Image.open(io.BytesIO(db_logo.image))
        else:
            logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
        logo = logo.resize((db_imagerender.width, db_imagerender.height))
        try:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y), logo)
        except Exception:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y))
    newslideimage.save(server["IMAGE_PATH"] + str(slide_id) + ".png")
    return FileResponse(server["IMAGE_PATH"] + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/drawslide/{slide_id}/{email}")
async def draw_slide(slide_id: int, email: str, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    usr = crud.get_user_by_email(db,email=email)
    draw = ImageDraw.Draw(newslideimage)
    db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
    if db_textrender:
        txt = ""
        if usr:
            if db_textrender.text == "email":
                txt = usr.email
            else:
                if db_textrender.text == "firstname":
                    txt = usr.firstname
                else:
                    if db_textrender.text == "lastname":
                        txt = usr.lastname
                    else:
                        if db_textrender.text == "fullname":
                            txt = usr.firstname + " " + usr.lastname
                        else:
                            if db_textrender.text == "contact_no":
                                txt = usr.contact_no
                            else:
                                if db_textrender.text == "contact_info":
                                    txt = usr.contact_info
                                else:
                                    txt = db_textrender.text
        fnt = ImageFont.truetype(server["FONT_PATH"] + db_textrender.font, db_textrender.size)
        draw.text(xy=(db_textrender.pos_x, db_textrender.pos_y), text=txt, align=db_textrender.align,
                  anchor=db_textrender.anchor, font=fnt, fill=(db_textrender.color_r,
                  db_textrender.color_g, db_textrender.color_b))
    # newslideimage.show()
    db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
    if db_imagerender:
        db_logo = crud.get_image_by_email(db, email=email)
        if db_logo:
            logo = Image.open(io.BytesIO(db_logo.image))
        else:
            logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
        logo = logo.resize((db_imagerender.width, db_imagerender.height))
        try:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y), logo)
        except Exception:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y))
    if os.path.exists(email):
        print("path "+email+" exists")
    else:
        os.mkdir(email)
    epath = email #.replace(".", "").replace("@","")
    newslideimage.save(epath + "/" + str(slide_id) + ".png")
    return FileResponse(epath + "/" + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/drawslidetest/{slide_id}/{email}/{slide_name}/{text}/{font_name}/{font_size}/{text_x}/{text_y}/{text_anchor}"
         "/{color_r}/{color_g}/{color_b}/{image_x}/{image_y}/{image_width}/{image_height}")
async def draw_slidetest(slide_id: int, email: str, slide_name: str, text: str, font_name: str, font_size: int, text_x: int,
                     text_y: int, text_anchor: str, color_r: int, color_g: int, color_b: int,
                     image_x: int, image_y: int, image_width: int, image_height: int, db: Session = Depends(get_db)):
    if slide_name == "" or slide_name == "Old Slide Image":
        db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
        if db_slideimage is None:
            raise HTTPException(status_code=404, detail="Slide id not found")
        newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    else:
        newslideimage = Image.open(server["SLIDE_PATH"] + slide_name)
    draw = ImageDraw.Draw(newslideimage)
    usr = crud.get_user_by_email(db,email=email)
    if text:
        txt = ""
        if usr:
            if text == "email":
                txt = usr.email
            else:
                if text == "firstname":
                    txt = usr.firstname
                else:
                    if text == "lastname":
                        txt = usr.lastname
                    else:
                        if text == "fullname":
                            txt = usr.firstname + " " + usr.lastname
                        else:
                            if text == "contact_no":
                                txt = usr.contact_no
                            else:
                                if text == "contact_info":
                                    txt = usr.contact_info
                                else:
                                    txt = text
        fnt = ImageFont.truetype(server["FONT_PATH"] + font_name, font_size)
        draw.text(xy=(text_x, text_y), text=txt, anchor=text_anchor, font=fnt, fill=(color_r, color_g, color_b))

    db_logo = crud.get_image_by_email(db, email=email)
    if db_logo:
        logo = Image.open(io.BytesIO(db_logo.image))
    else:
        logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
    logo = logo.resize((image_width, image_height))
    try:
        newslideimage.paste(logo, (image_x, image_y), logo)
    except Exception:
        newslideimage.paste(logo, (image_x, image_y))
    if os.path.exists(email):
        print("path "+email+" exists")
    else:
        os.mkdir(email)
    epath = email #.replace(".", "").replace("@","")
    newslideimage.save(epath + "/" + str(slide_id) + ".png")
    return FileResponse(epath + "/" + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/testdrawslide/{slide_id}/{text}/{font_name}/{font_size}/{text_x}/{text_y}/{color_r}/{color_g}/{color_b}"
         "/{image_x}/{image_y}/{image_width}/{image_height}/{email}")
async def testdraw_slide(slide_id: int, text: str, font_name: str, font_size: int, text_x: int, text_y: int,
                         color_r: int, color_g: int, color_b: int, image_x: int, image_y: int, image_width: int,
                         image_height: int, email: str, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    draw = ImageDraw.Draw(newslideimage)
    fnt = ImageFont.truetype(server["FONT_PATH"] + font_name, font_size)
    draw.text(xy=(text_x, text_y), text=text, align='left', anchor='la', font=fnt, fill=(color_r, color_g, color_b))
    # newslideimage.show()
    db_logo = crud.get_image_by_email(db, email=email)
    if db_logo is None:
        logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
    else:
        logo = Image.open(io.BytesIO(db_logo.image))
    logo = logo.resize((image_width, image_height))
    try:
        newslideimage.paste(logo, (image_x, image_y), logo)
    except Exception:
        newslideimage.paste(logo, (image_x, image_y))

    newslideimage.save(server["IMAGE_PATH"] + "test" + str(slide_id) + ".png")
    return FileResponse(server["IMAGE_PATH"] + "test" + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/drawthumb/{slide_id}/{email}")
async def get_thumb(slide_id: int, email: str, db: Session = Depends(get_db)):
    if email != 'xxx@xxx.xxx':
        db_user = crud.get_user_by_email(db=db, email=email)
        if db_user is None:
            raise HTTPException(status_code=403, detail="You no right")
        else:
            if db_user.role == 'user':
                db_slide = crud.get_slide_by_slideid(db=db, id=slide_id)
                db_right = crud.get_right_by_userid_presentationid(db=db, user_id=db_user.id,
                                                                   presentation_id=db_slide.presentation_id)
                if db_right is None:
                    raise HTTPException(status_code=403, detail="You no right")
    if os.path.isfile(server["IMAGE_PATH"] + str(slide_id) + ".png"):
        print("file "+server["IMAGE_PATH"] + str(slide_id) + ".png"+" exists")
    else:
        print("draw new "+server["IMAGE_PATH"] + str(slide_id) + ".png")
        db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
        if db_slideimage is None:
            raise HTTPException(status_code=404, detail="Slide id not found")
        newslideimage = Image.open(io.BytesIO(db_slideimage.image))
        # newslideimage.show()
        draw = ImageDraw.Draw(newslideimage)
        db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
        if db_textrender:
            # raise HTTPException(status_code=404, detail="Textrender not found")
            fnt = ImageFont.truetype(server["FONT_PATH"] + db_textrender.font, db_textrender.size)
            draw.text(xy=(db_textrender.pos_x, db_textrender.pos_y), text=db_textrender.text, align=db_textrender.align,
                      anchor=db_textrender.anchor, font=fnt, fill=(db_textrender.color_r,
                      db_textrender.color_g, db_textrender.color_b))
        # newslideimage.show()
        db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
        if db_imagerender:
            logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
            logo = logo.resize((db_imagerender.width, db_imagerender.height))
            try:
                newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y), logo)
            except Exception:
                newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y))

        newslideimage = newslideimage.resize((477, 256))
        newslideimage.save(server["IMAGE_PATH"] + str(slide_id) + ".png")
    return FileResponse(server["IMAGE_PATH"] + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/drawthumb/{slide_id}/{email}/")
async def draw_thumb(slide_id: int, email: str, db: Session = Depends(get_db)):
    db_slideimage = crud.get_slideimage(db, slide_id=slide_id)
    if db_slideimage is None:
        raise HTTPException(status_code=404, detail="Slide id not found")
    newslideimage = Image.open(io.BytesIO(db_slideimage.image))
    # newslideimage.show()
    draw = ImageDraw.Draw(newslideimage)
    db_textrender = crud.get_textrender_by_slideid(db, slide_id=slide_id)
    if db_textrender:
        # raise HTTPException(status_code=404, detail="Textrender not found")
        fnt = ImageFont.truetype(server["FONT_PATH"] + db_textrender.font, db_textrender.size)
        draw.text(xy=(db_textrender.pos_x, db_textrender.pos_y), text=db_textrender.text, align=db_textrender.align,
                  anchor=db_textrender.anchor, font=fnt, fill=(db_textrender.color_r,
                                                               db_textrender.color_g, db_textrender.color_b))
    # newslideimage.show()
    db_imagerender = crud.get_imagerender_by_slideid(db, slide_id=slide_id)
    if db_imagerender:
        db_logo = crud.get_image_by_email(db, email=email)
        if db_logo:
            logo = Image.open(io.BytesIO(db_logo.image))
        else:
            logo = Image.open(server["IMAGE_PATH"] + "placeholder.png")
        logo = logo.resize((db_imagerender.width, db_imagerender.height))
        try:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y), logo)
        except Exception:
            newslideimage.paste(logo, (db_imagerender.pos_x, db_imagerender.pos_y))

    newslideimage = newslideimage.resize((477, 256))
    newslideimage.save(server["IMAGE_PATH"] + str(slide_id) + ".png")
    print('new thumb')
    return FileResponse(server["IMAGE_PATH"] + str(slide_id) + ".png")  # "/api/presentation/images/"+
    # return FileResponse(newslideimage.tobytes("utf-8"), media_type="image/png")


@app.get("/downloadzip/{presentation_id}")
async def download_zip(presentation_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Slide by Presentation_id not found")
    with zipfile.ZipFile(server["IMAGE_PATH"] + "presentation" + str(presentation_id) + ".zip", "w") as zf:
        for slide in db_slide:
            zf.write(server["IMAGE_PATH"] + str(slide.id) + ".png")
        # zf.setpassword(b"password")
    return FileResponse(server["IMAGE_PATH"] + "presentation" + str(presentation_id) + ".zip")


@app.get("/gendownloadzip/{presentation_id}/{email}")
# @app.post("/gendownloadzip/{presentation_id}/{email}")
async def gendownload_zip(presentation_id: int, email: str, db: Session = Depends(get_db)):
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Slide by Presentation_id not found")
    epath = email #.replace(".", "").replace("@","")
    if os.path.exists(epath):
        print(epath + " path is exists")
    else:
        os.mkdir(epath)
    with zipfile.ZipFile(epath + "/presentation" + str(presentation_id) + ".zip", "w") as zf:
        for slide in db_slide:
            await draw_slide(slide_id=slide.id, email=email, db=db)
            zf.write(epath + "/" + str(slide.id) + ".png")
        # zf.setpassword(b"password")
    return FileResponse(epath + "/presentation" + str(presentation_id) + ".zip")


@app.get("/gendownloadazip/{user_id}/presentation{presentation_id}")
# @app.post("/gendownloadzip/{presentation_id}/{email}")
async def gendownloadzip(presentation_id: int, user_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        raise HTTPException(status_code=404, detail="Slide by Presentation_id not found")
    db_user = crud.get_user(db,user_id=user_id)
    epath = db_user.email  # .replace(".", "").replace("@","")
    if os.path.exists(epath):
        print(epath + " path is exists")
    else:
        os.mkdir(epath)
    with zipfile.ZipFile(epath + "/presentation" + str(presentation_id) + ".zip", "w") as zf:
        for slide in db_slide:
            await draw_slide(slide_id=slide.id, email=db_user.email, db=db)
            zf.write(epath + "/" + str(slide.id) + ".png")
        # zf.setpassword(b"password")
    return FileResponse(epath + "/presentation" + str(presentation_id) + ".zip")


@app.get("/gendownloadazip/{user_id}/{presentation_id}/{hash_id}")
async def downloadhashzip(presentation_id: int, user_id: int, hash_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db,user_id=user_id)
    epath = db_user.email
    print(epath + "/" + hash_id + ".zip")
    return FileResponse(epath + "/" + hash_id + ".zip",
                        filename="presentation"+str(presentation_id)+".zip")


@app.post("/gendownloadazip/{user_id}/{presentation_id}/")  # {user_id}/{presentation_id}/
async def gendownloadzip_by_hashid(presentation_id: int, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db,user_id=user_id)
    if db_user.role == 'user':
        db_right = crud.get_right_by_userid_presentationid(db,user_id=user_id,presentation_id=presentation_id)
        if db_right is None:
            print("User No Right")
            raise HTTPException(status_code=304, detail="User No Right")
    db_slide = crud.get_slides_by_presentation_id(db, presentation_id=presentation_id)
    if db_slide is None:
        print("Slide by Presentation_id not found")
        raise HTTPException(status_code=404, detail="Slide by Presentation_id not found")
    epath = db_user.email  # .replace(".", "").replace("@","")
    if os.path.exists(epath):
        print(epath + " path is exists")
    else:
        os.mkdir(epath)
    f_name = hashlib.md5(str(user_id*presentation_id).encode('utf-8')).hexdigest()
    with zipfile.ZipFile(epath + "/" + f_name + ".zip", "w") as zf:
        for slide in db_slide:
            await draw_slide(slide_id=slide.id, email=db_user.email, db=db)
            zf.write(epath + "/" + str(slide.id) + ".png")
        # zf.setpassword(b"password")
    return f_name


@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)


@app.post("/orderrights/", response_model=schemas.Order)
def create_order_right(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order_right(db=db, order=order)


@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    if len(orders) == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders


@app.get("/orders/{bundle_id}", response_model=List[schemas.Order])
def read_order(bundle_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_orders_by_bundleid(db, bundle_id=bundle_id)
    if len(db_order) == 0:
        raise HTTPException(status_code=404, detail="Bundle ID not found")
    return db_order


@app.get("/orders/email/{user_email}", response_model=List[schemas.Order])
def read_order_by_email(user_email: str, db: Session = Depends(get_db)):
    db_order = crud.get_orders_by_email(db, email=user_email)
    if len(db_order) == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_order


@app.post("/right/", response_model=schemas.Right)
def create_right(right: schemas.RightCreate, db: Session = Depends(get_db)):
    db_right = crud.get_right_by_userid_presentationid(db, user_id=right.user_id,
                                                       presentation_id=right.presentation_id)
    if db_right:
        raise HTTPException(status_code=400, detail="User brought this presentation already")
    return crud.create_right(db=db, right=right)


@app.get("/right/")  # , response_model=List[schemas.Right])
def read_right(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_right = crud.get_right(db, skip=skip, limit=limit)
    if len(db_right) == 0:
        raise HTTPException(status_code=404, detail="Right not found")
    return db_right


@app.get("/right/{user_id}")  # , response_model=List[schemas.Right])
def read_right(user_id: int, db: Session = Depends(get_db)):
    db_right = crud.get_right_by_userid(db, user_id=user_id)
    if len(db_right) == 0:
        raise HTTPException(status_code=404, detail="User ID not found")
    return db_right


@app.get("/right/{user_id}/{presentation_id}", response_model=schemas.Right)
def read_right(user_id: int, presentation_id: int, db: Session = Depends(get_db)):
    db_right = crud.get_right_by_userid_presentationid(db, user_id=user_id,presentation_id=presentation_id)
    if db_right is None:
        raise HTTPException(status_code=404, detail="User ID No Right")
    return db_right


@app.get("/right/email/{user_email}")  # , response_model=List[schemas.Right])
def read_right_by_email(user_email: str, db: Session = Depends(get_db)):
    db_right = crud.get_right_by_email(db, email=user_email)
    if db_right is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_right


@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}


@app.get("/uploadtest/")
async def uploadtest():
    content = """
<body>
<form action=""" + server["API_URL"] + """/ttf/ enctype="multipart/form-data" method="post">
<label for="upload_ttf">Upload Font:</label>
<input name="in_file" id="upload_ttf" type="file" multiple accept=".ttf">
<input type="submit">
</form>
<form action=""" + server["API_URL"] + """/files/ enctype="multipart/form-data" method="post">files
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action=""" + server["API_URL"] + """/uploadfiles/ enctype="multipart/form-data" method="post">uploadfiles
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action=""" + server["API_URL"] + """/endpoint1/ enctype="multipart/form-data" method="post">endpoint1
<input name="in_file" type="file" accept="image/png">
<input type="submit">
</form>
<form action=""" + server["API_URL"] + """/endpoint2/ enctype="multipart/form-data" method="post">endpoint2
<input name="in_file" type="file" accept="image/*">
<input type="submit">
</form>
<form action=""" + server["API_URL"] + """/endpoint3/ enctype="multipart/form-data" method="post">endpoint3
<input name="in_file" type="file" multiple accept="image/*">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/upload/")
async def upload():
    content = """
<body>
<form action=""" + server["API_URL"] + """/uploadttf/ enctype="multipart/form-data" method="post" 
class="bg-white rounded-lg p-8 flex flex-col md:ml-auto w-full mt-10 md:mt-0 relative z-10 shadow-md">
<label for="upload_ttfs">Fonts</label>
<input name="in_file" id="upload_ttfs" type="file" multiple accept="font/ttf" class="w-full">
<input type="submit" value="Upload Fonts" class="text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none 
hover:bg-indigo-600 rounded text-lg">
</form>
<form action=""" + server["API_URL"] + """/uploadimage/ enctype="multipart/form-data" method="post" 
class="bg-white rounded-lg p-8 flex flex-col md:ml-auto w-full mt-10 md:mt-0 relative z-10 shadow-md">
<label for="upload_images">Images</label>
<input name="in_file" id="upload_images" type="file" multiple accept="image/png" class="w-full">
<input type="submit" value="Upload Slides" class="text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none 
hover:bg-indigo-600 rounded text-lg">
</form>
<form action=""" + server["API_URL"] + """/uploadlogo/ enctype="multipart/form-data" method="post" 
class="bg-white rounded-lg p-8 flex flex-col md:ml-auto w-full mt-10 md:mt-0 relative z-10 shadow-md">
<label for="upload_logos">Logos</label>
<input name="in_file" id="upload_logos" type="file" multiple accept="image/png" class="w-full">
<input type="submit" value="Upload Logos" class="text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none 
hover:bg-indigo-600 rounded text-lg">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/uploadlibrary/")
async def uploadlibrary():
    content = """
<body>
<form action=""" + server["API_URL"] + """/uploadlibrary/ enctype="multipart/form-data" method="post" 
class="bg-white rounded-lg p-8 flex flex-col md:ml-auto w-full mt-10 md:mt-0 relative z-10 shadow-md">
<div class="md:flex md:items-center mb-6">
<div class="md:w-2/5 text-right mr-10">
<label for="upload_ttfs" class="md:text-right">TTF Fonts:</label>
</div>
<div class="md:w-3/5">
<input name="font_file" id="upload_ttfs" type="file" multiple accept="font/ttf" class="w-full">
</div>
</div>
<div class="md:flex md:items-center mb-6">
<div class="md:w-2/5 text-right mr-10">
<label for="upload_images" class="md:text-right">Slide Images:</label>
</div>
<div class="md:w-3/5">
<input name="slide_file" id="upload_images" type="file" multiple accept="image/png" class="w-full">
</div>
</div>
<div class="md:flex md:items-center mb-6">
<div class="md:w-2/5 text-right mr-10">
<label for="upload_logos" class="md:text-right">Logo/Photos:</label>
</div>
<div class="md:w-3/5">
<input name="logo_file" id="upload_logos" type="file" multiple accept="image/png" class="w-full">
</div>
</div>
<input type="submit" value="Upload" class="text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none 
hover:bg-indigo-600 rounded text-lg">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/uploadlibrary/")
async def post_library(font_file: List[UploadFile] = File(...), slide_file: List[UploadFile] = File(...),
                       logo_file: List[UploadFile] = File(...)):
    # return {"font_file[0]": font_file[0],"filename": font_file[0].filename}
    if font_file[0].filename != "":
        for file in font_file:
            async with aiofiles.open(server["FONT_PATH"] + file.filename, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
    if slide_file[0].filename != "":
        for file in slide_file:
            async with aiofiles.open(server["SLIDE_PATH"] + file.filename, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
    if logo_file[0].filename != "":
        for file in logo_file:
            async with aiofiles.open(server["LOGO_PATH"] + file.filename, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
    return {"font": [file.filename for file in font_file],
            "slide": [file.filename for file in slide_file],
            "logo": [file.filename for file in logo_file],
            }


@app.post("/ttf/")
async def post_ttf(in_file: List[UploadFile] = File(...)):
    for file in in_file:
        # save_upload_file(file,server["FONT_PATH"])
        async with aiofiles.open(server["FONT_PATH"] + file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    return {"filenames": [file.filename for file in in_file]}


@app.post("/uploadttf/")
async def post_ttfs(in_file: List[UploadFile] = File(...)):
    for file in in_file:
        # save_upload_file(file,server["FONT_PATH"])
        async with aiofiles.open(server["FONT_PATH"] + file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    return RedirectResponse(server["ORIGIN"] + "/mypresentation/")


@app.post("/uploadimage/")
async def post_images(in_file: List[UploadFile] = File(...)):
    for file in in_file:
        async with aiofiles.open(server["SLIDE_PATH"] + file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    # return {RedirectResponse(server["ORIGIN"]+"/mypresentation/")}
    return [{"Result": "OK"}, {"filenames": [file.filename for file in in_file]}]


@app.post("/uploadlogo/")
async def post_logos(in_file: List[UploadFile] = File(...)):
    for file in in_file:
        async with aiofiles.open(server["LOGO_PATH"] + file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    # return {RedirectResponse(server["ORIGIN"]+"/mypresentation/")}
    return [{"Result": "OK"}, {"filenames": [file.filename for file in in_file]}]


@app.post("/endpoint1/")
async def post_endpoint1(in_file: UploadFile = File(...)):
    # ...
    async with aiofiles.open(server["FILE_PATH"] + in_file.filename, 'wb') as out_file:
        content = await in_file.read()  # async read
        await out_file.write(content)  # async write

    return {"Result": "OK"}


@app.post("/endpoint2/")
async def post_endpoint2(in_file: UploadFile = File(...)):
    # ...
    async with aiofiles.open(server["FILE_PATH"] + in_file.filename, 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return {"Result": "OK"}


@app.post("/endpoint3/")
async def post_endpoint3(in_file: List[UploadFile] = File(...)):
    for file in in_file:
        async with aiofiles.open(server["FILE_PATH"] + file.filename, 'wb') as out_file:
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
