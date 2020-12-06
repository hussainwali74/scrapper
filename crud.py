from sqlalchemy.orm import Session
from models import Car

def get_data(db: Session):
    return db.query(Car).all()

def create_car(db: Session, car_name, mileage, exterior, drivetrain, transmission, engine, vin="",
               stock="", website=""):

    car = Car(car_name, mileage, exterior, drivetrain, transmission, engine, vin, stock, website)
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

def create_car_dict(db: Session, car_info: dict, website: str = ""):
    """
    :param db: Local Session with database
    :param car_info: Dictionary containing car's information
    :param website: Name of the website from which car's information is extracted
    :return Car: car ORM object
    """
    car = create_car(db, car_name=car_info["car_name"], mileage=car_info["mileage"],
                     exterior=car_info["exterior"], drivetrain=car_info["drivetrain"],
                     transmission=car_info["transmission"], engine=car_info["engine"],
                     stock="", website=website)
    return car
