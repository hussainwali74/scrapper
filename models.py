from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    car_name = Column(String)
    mileage = Column(String)
    exterior = Column(String)
    drivetrain = Column(String)
    transmission = Column(String)
    engine = Column(String)
    vin = Column(String)
    stock = Column(String)
    website = Column(String)

    def __init__(self, car_name, mileage, exterior, drivetrain, transmission, engine, vin, stock, website):
        self.car_name = car_name
        self.mileage = mileage
        self.exterior = exterior
        self.drivetrain = drivetrain
        self.transmission = transmission
        self.engine = engine
        self.vin = vin
        self.stock = stock
        self.website = website

    def __repr__(self):
        return f"<Car(car_name: {self.car_name}, mileage: {self.mileage}, exterior: {self.exterior}, " \
               f"drivetrain: {self.drivetrain}, transmission: {self.transmission}, engine: {self.engine}, " \
               f"vin: {self.vin}, stock: {self.stock}, website: {self.website})"
