import string

import sqlalchemy.sql.expression
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
# from PIL import Image
import base64


def get_bundle(db: Session, bundle_id: int):
    return db.query(models.Bundle).filter(models.Bundle.is_active).filter(models.Bundle.id == bundle_id).first()


def get_bundle_by_title(db: Session, title: str):
    return db.query(models.Bundle).filter(models.Bundle.is_active).filter(models.Bundle.title == title).first()


def get_bundles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bundle).filter(models.Bundle.is_active).offset(skip).limit(limit).all()


def create_bundle(db: Session, bundle: schemas.BundleCreate):
    db_bundle = models.Bundle(title=bundle.title, price=bundle.price, start_date=bundle.start_date)
    db.add(db_bundle)
    db.commit()
    db.refresh(db_bundle)
    return db_bundle


def edit_bundle(db: Session, bundle: schemas.BundleCreate):
    db_bundle = db.query(models.Bundle).filter(models.Bundle.id == bundle.id).update(
        {"title": bundle.title, "price": bundle.price})
    db.commit()
    db_bundle = db.query(models.Bundle).filter(models.Bundle.id == bundle.id).first()
    db.refresh(db_bundle)
    return db_bundle


def delete_bundle(db: Session, bundle: schemas.Bundle):
    db_bundle = db.query(models.Bundle).filter(models.Bundle.id == bundle.id).update(
        {"is_active": False})
    db_bundlepresentation = db.query(models.BundlePresentation).filter(
        models.BundlePresentation.bundle_id == bundle.id).update(
        {"is_active": False})
    db.commit()
    return db_bundle


def get_bundlepresentation_by_bundleid(db: Session, bundle_id: int):
    return db.query(models.BundlePresentation).filter(models.BundlePresentation.is_active).filter(
        models.BundlePresentation.bundle_id == bundle_id).all()


def get_bundlepresentation_by_bundleidpresentationid(db: Session, bundle_id: int, presentation_id: int):
    return db.query(models.BundlePresentation).filter(
        models.BundlePresentation.is_active).filter(
        models.BundlePresentation.bundle_id == bundle_id).filter(
        models.BundlePresentation.presentation_id == presentation_id).first()


def get_bundlepresentations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BundlePresentation).filter(models.BundlePresentation.is_active).offset(
        skip).limit(limit).all()


def create_bundlepresentation(db: Session, bundlepresentation: schemas.BundlePresentationCreate):
    db_bundlepresentation = models.BundlePresentation(presentation_id=bundlepresentation.presentation_id,
                                                      bundle_id=bundlepresentation.bundle_id)
    db.add(db_bundlepresentation)
    db.commit()
    db.refresh(db_bundlepresentation)
    return db_bundlepresentation


def delete_bundlepresentation_by_bundleid(db: Session, bundle_id: int):
    db_bundlepresentation = db.query(models.BundlePresentation).filter(
        models.BundlePresentation.bundle_id == bundle_id).update({"is_active": False})
    db.commit()
    return db_bundlepresentation


def delete_bundlepresentation_by_presentationid(db: Session, presentation_id: int):
    db_bundlepresentation = db.query(models.BundlePresentation).filter(
        models.BundlePresentation.presentation_id == presentation_id).update({"is_active": False})
    db.commit()
    return db_bundlepresentation


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.is_active).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.is_active).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.is_active).offset(skip).limit(limit).all()


def get_user_column(db: Session):
    return db.query(models.User).filter(models.User.is_active).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, role=user.role, firstname=user.firstname, lastname=user.lastname,
                          contact_no=user.contact_no, contact_line=user.contact_line, contact_fb=user.contact_fb,
                          contact_ig=user.contact_ig,
                          contact_tw=user.contact_tw, contact_info=user.contact_info)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def edit_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user.id).update(
        {"email": user.email, "firstname": user.firstname, "lastname": user.lastname,
         "contact_no": user.contact_no, "contact_line": user.contact_line, "contact_fb": user.contact_fb,
         "contact_ig": user.contact_ig, "contact_tw": user.contact_tw, "contact_info": user.contact_info
         })
    db.commit()
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user.id).update(
        {"is_active": False})
    db.commit()
    return db_user


def get_presentations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Presentation).order_by(models.Presentation.id).filter(models.Presentation.is_active).offset(
        skip).limit(limit).all()


def get_presentation(db: Session, presentation_id: int):
    return db.query(models.Presentation).filter(models.Presentation.is_active).filter(
        models.Presentation.id == presentation_id).first()


def get_presentation_by_title(db: Session, presentation_title: str):
    return db.query(models.Presentation).filter(models.Presentation.is_active).filter(
        models.Presentation.title == presentation_title).all()


def get_presentation_by_email(db: Session, email: str):
    db_right = get_right_by_email(db, email=email)
    db_presentations: list[models.Presentation] = []
    for right in db_right:
        presentation = db.query(models.Presentation).order_by(models.Presentation.id).filter(
            models.Presentation.is_active).filter(
            models.Presentation.id == right.presentation_id).first()
        db_presentations.append(presentation)
    return db_presentations


def create_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = models.Presentation(title=presentation.title, category_id=presentation.category_id)
    db.add(db_presentation)
    db.commit()
    db.refresh(db_presentation)
    return db_presentation


def edit_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = db.query(models.Presentation).filter(models.Presentation.id == presentation.id).update(
        {"title": presentation.title, "category_id": presentation.category_id, "description": presentation.description})
    db.commit()
    db_presentation = db.query(models.Presentation).filter(models.Presentation.id == presentation.id).first()
    db.refresh(db_presentation)
    return db_presentation


def delete_presentation(db: Session, presentation: schemas.PresentationCreate):
    db_presentation = db.query(models.Presentation).filter(models.Presentation.id==presentation.id).update(
        {"is_active": False})
    db_bundlepresentation = db.query(models.BundlePresentation).filter(
        models.BundlePresentation.presentation_id==presentation.id).update(
        {"is_active": False})
    db_slide = db.query(models.Slide).filter(models.Slide.presentation_id==presentation.id).update({"is_active":False})
    db.commit()
    return db_presentation


def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.is_active).filter(models.Category.id == category_id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(models.Category).filter(models.Category.is_active).filter(models.Category.title == title).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).filter(models.Category.is_active).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(title=category.title)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_slides(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Slide).order_by(models.Slide.id).filter(models.Slide.is_active).offset(skip).limit(
        limit).all()


def get_slide(db: Session, slide_id: int):
    return db.query(models.Slide).filter(models.Slide.is_active).filter(models.Slide.id == slide_id).first()


def get_slide_by_title(db: Session, slide_title: str, presentation_id):
    return db.query(models.Slide).filter(models.Slide.is_active).filter(models.Slide.title == slide_title).filter(
        models.Slide.presentation_id == presentation_id).first()


def get_slide_by_slideid(db: Session, id: int):
    return db.query(models.Slide).order_by(models.Slide.order).filter(models.Slide.is_active).filter(
        models.Slide.id == id).first()  # .first()


def get_slides_by_presentation_id(db: Session, presentation_id: int):
    return db.query(models.Slide).order_by(models.Slide.order).filter(models.Slide.is_active).filter(
        models.Slide.presentation_id == presentation_id).all()  # .first()


def create_slide(db: Session, slide: schemas.SlideCreate):
    db_slide = models.Slide(title=slide.title, presentation_id=slide.presentation_id, order=slide.order)
    db.add(db_slide)
    db.commit()
    db.refresh(db_slide)
    return db_slide


def edit_slide(db: Session, slide: schemas.Slide):
    db_slide = db.query(models.Slide).filter(models.Slide.id == slide.id).update(
        {"title": slide.title, "presentation_id": slide.presentation_id, "order": slide.order,
         "is_active": slide.is_active})
    db.commit()
    db_slide = db.query(models.Slide).filter(models.Slide.id == slide.id).first()
    db.refresh(db_slide)
    return db_slide


def delete_slide(db: Session, slide: schemas.Slide):
    db_slide = db.query(models.Slide).filter(models.Slide.id == slide.id).update(
        {"is_active": False})
    db.commit()
    return db_slide


def get_slideimage(db: Session, slide_id: int):
    return db.query(models.SlideImage).filter(models.SlideImage.is_active).filter(
        models.SlideImage.slide_id == slide_id).first()


def get_slideimage_by_presentation_id(db: Session, presentation_id: int):
    dbslide = db.query(models.Slide).order_by(models.Slide.order).filter(
        models.Slide.presentation_id == presentation_id).first()
    if dbslide is None:
        return None
    return db.query(models.SlideImage).filter(models.SlideImage.is_active).filter(
        models.SlideImage.slide_id == dbslide.id).first()


def get_slideimages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SlideImage).filter(models.SlideImage.is_active).count()  # .offset(skip).limit(limit).all()


def create_slideimage(db: Session, slideimage: schemas.SlideImageCreate):
    db_slideimage = models.SlideImage(slide_id=slideimage.slide_id, image=convertToBinaryData(slideimage.image))
    db.add(db_slideimage)
    db.commit()
    # db.refresh(db_slideimage)
    return db.query(models.SlideImage).filter(models.SlideImage.is_active).count()  # db_slideimage


def edit_slideimage(db: Session, slideimage: schemas.SlideImage):
    db_slideimage = db.query(models.SlideImage).filter(
        models.SlideImage.slide_id == slideimage.slide_id).update(
        {"image": convertToBinaryData(slideimage.image)})
    # db_slideimage = models.SlideImage(slide_id=slideimage.slide_id, image=convertToBinaryData(slideimage.image))
    db.commit()
    db_slideimage = db.query(models.SlideImage).filter(
        models.SlideImage.slide_id == slideimage.slide_id).first()
    return db_slideimage.id


def convertToBinaryData(filename):
    # image = Image.open(filename)
    # image.show()
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def get_imagerender_by_slideid(db: Session, slide_id: int):
    return db.query(models.ImageRender).filter(models.ImageRender.is_active).filter(
        models.ImageRender.slide_id == slide_id).first()


def get_imagerender_by_title(db: Session, slide_id, title: str):
    return db.query(models.ImageRender).filter(models.ImageRender.is_active).filter(
        models.ImageRender.title == title).filter(
        models.ImageRender.slide_id == slide_id).first()


def get_imagerenders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ImageRender).filter(models.ImageRender.is_active).offset(skip).limit(limit).all()


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
    db_imagerender = db.query(models.ImageRender).filter(models.ImageRender.id == imagerender.id).update(
        {"title": imagerender.title, "slide_id": imagerender.slide_id, "image_id": imagerender.image_id,
         "image_path": imagerender.image_path, "height": imagerender.height, "width": imagerender.width,
         "pos_x": imagerender.pos_x, "pos_y": imagerender.pos_y, "align": imagerender.align
         })
    db.commit()
    db_imagerender = db.query(models.ImageRender).filter(models.ImageRender.id == imagerender.id).first()
    db.refresh(db_imagerender)
    return db_imagerender


def get_textrender_by_slideid(db: Session, slide_id: int):
    return db.query(models.TextRender).filter(models.TextRender.is_active).filter(
        models.TextRender.slide_id == slide_id).first()


def get_textrenders_by_slideid(db: Session, slide_id: int):
    return db.query(models.TextRender).filter(models.TextRender.is_active).filter(
        models.TextRender.slide_id == slide_id).all()


def get_textrender_by_title(db: Session, title: str, slide_id):
    return db.query(models.TextRender).filter(models.TextRender.is_active).filter(
        models.TextRender.title == title).filter(
        models.TextRender.slide_id == slide_id).first()


def get_textrenders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TextRender).filter(models.TextRender.is_active).offset(skip).limit(limit).all()


def create_textrender(db: Session, textrender: schemas.TextRenderCreate):
    db_textrender = models.TextRender(title=textrender.title, slide_id=textrender.slide_id, text=textrender.text,
                                      font=textrender.font, size=textrender.size, pos_x=textrender.pos_x,
                                      pos_y=textrender.pos_y, align=textrender.align, anchor=textrender.anchor,
                                      color_r=textrender.color_r,
                                      color_g=textrender.color_g, color_b=textrender.color_b)
    db.add(db_textrender)
    db.commit()
    db.refresh(db_textrender)
    return db_textrender


def edit_textrender(db: Session, textrender: schemas.TextRenderCreate):
    db_textrender = db.query(models.TextRender).filter(models.TextRender.id == textrender.id).update(
        {"title": textrender.title, "slide_id": textrender.slide_id, "text": textrender.text, "font": textrender.font,
         "size": textrender.size, "pos_x": textrender.pos_x, "pos_y": textrender.pos_y, "align": textrender.align,
         "anchor": textrender.anchor, "color_r": textrender.color_r,
         "color_g": textrender.color_g, "color_b": textrender.color_b})
    db.commit()
    db_textrender = db.query(models.TextRender).filter(models.TextRender.id == textrender.id).first()
    db.refresh(db_textrender)
    return db_textrender


def get_orders_by_bundleid(db: Session, bundle_id: int):
    return db.query(models.Order).filter(models.Order.is_active).filter(models.Order.bundle_id == bundle_id).all()


def get_orders_by_email(db: Session, email: str):
    return db.query(models.Order).filter(models.Order.is_active).filter(models.Order.user_email == email).all()


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).filter(models.Order.is_active).offset(skip).limit(limit).all()


def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(bundle_id=order.bundle_id, user_email=order.user_email, order_date=order.order_date)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def create_order_right(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(bundle_id=order.bundle_id, user_email=order.user_email, order_date=order.order_date)
    db.add(db_order)
    print("add order success: " + order.user_email)
    db_user = db.query(models.User).filter(models.User.is_active).filter(models.User.email == order.user_email).first()
    if db_user is None:
        db_user = models.User(email=order.user_email, role='user', firstname='firstname', lastname='lastname',
                              contact_no='contact_no', contact_line='contact_line', contact_fb='contact_fb',
                              contact_ig='contact_ig', contact_tw='contact_tw', contact_info='contact_info',
                              is_active=True)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    db_bundlepresentation = db.query(models.BundlePresentation).filter(
        models.BundlePresentation.bundle_id == order.bundle_id).all()
    db_right = db.query(models.Right).first()
    for bp in db_bundlepresentation:
        print("bd loop")
        db_right = models.Right(presentation_id=bp.presentation_id, user_id=db_user.id, order_date=order.order_date)
        db.add(db_right)
    db.commit()
    db.refresh(db_right)
    db.refresh(db_order)
    return db_order


def get_right_by_userid(db: Session, user_id: int):
    return db.query(models.Right).filter(models.Right.is_active).filter(models.Right.user_id == user_id).all()


def get_right_by_userid_presentationid(db: Session, user_id: int, presentation_id: int):
    return db.query(models.Right).filter(models.Right.is_active).filter(models.Right.user_id == user_id).filter(
        models.Right.presentation_id == presentation_id).first()


def get_right_by_email(db: Session, email: str):
    db_user = get_user_by_email(db, email=email)
    return db.query(models.Right).filter(models.Right.is_active).filter(models.Right.user_id == db_user.id).all()


def get_right(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Right).filter(models.Right.is_active).offset(skip).limit(limit).all()


def create_right(db: Session, right: schemas.RightCreate):
    db_right = models.Right(presentation_id=right.presentation_id, user_id=right.user_id, order_date=right.order_date)
    db.add(db_right)
    db.commit()
    db.refresh(db_right)
    return db_right


def get_image(db: Session, image_id: int):
    return db.query(models.LogoImage).filter(models.LogoImage.is_active).filter(models.LogoImage.id == image_id).first()


def get_image_by_user_id(db: Session, user_id: int):
    return db.query(models.LogoImage).filter(models.LogoImage.is_active).filter(
        models.LogoImage.user_id == user_id).first()


def get_image_by_email(db: Session, email: str):
    dbuser = db.query(models.User).filter(models.User.is_active).filter(models.User.email == email).first()
    if dbuser is None:
        return None
    return db.query(models.LogoImage).filter(models.LogoImage.is_active).filter(
        models.LogoImage.user_id == dbuser.id).first()


def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LogoImage).filter(models.LogoImage.is_active).count()  # .offset(skip).limit(limit).all()


def create_image(db: Session, logoimage: schemas.LogoImageCreate):
    db_changeimagelog = models.ChangeImageLog(user_id=logoimage.user_id,
                                              when=date.today().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(db_changeimagelog)
    db.commit()
    db_image = models.LogoImage(user_id=logoimage.user_id, image=convertToBinaryData(logoimage.image))
    db.add(db_image)
    db.commit()
    # db.refresh(db_slideimage)
    return db.query(models.LogoImage).count()  # db_slideimage


def edit_image(db: Session, logoimage: schemas.LogoImageCreate):
    db_image = db.query(models.LogoImage).filter(models.LogoImage.user_id == logoimage.user_id).update(
        {"image": convertToBinaryData(logoimage.image)})
    db.commit()
    db_image = db.query(models.LogoImage).filter(models.LogoImage.user_id == logoimage.user_id).first()
    db.refresh(db_image)
    return db_image


def edit_image_by_email(email: str, db: Session, logoimage: schemas.LogoImageCreate):
    db_user = db.query(models.User).filter(models.User.email == email)
    db_image = db.query(models.LogoImage).filter(models.LogoImage.user_id == db_user.user_id).update(
        {"image": convertToBinaryData(logoimage.image)})
    db.commit()
    db_image = db.query(models.LogoImage).filter(models.LogoImage.user_id == logoimage.user_id).first()
    db.refresh(db_image)
    return db_image


def get_changelog(db: Session, id: int):
    return db.query(models.ChangeLog).filter(models.ChangeLog.id == id).first()


def get_changelog_by_userid(db: Session, user_id: int):
    return db.query(models.ChangeLog).filter(models.ChangeLog.user_id == user_id).all()


def create_changelog(db: Session, changelog: schemas.ChangeLog):
    db_changelog = models.ChangeLog(user_id=changelog.user_id, when=changelog.when, table=changelog.table,
                                    old=changelog.old, new=changelog.new, remark=changelog.remark)
    db.add(db_changelog)
    db.commit()
    db.refresh(db_changelog)
    return db_changelog


def get_changeimagelog(db: Session, id: int):
    return db.query(models.ChangeImageLog).filter(models.ChangeImageLog.id == id).first()


def get_changeimagelog_by_userid(db: Session, user_id: int):
    return db.query(models.ChangeImageLog).filter(models.ChangeImageLog.user_id == user_id).all()


def create_changeimagelog(db: Session, changeimagelog: schemas.ChangeImageLog):
    db_changeimagelog = models.ChangeImageLog(user_id=changeimagelog.user_id, when=changeimagelog.when,
                                              new=convertToBinaryData(changeimagelog.new), remark=changeimagelog.remark)
    db.add(db_changeimagelog)
    db.commit()
    db.refresh(db_changeimagelog)
    return db_changeimagelog.id
