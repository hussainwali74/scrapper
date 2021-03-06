from datetime import datetime

from pydantic import BaseModel, Field


class Car(BaseModel):
    id: int
    car_name: str
    car_page_link: str
    body_style: str
    mileage: int
    exterior: str  # = Field(..., gt=0, lt=450)  # means str 0 < length < 450
    drivetrain: str
    transmission = str
    engine = str
    city = str
    price = int
    vin = str
    stock = str
    website = str
    entry_date: datetime
    img_link: str

    class Config:
        orm_mode = True


class CarIN(BaseModel):
    car_name: str
    car_page_link: str
    body_style: str
    mileage: int
    exterior: str  # = Field(..., gt=0, lt=450)
    drivetrain: str
    transmission: str
    engine: str
    city: str
    price: int
    vin: str
    stock: str
    website: str
    entry_date: datetime
    img_link: str

    class Config:
        orm_mode = True
