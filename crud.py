import string

import sqlalchemy.sql.expression
from sqlalchemy.orm import Session
from . import models, schemas
# from PIL import Image
import base64


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
    return db.query(models.Presentation).filter(models.Presentation.id == presentation_id).all()


def get_presentation_by_title(db: Session, presentation_title: str):
    return db.query(models.Presentation).filter(models.Presentation.title == presentation_title).all()


def get_presentation_by_email(db: Session, email: str):
    db_order = get_orders_by_email(db, email=email)
    db_presentations: list[models.Presentation] = []
    for order in db_order:
        presentation = db.query(models.Presentation).filter(models.Presentation.id == order.presentation_id).first()
        db_presentations.append(presentation)
    return db_presentations


def create_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = models.Presentation(title=presentation.title, category_id=presentation.category_id)
    db.add(db_presentation)
    db.commit()
    db.refresh(db_presentation)
    return db_presentation


# def delete_presentation(db: Session, presentation_id: int):
#     db_presentation = db.query(models.Presentation).filter(models.Presentation.id == presentation_id).first()
#     db.delete(db_presentation)
#     db.commit()
#     return


def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


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
    return db.query(models.Slide).filter(models.Slide.title == slide_title).filter(
        models.Slide.presentation_id == presentation_id).first()


def get_slides_by_presentation_id(db: Session, presentation_id: int):
    return db.query(models.Slide).filter(models.Slide.presentation_id == presentation_id).all()    # .first()


def create_slide(db: Session, slide: schemas.SlideCreate):
    db_slide = models.Slide(title=slide.title, presentation_id=slide.presentation_id)
    db.add(db_slide)
    db.commit()
    db.refresh(db_slide)
    return db_slide


def get_slideimage(db: Session, slide_id: int):
    return db.query(models.SlideImage).filter(models.SlideImage.slide_id == slide_id).first()


def get_slideimage_by_presentation_id(db: Session, presentation_id: int):
    dbslide = db.query(models.Slide).filter(models.Slide.presentation_id == presentation_id).first()
    if dbslide is None:
        return None
    return db.query(models.SlideImage).filter(models.SlideImage.slide_id == dbslide.id).first()


def get_slideimages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SlideImage).count()  # .offset(skip).limit(limit).all()


def create_slideimage(db: Session, slideimage: schemas.SlideImageCreate):
    db_slideimage = models.SlideImage(slide_id=slideimage.slide_id, image=convertToBinaryData(slideimage.image))
    db.add(db_slideimage)
    db.commit()
    # db.refresh(db_slideimage)
    return db.query(models.SlideImage).count()  # db_slideimage


def convertToBinaryData(filename):
    # image = Image.open(filename)
    # image.show()
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def get_imagerender_by_slideid(db: Session, slide_id: int):
    return db.query(models.ImageRender).filter(models.ImageRender.slide_id == slide_id).first()


def get_imagerender_by_title(db: Session, slide_id, title: str):
    return db.query(models.ImageRender).filter(models.ImageRender.title == title).filter(
        models.ImageRender.slide_id == slide_id).first()


def get_imagerenders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ImageRender).offset(skip).limit(limit).all()


def create_imagerender(db: Session, imagerender: schemas.ImageRenderCreate):
    db_imagerender = models.ImageRender(title=imagerender.title, slide_id=imagerender.slide_id,
                                        image_id=imagerender.image_id, image_path=imagerender.image_path,
                                        pos_x=imagerender.pos_x, pos_y=imagerender.pos_y, width=imagerender.width,
                                        height=imagerender.height, align=imagerender.align)
    db.add(db_imagerender)
    db.commit()
    db.refresh(db_imagerender)
    return db_imagerender


def edit_imagerender(db: Session, imagerender: schemas.ImageRenderCreate):
    db_imagerender = db.query(models.ImageRender).filter(models.ImageRender.id==imagerender.id).update(
        {"title": imagerender.title, "slide_id": imagerender.slide_id, "image_id": imagerender.image_id,
         "image_path": imagerender.image_path, "height": imagerender.height, "width": imagerender.width,
         "pos_x": imagerender.pos_x, "pos_y": imagerender.pos_y, "align": imagerender.align
         })
    db.commit()
    db_imagerender = db.query(models.ImageRender).filter(models.ImageRender.id==imagerender.id).first()
    db.refresh(db_imagerender)
    return db_imagerender


def get_textrender_by_slideid(db: Session, slide_id: int):
    return db.query(models.TextRender).filter(models.TextRender.slide_id == slide_id).first()


def get_textrender_by_title(db: Session, title: str, slide_id):
    return db.query(models.TextRender).filter(models.TextRender.title == title).filter(
        models.TextRender.slide_id == slide_id).first()


def get_textrenders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TextRender).offset(skip).limit(limit).all()


def create_textrender(db: Session, textrender: schemas.TextRenderCreate):
    db_textrender = models.TextRender(title=textrender.title, slide_id=textrender.slide_id, text=textrender.text,
                                      font=textrender.font, size=textrender.size, pos_x=textrender.pos_x,
                                      pos_y=textrender.pos_y, align=textrender.align, anchor=textrender.anchor,
                                      color_r=textrender.color_r, color_g=textrender.color_g,
                                      color_b=textrender.color_b)
    db.add(db_textrender)
    db.commit()
    db.refresh(db_textrender)
    return db_textrender


def edit_textrender(db: Session, textrender: schemas.TextRenderCreate):
    db_textrender = db.query(models.TextRender).filter(models.TextRender.id==textrender.id).update(
        {"title": textrender.title, "slide_id": textrender.slide_id, "text": textrender.text, "font": textrender.font,
         "size": textrender.size, "pos_x": textrender.pos_x, "pos_y": textrender.pos_y, "align": textrender.align,
         "anchor": textrender.anchor, "color_r": textrender.color_r, "color_g": textrender.color_g,
         "color_b": textrender.color_b
         })
    db.commit()
    db_textrender = db.query(models.TextRender).filter(models.TextRender.id==textrender.id).first()
    db.refresh(db_textrender)
    return db_textrender


def get_orders_by_userid(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()


def get_orders_by_userid_presentationid(db: Session, user_id: int, presentation_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).filter(
        models.Order.presentation_id == presentation_id).all()


def get_orders_by_email(db: Session, email: str):
    db_user = get_user_by_email(db, email=email)
    return db.query(models.Order).filter(models.Order.user_id == db_user.id).all()


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(presentation_id=order.presentation_id, user_id=order.user_id, order_date=order.order_date)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_image(db: Session, image_id: int):
    return db.query(models.LogoImage).filter(models.LogoImage.id == image_id).first()


def get_image_by_user_id(db: Session, user_id: int):
    return db.query(models.LogoImage).filter(models.LogoImage.user_id == user_id).first()


def get_image_by_email(db: Session, email: str):
    dbuser = db.query(models.User).filter(models.User.email == email).first()
    if dbuser is None:
        return None
    return db.query(models.LogoImage).filter(models.LogoImage.user_id == dbuser.id).first()


def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LogoImage).count()  # .offset(skip).limit(limit).all()


def create_image(db: Session, logoimage: schemas.LogoImageCreate):
    db_image = models.LogoImage(user_id=logoimage.user_id, image=convertToBinaryData(logoimage.image))
    db.add(db_image)
    db.commit()
    # db.refresh(db_slideimage)
    return db.query(models.LogoImage).count()  # db_slideimage
