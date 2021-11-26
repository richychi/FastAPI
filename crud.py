from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas


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


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


def get_presentation(db: Session, presentation_id: int):
    return db.query(models.Presentation).filter(models.Presentation.id == presentation_id).first()


def create_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = models.Presentation(id=presentation.id)
    db.add(db_presentation)
    db.commit()
    db.refresh(db_presentation)
    return db_presentation


def delete_presentation(db: Session, presentation_id: int):
    db_presentation = db.query(models.Presentation).filter(models.Presentation.id == presentation_id).first()
    db.delete(db_presentation)
    db.commit()
    return

