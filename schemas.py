#
from pydantic import BaseModel


class PresentationBase(BaseModel):
    title: str
    description: str = 'description'
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
    role: str


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
    image_path: str = './api/presentation/images/'
    pos_x: int = 1600
    pos_y: int = 20
    width: int = 200
    height: int = 200
    align: str = 'left'


class ImageRenderCreate(ImageRenderBase):
    pass


class ImageRender(ImageRenderBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class TextRenderBase(BaseModel):
    title: str
    slide_id: int
    text: str
    font: str = 'Thonburi.ttf'
    size: int = 40
    pos_x: int = 20
    pos_y: int = 20
    anchor: str = 'la'
    align: str = 'left'
    color_r: int = 0
    color_g: int = 0
    color_b: int = 0


class TextRenderCreate(TextRenderBase):
    pass


class TextRender(TextRenderBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
