#
import datetime
from pydantic import BaseModel


class PresentationBase(BaseModel):
    id: int
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
    id: int
    email: str
    role: str
    firstname: str = ''
    lastname: str = ''
    contact_no: str = ''
    contact_line: str = ''
    contact_fb: str = ''
    contact_ig: str = ''
    contact_tw: str = ''
    contact_info: str = ''


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
    order: int


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


class LogoImageBase(BaseModel):
    user_id: int
    image: bytes


class LogoImageCreate(LogoImageBase):
    pass


class LogoImage(LogoImageBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class ImageRenderBase(BaseModel):
    id: int
    title: str
    slide_id: int
    image_path: str = './api/presentation/images/'
    image_id: int = 1
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
    id: int
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


class OrderBase(BaseModel):
    order_date: datetime.datetime = datetime.datetime.today()  # .strftime("%Y-%d-%m %H:%M:%S")
    user_email: str
    bundle_id: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class RightBase(BaseModel):
    id: int
    order_date: datetime.datetime = datetime.datetime.today()  # .strftime("%Y-%d-%m %H:%M:%S")
    user_id: int
    presentation_id: int


class RightCreate(RightBase):
    pass


class Right(RightBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class BundleBase(BaseModel):
    id: int
    title: str
    price: int
    start_date: datetime.datetime = datetime.datetime.today()  # .strftime("%Y-%d-%m %H:%M:%S")
    # end_date: datetime.datetime


class BundleCreate(BundleBase):
    pass


class Bundle(BundleBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class BundlePresentationBase(BaseModel):
    bundle_id: int
    presentation_id: int


class BundlePresentationCreate(BundlePresentationBase):
    pass


class BundlePresentation(BundlePresentationBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class ChangeLog(BaseModel):
    id: int
    user_id: int
    when: datetime.datetime = datetime.datetime.today()
    table: str
    old: str
    new: str
    remark: str = ""

    class Config:
        orm_mode = True


class ChangeImageLog(BaseModel):
    id: int
    user_id: int
    when: datetime.datetime = datetime.datetime.today()
    new: bytes
    remark: str

    class Config:
        orm_mode = True
