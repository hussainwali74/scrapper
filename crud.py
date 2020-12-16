from sqlalchemy.orm import Session
from models import Car

def get_data(db: Session):
    return db.query(Car).all()

def get_car_by_specs(db: Session, car_info: dict):
    car_name = car_info.get("car_name", "")
    mileage = car_info.get("mileage", "")
    exterior = car_info.get("exterior", "")

    # simple comma separated constraints in filter apply AND
    return db.query(Car).filter(Car.car_name == car_name, Car.mileage == mileage, Car.exterior == exterior).all()

def create_car(db: Session, car_name="", body_style="", mileage="", exterior="", drivetrain="", transmission="",
               engine="", city="", price=None, vin="", stock="", website=""):

    car = Car(car_name=car_name, body_style=body_style, mileage=mileage, exterior=exterior, drivetrain=drivetrain,
              transmission=transmission, engine=engine, city=city, price=price, vin=vin, stock=stock, website=website)
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
    # Check for duplication
    cars_list = get_car_by_specs(db, car_info)

    if not len(cars_list):
        # Add car
        car = create_car(db, car_name=car_info.get("car_name", ""), body_style=car_info.get("body_style", ""),
                         mileage=car_info.get("mileage", ""), exterior=car_info.get("exterior", ""),
                         drivetrain=car_info.get("drivetrain", ""), transmission=car_info.get("transmission", ""),
                         engine=car_info.get("engine", ""), city=car_info.get("city", ""),
                         price=car_info.get("price", None), stock="", website=website)
        return car
    else:
        return "ok car not created"
    # return "ok"
