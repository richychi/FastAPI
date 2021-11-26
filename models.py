from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, defaultload, relation
from sqlalchemy.sql.expression import null

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=True)

    presentations = relationship("Presentation", back_populates="category")


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="presentations")
    slides = relationship("Slide", back_populates="presentation")
    orders = relationship("Order", back_populates="presentation")


class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"))

    presentation = relationship("Presentation", back_populates="slides")
    text_renders = relationship("TextRender", back_populates="slide")
    image_renders = relationship("ImageRender", back_populates="slide")


class TextRender(Base):
    __tablename__ = "text_renders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=True)
    text = Column(String, index=False)
    font = Column(String)
    size = Column(Integer)
    pos_x = Column(Integer)
    pos_y = Column(Integer)
    align = Column(String)
    slide_id = Column(Integer, ForeignKey("slides.id"))

    slide = relationship("Slide", back_populates="text_renders")


class ImageRender(Base):
    __tablename__ = "image_renders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=True)
    image_path = Column(String)
    pos_x = Column(Integer)
    pos_y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    align = Column(String)
    slide_id = Column(Integer, ForeignKey("slides.id"))

    slide = relationship("Slide", back_populates="image_renders")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    presentation_id = Column(Integer, ForeignKey("presentations.id"))

    user = relationship("User", back_populates="orders")
    presentation = relationship("Presentation", back_populates="orders")
