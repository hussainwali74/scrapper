from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

"""
# Car table for testing
CREATE TABLE car_dev (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    mileage VARCHAR,
    price INTEGER
);
ALTER TABLE cars ADD COLUMN price INTEGER;
"""

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    car_name = Column(String)
    body_style = Column(String)
    mileage = Column(String)
    exterior = Column(String)
    drivetrain = Column(String)
    transmission = Column(String)
    engine = Column(String)
    city = Column(String)
    price = Column(String)
    vin = Column(String)
    stock = Column(String)
    website = Column(String)

    def __init__(self, car_name="", body_style="", mileage="", exterior="", drivetrain="", transmission="", engine="",
                 city="", price=None, vin="", stock="", website=""):
        self.car_name = car_name
        self.body_style = body_style
        self.mileage = mileage
        self.exterior = exterior
        self.drivetrain = drivetrain
        self.transmission = transmission
        self.engine = engine
        self.city = city
        self.price = price
        self.vin = vin
        self.stock = stock
        self.website = website

    def __repr__(self):
        return f"<Car(car_name: {self.car_name}, mileage: {self.mileage}, exterior: {self.exterior}, " \
               f"drivetrain: {self.drivetrain}, transmission: {self.transmission}, engine: {self.engine}, " \
               f"city: {self.city}, price: {self.price}, website: {self.website})"
