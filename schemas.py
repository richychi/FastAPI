#
from pydantic import BaseModel


class PresentationBase(BaseModel):
    title: str
    category_id: int


class PresentationCreate(PresentationBase):
    pass


class Presentation(PresentationBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class PresentationRename(BaseModel):
    new_title: str


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    title: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class SlideBase(BaseModel):
    title: str
    presentation_id: int


class SlideCreate(SlideBase):
    pass


class Slide(SlideBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class SlideImageBase(BaseModel):
    slide_id: int
    image: bytes


class SlideImageCreate(SlideImageBase):
    pass


class SlideImage(SlideImageBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class ImageRenderBase(BaseModel):
    title: str
    slide_id: int


class ImageRenderCreate(ImageRenderBase):
    pass


class ImageRender(ImageRenderBase):
    id: int
    is_active: bool
    pos_x: int
    pos_y: int
    width: int
    height: int
    align: int

    class Config:
        orm_mode = True


class TextRenderBase(BaseModel):
    title: str
    slide_id: int
    text: str
    font: str = 'Tahoma'
    size: int = 14
    pos_x: int = 20
    pos_y: int = 20
    align: int = 4
    color_r: int = 255
    color_g: int = 255
    color_b: int = 255


class TextRenderCreate(TextRenderBase):
    pass


class TextRender(TextRenderBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
