#
import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, LargeBinary  # , BLOB, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default='user')
    firstname = Column(String, default='')
    lastname = Column(String, default='')
    contact_no = Column(String, default='')
    contact_line = Column(String, default='')
    contact_fb = Column(String, default='')
    contact_ig = Column(String, default='')
    contact_tw = Column(String, default='')
    contact_info = Column(String, default='')
    is_active = Column(Boolean, default='')

    rights = relationship("Right", back_populates="users")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    presentations = relationship("Presentation", back_populates="category")


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="description")
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="presentations")
    slides = relationship("Slide", back_populates="presentation")
    bundle_presentations = relationship("BundlePresentation", back_populates="presentations")
    rights = relationship("Right", back_populates="presentations")


class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"))
    order = Column(Integer)

    presentation = relationship("Presentation", back_populates="slides")
    text_render = relationship("TextRender", back_populates="slide")
    image_render = relationship("ImageRender", back_populates="slide")
    slideimage = relationship("SlideImage", back_populates="slide")


class SlideImage(Base):
    __tablename__ = "slideimages"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(LargeBinary)
    slide_id = Column(Integer, ForeignKey("slides.id"))
    is_active = Column(Boolean, default=True)

    slide = relationship("Slide", back_populates="slideimage")


class TextRender(Base):
    __tablename__ = "text_renders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    text = Column(String, index=True)
    font = Column(String, default='Tahoma')
    size = Column(Integer, default=14)
    pos_x = Column(Integer, default=20)
    pos_y = Column(Integer, default=20)
    anchor = Column(String, default='la')
    align = Column(String, default='left')
    color_r = Column(Integer, default=255)
    color_g = Column(Integer, default=255)
    color_b = Column(Integer, default=255)
    slide_id = Column(Integer, ForeignKey("slides.id"))

    slide = relationship("Slide", back_populates="text_render")


class ImageRender(Base):
    __tablename__ = "image_renders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    image_path = Column(String, default='./api/presentation/images/')
    pos_x = Column(Integer, default=1600)
    pos_y = Column(Integer, default=20)
    width = Column(Integer, default=200)
    height = Column(Integer, default=200)
    align = Column(String, default='left')
    slide_id = Column(Integer, ForeignKey("slides.id"))
    image_id = Column(Integer, ForeignKey("logo.id"))

    slide = relationship("Slide", back_populates="image_render")
    logoimage = relationship("LogoImage", back_populates="image_renders")


class LogoImage(Base):
    __tablename__ = "logo"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(LargeBinary)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    image_renders = relationship("ImageRender", back_populates="logoimage")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.datetime.today())
    is_active = Column(Boolean, default=True)
    user_email = Column(String, index=True)
    bundle_id = Column(Integer, ForeignKey("bundles.id"))

    bundle = relationship("Bundle", back_populates="order")


class Right(Base):
    __tablename__ = "right"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.datetime.today())
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    presentation_id = Column(Integer, ForeignKey("presentations.id"))

    users = relationship("User", back_populates="rights")
    presentations = relationship("Presentation", back_populates="rights")


class Bundle(Base):
    __tablename__ = "bundles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Integer, default=0)
    start_date = Column(DateTime, default=datetime.datetime.today())
    # end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    bundle_presentations = relationship("BundlePresentation", back_populates="bundles")
    order = relationship("Order", back_populates="bundle")


class BundlePresentation(Base):
    __tablename__ = "bundle_presentations"

    id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(Integer, ForeignKey("bundles.id"))
    presentation_id = Column(Integer, ForeignKey("presentations.id"))
    is_active = Column(Boolean, default=True)

    bundles = relationship("Bundle", back_populates="bundle_presentations")
    presentations = relationship("Presentation", back_populates="bundle_presentations")


class ChangeLog(Base):
    __tablename__ = "change_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    when = Column(DateTime, default=datetime.datetime.today())
    table = Column(String, index=True)
    old = Column(String, index=True)
    new = Column(String, index=True)
    remark = Column(String)


class ChangeImageLog(Base):
    __tablename__ = "changeimage_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    when = Column(DateTime, default=datetime.datetime.today())
    new = Column(LargeBinary)
    remark = Column(String)
