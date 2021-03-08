from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.db_models.car import CarDB
from models.car import CarIN
from typing import List
from datetime import date

"""
       INTEGER1 -eq INTEGER2
              INTEGER1 is equal to INTEGER2

       INTEGER1 -ge INTEGER2
              INTEGER1 is greater than or equal to INTEGER2

       INTEGER1 -gt INTEGER2
              INTEGER1 is greater than INTEGER2

       INTEGER1 -le INTEGER2
              INTEGER1 is less than or equal to INTEGER2

       INTEGER1 -lt INTEGER2
              INTEGER1 is less than INTEGER2

       INTEGER1 -ne INTEGER2
              INTEGER1 is not equal to INTEGER2
"""
def get_data(db: Session):
    return db.query(CarDB).all()

def get_car_by_specs(db: Session, car_info: dict):
    car_name = car_info.get("car_name", "")
    mileage = car_info.get("mileage", None)
    exterior = car_info.get("exterior", "")
    price = car_info.get("price", None)

    # simple comma separated constraints in filter apply AND
    return db.query(CarDB).filter(CarDB.car_name == car_name, CarDB.mileage == mileage, CarDB.exterior == exterior,
                                  CarDB.price == price).all()

def car_exists_in_db(db: Session, incoming_car: CarDB):
    """
    :return: bool
    """
    car_name = incoming_car.car_name
    mileage = incoming_car.mileage
    exterior = incoming_car.exterior
    price = incoming_car.price
    # print(f'type: {type(incoming_car)} ')
    # print(f'{incoming_car}')
    res = db.query(CarDB).filter(CarDB.car_name == car_name, CarDB.mileage == mileage, CarDB.exterior == exterior,
                                 CarDB.price == price).all()

    # Prob: If old car saved didn't have an image.
    # On next run the incoming car object might have image saved.
    if len(res):
        one_car = res[0]
        if one_car.img_path == "":
            return False
        else:
            return True
    else:
        return False


def create(db: Session, *, car_in: CarIN, autocommit: bool = True):
    """
    Before adding into DB makes sure car doesn't already exists in DB.
    :param db:
    :param car_in:
    :param autocommit: This is here to introduce transaction type effect. If True each car_in passed is committed to DB
    before moving to next, if False all car_ins are kinda stagged and commit outside this function via: db.commit()
    :return:
    """
    car_in_data = jsonable_encoder(car_in)
    # car = CarDB(**car_in_data, id=None)
    car = CarDB(**car_in_data)

    if not car_exists_in_db(db, car):
        db.add(car)
        if autocommit:
            db.commit()
            db.refresh(car)
        else:
            db.flush()
        car_ret = jsonable_encoder(car)
        car_ret["in_db"] = "Added"
    else:
        car_ret = jsonable_encoder(car)
        car_ret["in_db"] = "Existed"

    return car_ret

# Old Function
# def create(db: Session, car_name="", body_style="", mileage=None, exterior="", drivetrain="", transmission="",
#                engine="", city="", price=None, vin="", stock="", website="", entry_date=None):
#
#     car = CarDB(car_name=car_name, body_style=body_style, mileage=mileage, exterior=exterior, drivetrain=drivetrain,
#               transmission=transmission, engine=engine, city=city, price=price, vin=vin, stock=stock, website=website,
#               entry_date=entry_date)
#     db.add(car)
#     db.commit()
#     db.refresh(car)
#     return car

def create_car_dict(db: Session, car_info: dict, website: str = ""):
    """
    :param db: Local Session with database
    :param car_info: Dictionary containing car's information
    :param website: Name of the website from which car's information is extracted
    :return CarDB: car ORM object
    """
    # Check for duplication
    cars_list = get_car_by_specs(db, car_info)

    if not len(cars_list):
        # Add car
        car = create_car(db, car_name=car_info.get("car_name", ""), body_style=car_info.get("body_style", ""),
                         mileage=car_info.get("mileage", None), exterior=car_info.get("exterior", ""),
                         drivetrain=car_info.get("drivetrain", ""), transmission=car_info.get("transmission", ""),
                         engine=car_info.get("engine", ""), city=car_info.get("city", ""),
                         price=car_info.get("price", None), stock="", website=website,
                         entry_date=car_info.get("date", None))
        return car
    else:
        return "ok car not created"
    # return "ok"

def get_car_filter_date(db: Session, date_gt: date = None, limit: int = None) -> List[CarDB]:
    queries = []
    if date_gt:
        print(f'date_gt: {date_gt}')
        queries.append( func.DATE(CarDB.entry_date) > date_gt )
    return db.query(CarDB).filter(*queries).limit(limit).all()

def get_car(db: Session, name: str = "", price_ge: int = None, price_le: int = None,
            mileage_ge: int = None, mileage_le: int = None,
            date_ge: date = None, date_le: date = None, limit: int = None) -> List[CarDB]:

    queries = [ CarDB.car_name.like(f'%{name}%') ]
    if price_ge:
        queries.append( CarDB.price >= price_ge )
    if price_le:
        queries.append( CarDB.price <= price_le )
    if mileage_ge:
        queries.append( CarDB.mileage >= mileage_ge )
    if mileage_le:
        queries.append( CarDB.mileage <= mileage_le )
    if date_ge:
        queries.append( func.DATE(CarDB.entry_date) >= date_ge )
    if date_le:
        queries.append( func.DATE(CarDB.entry_date) <= date_le )

    return db.query(CarDB).filter(*queries).limit(limit).all()

# def get_all_orders(
#         db_session: Session,
#         *,
#         distribution_id: int = None,
#         order_date: date = None,
#         order_ids: List[int] = None,
#         pricing_ids: List[int],
#         order_status: OrderStatus = None,
#         price_less_than: float = None,
#         limit: int = None,
#         offset: int = None # Sqlalchemy would accept None for offset and limit and assume it to be 0
# ) -> List[Secondary_orderDB]:
#     queries = []
#     if order_date: # Filtering on a date field (datetime to date comparison)
#         queries.append(func.DATE(Secondary_orderDB.date) == order_date)
#     if distribution_id: # Filtering on a integer field
#         queries.append(Secondary_orderDB.fk_distribution == distribution_id)
#     if order_ids: # Using Sql's IN cluase (Gets the matching ids :D)
#         queries.append(Secondary_orderDB.id.in_(order_ids))
#     if order_status: # Simple string comparison
#         queries.append(Secondary_orderDB.status == order_status)
#     if price_less_than:
#         queries.append(Secondary_orderDB.price < price_less_than)
#
#     orders = db_session.query(Secondary_orderDB).filter(*queries).limit(limit).offset(offset).all()
#     return orders
