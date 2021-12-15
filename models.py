#
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, LargeBinary  # , BLOB, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default='user')
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="users")


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
    orders = relationship("Order", back_populates="presentations")


class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"))

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

    slide = relationship("Slide", back_populates="image_render")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    presentation_id = Column(Integer, ForeignKey("presentations.id"))

    users = relationship("User", back_populates="orders")
    presentations = relationship("Presentation", back_populates="orders")
