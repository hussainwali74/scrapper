from fastapi import Depends, APIRouter

from database import SessionLocal, engine, Base, get_db
from models.db_models.car import CarDB

from sqlalchemy.orm import Session
import crud

from web_scrapper import get_car_info_from_web
from datetime import date

Base.metadata.create_all(bind=engine)


router = APIRouter()
# car1 = Car(carName="toyota")

@router.get("/")
async def root(db: Session = Depends(get_db)):
    res = crud.get_data(db)
    res = res[-10:]
    return res
    # return {"message": "Hello World"}


@router.get("/add-cars")
async def add_cars(db: Session = Depends(get_db)):
    """ Add cars from websites to DB """
    # res = crud.create_car(db, "toyota", f"12245km", "black", "4x4", "auto", "vti",
    # "uo", "yes", "https://www.google.com")

    url_list = [
        # 'https://www.regalmotorsltd.com/used/used-vehicle-inventory.html',
        # 'https://www.junctionmotors.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.northstarfordsalescalgary.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.collegefordlincoln.com/used/preowned-inventory.html?reset=1',
        # 'http://www.truenorthford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.lambford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.metroford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.cslford.ca/used/used-vehicle-inventory.html?reset=2',
        # 'https://www.norrisford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.patriciafordsales.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.castleford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.collegefordtaber.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.westergardford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.royalford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.jubileeford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.senchuk.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.centennialford.sk.ca/used/used-vehicle-inventory.html',
        # 'https://www.formomotors.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.meritford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.twowayservice.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.northlandford.mb.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.rhinelandcar.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.steeltownford.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.gimliford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.hometownford.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.kelleherforddauphin.com/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.metcalfesgarage.ca/used/used-vehicle-inventory.html?reset=1',
        # 'https://www.roblinfordsales.com/used/used-vehicle-inventory?reset=1',
        # 'https://www.virdenford.ca/pre-owned/pre-owned-vehicle-inventory.html?reset=1',
        'https://www.westwardford.com/used/used-vehicle-inventory.html?reset=1',

        # 'https://www.woodridgeford.com/used/',
        # 'https://www.okotoksford.com/used/',
        # 'https://www.advantageford.ca/used/',
        # 'https://www.zarownymotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
        # 'https://www.westlockford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        # 'https://www.griffithsford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC&query=',
        # 'https://www.rainbowford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC',
        # 'https://www.bigmford.com/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC',
        # 'https://www.jerryford.com/inventory/used-inventory?stock_type=Used&page=1&page_length=100',
        # 'https://www.draytonvalleyford.com/inventory/search?page=1&page_length=100&stock_type=Used',
        # 'https://www.harwoodford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        # 'https://www.fourlaneford.com/used-cars-just-south-of-red-deer-in-innisfail?sort-by=price&direction=high-to-low',
        # 'https://www.aspenford.ca/used-cars-stettler-ab',
        # 'https://www.webbsford.com/used-inventory',
        # 'https://www.suncityford.ca/medicine-hat-used-cars',
        # 'https://www.marlboroughford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc',
        # 'https://www.universalford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc&page=1',

        # 'https://www.camclarkfordairdrie.com/vehicles/2020/ford/expedition/olds/ab/47305249/?sale_class=used',
        # 'https://www.integrityford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        # 'https://www.moosejawfordsales.com/vehicles/used?view=grid&sc=used',
        # 'https://www.bennettdunlopford.com/vehicles/used?st=price,asc&view=grid&sc=used',
        # 'https://www.rivercityford.ca/vehicles/used/?st=price,desc&view=grid&sc=used',

        # 'https://www.zenderford.com/vehicles/used/?view=grid&sc=used&st=price,desc',
        # 'https://www.boundaryford.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        # 'https://www.denhamford.ca/vehicles/used/?sc=used&st=price,desc&view=grid',
        # 'https://www.maclinfordcalgary.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        # 'https://www.legacyfordponoka.ca/vehicles/used/?view=grid&sc=used',
        # 'https://www.legacyfordrimbey.ca/vehicles/used/?view=grid&sc=used',
        # 'https://www.vegford.ca/vehicles/used/?v1=All&view=grid&sc=used',
        # 'https://www.vickarford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        # 'https://www.mid-townford.com/vehicles/used/?sc=used&st=price,desc&view=grid',
        # Multi-page
        # 'https://www.greatplainsford.com/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',

        # 'https://www.highriverford.com/used-cars-high-river-ab?sort=Sfield_Price&direction=desc',
        # 'https://www.hansenford.ca/inventory/used-vehicles/price-40000--/srp-page-1/',
        # 'https://www.windsorford.com/inventory/Used/?page=1',
        # 'http://www.northstarfordcarsandtrucks.com/used/used-vehicle-inventory.html',
        # 'https://www.strathmoreford.com/used-inventory/index.htm?start=0',
        # 'https://www.revolutionford.com/used-inventory/page/1',
    ]
    # url_list = ['https://www.regalmotorsltd.com/used/used-vehicle-inventory.html']
    done_for = []
    for url in url_list:
        print(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            print(one_car)
            car_return = crud.create(db, car_in=one_car, autocommit=True)
            print(f'Car ka status in DB: {car_return["in_db"]}')
            # crud.create_car_dict(db, one_car, website=url)
    # db.commit()  # Uncomment if using autocommit=False
    return done_for


@router.get("/cars/")
async def read_item(db: Session = Depends(get_db), date_gt: date = None, skip: int = 0, limit: int = 10):
    print(f'main: date_gt: {date_gt}')
    res = crud.get_car_filter_date(db, date_gt, limit=limit)
    return res

@router.get("/search")
async def search_car(db: Session = Depends(get_db), name: str = "", price_ge: int = None, price_le: int = None,
                     mileage_ge: int = None, mileage_le: int = None, date_ge: date = None, date_le: date = None,
                     limit: int = 10):
    print(f"name: {name}, price_ge: {price_ge}, price_le: {price_le}, "
          f"mileage_ge: {mileage_ge}, mileage_le: {mileage_le}, date_ge: {date_ge}, date_le: {date_le}, limit: {limit}")
    result = crud.get_car(db, name=name, price_ge=price_ge, price_le=price_le, mileage_ge=mileage_ge,
                          mileage_le=mileage_le, date_ge=date_ge, date_le=date_le, limit=limit)
    return result

# ------------- For testing -------------------

@router.get("/add-highriverford")
async def add_cars(db: Session = Depends(get_db)):
    """ Adds cars to DB from the following website """
    url_list = [ 'https://www.highriverford.com/used-cars-high-river-ab?sort=Sfield_Price&direction=desc', ]
    done_for = []
    for url in url_list:
        print(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            print(one_car)
            crud.create(db, car_in=one_car, autocommit=True)
    return done_for

@router.get("/add-zarowny-n-others")
async def add_zarowny_n_others(db: Session = Depends(get_db)):
    url_list = [
        'https://www.zarownymotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.westlockford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.griffithsford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC&query=',
        'https://www.rainbowford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC',
    ]
    done_for = []
    for url in url_list:
        print(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            print(one_car)
            crud.create(db, car_in=one_car, autocommit=True)
    return done_for

@router.get("/one-car")
async def add_single_car( db: Session = Depends(get_db) ):
    car_info = {"car_name": "Honda city",
                "mileage": "12245km",
                "exterior": "white",
                "drivetrain": "4x4",
                "transmission": "auto",
                "engine": "vti",
                "date": "2020-11-10"}
    car_info = {'car_name': '2018 Ford F-350 Lariat | Nav | Quad Beams | BLIS | Only 37K!', 'price': 74221,
                'website': 'https://www.boundaryford.com/vehicles/used/?st=price,desc&sc=used&view=grid',
                'mileage': 37825, 'body_style': 'Truck', 'engine': '6.7L Power Stroke', 'exterior': 'White',
                'transmission': '6 Speed Automatic', 'drivetrain': '4x4'}
    res = crud.create(db, car_in=car_info, autocommit=True)
    return res

@router.get("/multi-car")
async def add_single_car(db: Session = Depends(get_db)):
    list_of_car_info = [{"car_name": "Honda city 3",
                         "mileage": 133_210,
                         "exterior": "white",
                         "drivetrain": "4x4",
                         "price": 200_000,
                         "transmission": "auto",
                         "engine": "vti",
                         "entry_date": "2020-11-10"},

                        {"car_name": "Toyota GLI 3",
                         "mileage": 100_000,
                         "exterior": "white",
                         "drivetrain": "4x4",
                         "price": 200_000,
                         "transmission": "auto",
                         "engine": "vti",
                         "entry_date": "2020-11-10"},

                        {"car_name": "Hustler",
                         "mileage": 200,
                         "exterior": "white",
                         "drivetrain": "4x4",
                         "price": 200_000,
                         "transmission": "auto",
                         "engine": "vti",
                         "entry_date": "2020-11-10"}, ]
    for one_car in list_of_car_info:
        res = crud.create(db, car_in=one_car, autocommit=True)
    return res

@router.get("/test/cars/")
async def read_item(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


