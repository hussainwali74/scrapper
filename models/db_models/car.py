from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import func
from sqlalchemy import TIMESTAMP
from database import Base

"""
# For deleting a table
DROP TABLE cars; 
# For emptying the table
TRUNCATE cars;
# Car table for testing
CREATE TABLE car_dev (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    mileage VARCHAR,
    price INTEGER
);
ALTER TABLE cars ADD COLUMN price INTEGER;

INSERT INTO car_dev(name, mileage, price, entry_date) VALUES ('kia', '213234', 229910, '2020-10-01');
"""

class CarDB(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    car_name = Column(String)
    body_style = Column(String)
    mileage = Column(Integer)
    exterior = Column(String)
    drivetrain = Column(String)
    transmission = Column(String)
    engine = Column(String)
    city = Column(String)
    price = Column(Integer)
    vin = Column(String)
    stock = Column(String)
    website = Column(String)
    entry_date = Column(TIMESTAMP, default=func.now())
    img_link = Column(String)
    # updated_at = Column(TIMESTAMP, nullable=False,
    # server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __init__(self, car_name="", body_style="", mileage=None, exterior="", drivetrain="", transmission="", engine="",
                 city="", price=None, vin="", stock="", website="", entry_date=None, img_link=""):
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
        self.entry_date = entry_date
        self.img_link = img_link

    def __repr__(self):
        return f"<Car(id: {self.id}, car_name: {self.car_name}, mileage: {self.mileage}, exterior: {self.exterior}, " \
               f"drivetrain: {self.drivetrain}, transmission: {self.transmission}, engine: {self.engine}, " \
               f"city: {self.city}, price: {self.price}, website: {self.website}, img_path: {self.img_link})"
