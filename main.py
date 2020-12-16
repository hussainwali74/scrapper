from fastapi import Depends, FastAPI

from database import SessionLocal, engine, Base
from models import Car

from sqlalchemy.orm import Session
import crud

from web_scrapper import get_car_info_from_web

Base.metadata.create_all(bind=engine)

app = FastAPI()

# car1 = Car(carName="toyota")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root(db: Session = Depends(get_db)):
    res = crud.get_data(db)
    res = res[-10:]
    return res
    # return {"message": "Hello World"}


@app.get("/add-cars")
async def add_cars(db: Session = Depends(get_db)):

    # res = crud.create_car(db, "toyota", f"12245km", "black", "4x4", "auto", "vti",
    # "uo", "yes", "https://www.google.com")

    url_list = ['https://www.regalmotorsltd.com/used/used-vehicle-inventory.html',
                'https://www.junctionmotors.com/used/used-vehicle-inventory.html?reset=1',
                'https://www.northstarfordsalescalgary.ca/used/used-vehicle-inventory.html?reset=1',
                'https://www.woodridgeford.com/used/pg/1',
                'https://www.zarownymotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
                'https://www.fourlaneford.com/used-cars-just-south-of-red-deer-in-innisfail?sort-by=price&direction=high-to-low',
                'https://www.marlboroughford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc',
                'https://www.universalford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc&page=1',
                'https://www.westlockford.com/inventory/search?stock_type=Used&page=1&page_length=100']

    url_list = ['https://www.regalmotorsltd.com/used/used-vehicle-inventory.html']
    done_for = []
    for url in url_list:
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            print(one_car)
            crud.create_car_dict(db, one_car, website=url)

    return done_for


@app.get("/test-dup")
async def test_duplicate_entry( db: Session = Depends(get_db) ):
    car_info = {"car_name": "toyota",
                "mileage": "12245km",
                "exterior": "white",
                "drivetrain": "4x4",
                "transmission": "auto",
                "engine": "vti"}
    res = crud.create_car_dict(db, car_info, "xyz site")
    return res


if __name__ == '__main__':
    pass
