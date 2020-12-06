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
    print(res)
    return {"message": res}
    # return {"message": "Hello World"}


@app.get("/add-cars")
async def add_cars(db: Session = Depends(get_db)):
    # res = crud.create_car(db, "toyota", f"12245km", "black", "4x4", "auto", "vti", "uo", "yes", "https://www.google.com")

    website = 'https://www.regalmotorsltd.com/used/used-vehicle-inventory.html'
    res = get_car_info_from_web()
    for one_car in res:
        print(one_car)
        added_car = crud.create_car_dict(db, one_car, website=website)
    return res


if __name__ == '__main__':
    pass
