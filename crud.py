from sqlalchemy.orm import Session
from . import models, schemas
from PIL import Image


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_presentations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Presentation).offset(skip).limit(limit).all()


def get_presentation(db: Session, presentation_id: int):
    return db.query(models.Presentation).filter(models.Presentation.id == presentation_id).first()


def get_presentation_by_title(db: Session, presentation_title: str):
    return db.query(models.Presentation).filter(models.Presentation.title == presentation_title).first()


def create_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = models.Presentation(title=presentation.title, category_id=presentation.category_id)
    db.add(db_presentation)
    db.commit()
    db.refresh(db_presentation)
    return db_presentation


def delete_presentation(db: Session, presentation_id: int):
    db_presentation = db.query(models.Presentation).filter(models.Presentation.id == presentation_id).first()
    db.delete(db_presentation)
    db.commit()
    return


def get_category(db: Session, id: int):
    return db.query(models.Category).filter(models.Category.id == id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(models.Category).filter(models.Category.title == title).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(title=category.title)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_slides(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Slide).offset(skip).limit(limit).all()


def get_slide(db: Session, slide_id: int):
    return db.query(models.Slide).filter(models.Slide.id == slide_id).first()


def get_slide_by_title(db: Session, slide_title: str, presentation_id):
    return db.query(models.Slide).filter(models.Slide.title == slide_title
                                         and models.Slide.presentation_id == presentation_id).first()


def get_slides_by_presentation_id(db: Session, presentation_id: int):
    return db.query(models.Slide).filter(models.Slide.presentation_id == presentation_id).all()    # .first()


# def get_slide_by_presentation_title(db: Session, presentation_title: str):
#     return db.query(models.Slide).filter(models.Slide.presentation_title == presentation_title).first()


def create_slide(db: Session, slide: schemas.SlideCreate):
    db_slide = models.Slide(title=slide.title, presentation_id=slide.presentation_id)
    db.add(db_slide)
    db.commit()
    db.refresh(db_slide)
    return db_slide


def get_slideimage(db: Session, slide_id: int):
    return db.query(models.SlideImage).filter(models.SlideImage.slide_id == slide_id).first()


def get_slideimages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SlideImage).offset(skip).limit(limit).all()  # .all()


def create_slideimage(db: Session, slideimage: schemas.SlideImageCreate):
    db_slideimage = models.SlideImage(slide_id=slideimage.slide_id, image=convertToBinaryData(slideimage.image))
    db.add(db_slideimage)
    db.commit()
    db.refresh(db_slideimage)
    return db_slideimage


def convertToBinaryData(filename):
    image = Image.open(filename)
    # image.show()
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData
