from fastapi import Depends, APIRouter, File, UploadFile

from database import SessionLocal, engine, Base, get_db
from models.db_models.car import CarDB

from sqlalchemy.orm import Session
import crud
import logging
import gc

from web_scrapper import get_car_info_from_web
from datetime import date
from time import time

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
        # # 'https://www.royalford.ca/used/used-vehicle-inventory.html?reset=1',  # Got changed
        # # 'https://www.metcalfesgarage.ca/used/used-vehicle-inventory.html?reset=1',    # Got changed
        # # 'https://www.formomotors.com/used/used-vehicle-inventory.html?reset=1',    # Got changed
        'https://www.regalmotorsltd.com/used/used-vehicle-inventory.html',
        'https://www.junctionmotors.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.northstarfordsalescalgary.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.collegefordlincoln.com/used/preowned-inventory.html?reset=1',
        'https://www.truenorthford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.lambford.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.metroford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.cslford.ca/used/used-vehicle-inventory.html?reset=2',
        'https://www.norrisford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.patriciafordsales.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.castleford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.collegefordtaber.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.westergardford.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.jubileeford.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.senchuk.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.centennialford.sk.ca/used/used-vehicle-inventory.html',
        'https://www.meritford.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.twowayservice.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.northlandford.mb.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.rhinelandcar.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.steeltownford.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.gimliford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.hometownford.ca/used/used-vehicle-inventory.html?reset=1',
        'https://www.kelleherforddauphin.com/used/used-vehicle-inventory.html?reset=1',
        'https://www.roblinfordsales.com/used/used-vehicle-inventory?reset=1',
        'https://www.virdenford.ca/pre-owned/pre-owned-vehicle-inventory.html?reset=1',
        'https://www.westwardford.com/used/used-vehicle-inventory.html?reset=1',

        'https://www.woodridgeford.com/used/',
        'https://www.okotoksford.com/used/',
        'https://www.advantageford.ca/used/',
        'https://www.countryford.ca/used/',

        'https://www.zarownymotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.westlockford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.griffithsford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC&query=',
        'https://www.bigmford.com/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC',
        'https://www.jerryford.com/inventory/used-inventory?stock_type=Used&page=1&page_length=100',
        'https://www.draytonvalleyford.com/inventory/search?page=1&page_length=100&stock_type=Used',
        'https://www.harwoodford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.discoveryfordsales.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.langenburgmotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.melodymotors.com/inventory/search?stock_type=Used&sort_by=price&sort_order=ASC&page=1&page_length=100',
        'https://www.valleyfordhague.ca/inventory/hague-used-vehicle-inventory?stock_type=Used&page=1&page_length=100',
        'https://www.fairwayford.ca/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.coldlakeford.com/inventory/search?stock_type=Used&page=1&page_length=100',

        'https://www.fourlaneford.com/used-cars-just-south-of-red-deer-in-innisfail?sort-by=price&direction=high-to-low',
        'https://www.aspenford.ca/used-cars-stettler-ab',
        'https://www.webbsford.com/used-inventory',
        'https://www.suncityford.ca/medicine-hat-used-cars',
        'https://www.pineridgeford.com/used-vehicle-sales?sort-by=price&direction=high-to-low',
        'https://www.wilfselieford.ca/used-vehicles-just-west-of-winnipeg?sort-by=price&direction=high-to-low'

        'https://www.marlboroughford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc',
        'https://www.universalford.com/used-cars-calgary-ab?sort=DateInStock&direction=desc&page=1', # scrape first page

        'https://www.camclarkfordairdrie.com/vehicles/2020/ford/expedition/olds/ab/47305249/?sale_class=used',
        'https://www.integrityford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.moosejawfordsales.com/vehicles/used?view=grid&sc=used',
        'https://www.bennettdunlopford.com/vehicles/used?st=price,asc&view=grid&sc=used',
        'https://www.rivercityford.ca/vehicles/used/?st=price,desc&view=grid&sc=used',

        'https://www.zenderford.com/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.boundaryford.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        'https://www.maclinfordcalgary.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        'https://www.legacyfordponoka.ca/vehicles/used/?view=grid&sc=used',
        'https://www.legacyfordrimbey.ca/vehicles/used/?view=grid&sc=used',
        'https://www.vegford.ca/vehicles/used/?v1=All&view=grid&sc=used',
        'https://www.vickarford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.mid-townford.com/vehicles/used/?sc=used&st=price,desc&view=grid',
        # Multi-page
        'https://www.greatplainsford.com/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',
        'https://www.denhamford.ca/vehicles/used/?sc=used&st=price,desc&view=grid&pg=1',
        'https://www.esterhazyford.ca/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',
        'https://www.futureford.ca/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',

        'https://www.highriverford.com/used-cars-high-river-ab?sort=Sfield_Price&direction=desc',
        'https://www.hansenford.ca/inventory/used-vehicles/price-40000--/srp-page-1/',
        'https://www.windsorford.com/inventory/Used/?page=1',
        'http://www.northstarfordcarsandtrucks.com/used/used-vehicle-inventory.html',
        'https://www.strathmoreford.com/used-inventory/index.htm?start=0',
        'https://www.revolutionford.com/used-inventory/page/1',

        'https://novlanbros.com/inventory/list/#/?&orderBy=1&t=0&filter=[Used%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C',
        'https://www.knightfordlincoln.ca/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',
        'https://www.capitalfordlincoln.com/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',
        'https://www.capitalfordwinnipeg.ca/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',

        'https://www.cypressmotors.com/used-vehicles-swift-current-sk',
        'https://www.birchwoodford.ca/vehicles/?results_page=1&condition=used&sort=price',
        'https://merlinford.com/used-inventory/?pag=1',
        'https://kelleherford.com/used-inventory/sort_by/price/sort_order/desc/?pag=1',
        'https://www.rainbowford.ca/inventory/?condition=pre-owned',  # done
    ]
    # url_list = [ 'https://www.truenorthford.ca/used/used-vehicle-inventory.html?reset=1', ]
    start_time = time()
    done_for = []
    for url in url_list:
        car_count = 0
        logging.info(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            logging.info(one_car)
            car_return = crud.create(db, car_in=one_car, autocommit=True)
            car_count = car_count + 1 if car_return["in_db"] == "Added" else car_count
            logging.info(f'  --- Car status in DB: {car_return["in_db"]}')
        # db.commit()  # Uncomment if using autocommit=False
        logging.info(f'Total Cars added: {car_count}')
        del res
        gc.collect()
    logging.info(f'Time in Hours: {(time() - start_time) / (60 * 60)}')
    logging.info(f'Time in Minutes: {(time() - start_time) / 60}')
    return done_for


@router.get("/cars/")
async def read_item(db: Session = Depends(get_db), date_gt: date = None, skip: int = 0, limit: int = 10):
    logging.info(f'main: date_gt: {date_gt}')
    res = crud.get_car_filter_date(db, date_gt, limit=limit)
    return res

@router.get("/search")
async def search_car(db: Session = Depends(get_db), name: str = "", price_ge: int = None, price_le: int = None,
                     mileage_ge: int = None, mileage_le: int = None, date_ge: date = None, date_le: date = None,
                     limit: int = 10):
    logging.info(f"name: {name}, price_ge: {price_ge}, price_le: {price_le}, "
                 f"mileage_ge: {mileage_ge}, mileage_le: {mileage_le}, date_ge: {date_ge}, "
                 f"date_le: {date_le}, limit: {limit}")
    result = crud.get_car(db, name=name, price_ge=price_ge, price_le=price_le, mileage_ge=mileage_ge,
                          mileage_le=mileage_le, date_ge=date_ge, date_le=date_le, limit=limit)
    return result

# ------------- For testing -------------------

@router.get("/add-sites-set1")
async def add_sites_set1(db: Session = Depends(get_db)):
    """ Adds Cars from website set 1 """
    url_list = [
        'https://www.camclarkfordairdrie.com/vehicles/2020/ford/expedition/olds/ab/47305249/?sale_class=used',
        'https://www.integrityford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.moosejawfordsales.com/vehicles/used?view=grid&sc=used',
        'https://www.bennettdunlopford.com/vehicles/used?st=price,asc&view=grid&sc=used',
        'https://www.rivercityford.ca/vehicles/used/?st=price,desc&view=grid&sc=used',

        'https://www.zenderford.com/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.boundaryford.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        'https://www.maclinfordcalgary.com/vehicles/used/?st=price,desc&sc=used&view=grid',
        'https://www.legacyfordponoka.ca/vehicles/used/?view=grid&sc=used',
        'https://www.legacyfordrimbey.ca/vehicles/used/?view=grid&sc=used',
        'https://www.vegford.ca/vehicles/used/?v1=All&view=grid&sc=used',
        'https://www.vickarford.ca/vehicles/used/?view=grid&sc=used&st=price,desc',
        'https://www.mid-townford.com/vehicles/used/?sc=used&st=price,desc&view=grid',
        # Multi-page
        'https://www.greatplainsford.com/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',
        'https://www.denhamford.ca/vehicles/used/?sc=used&st=price,desc&view=grid&pg=1',
        'https://www.esterhazyford.ca/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',
        'https://www.futureford.ca/vehicles/used/?st=year,desc&view=grid&sc=used&pg=1',

        'https://www.highriverford.com/used-cars-high-river-ab?sort=Sfield_Price&direction=desc',
        'https://www.hansenford.ca/inventory/used-vehicles/price-40000--/srp-page-1/',
        'https://www.windsorford.com/inventory/Used/?page=1',
        'http://www.northstarfordcarsandtrucks.com/used/used-vehicle-inventory.html',
        'https://www.strathmoreford.com/used-inventory/index.htm?start=0',
        'https://www.revolutionford.com/used-inventory/page/1',

        'https://novlanbros.com/inventory/list/#/?&orderBy=1&t=0&filter=[Used%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C',
        'https://www.knightfordlincoln.ca/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',
        'https://www.capitalfordlincoln.com/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',
        'https://www.capitalfordwinnipeg.ca/used-vehicles/?_p=0&_dFR%5Btype%5D%5B0%5D=Used&_dFR%5Btype%5D%5B1%5D=Certified%2520Used&_paymentType=our_price',

        'https://www.cypressmotors.com/used-vehicles-swift-current-sk',
        'https://www.birchwoodford.ca/vehicles/?results_page=1&condition=used&sort=price',
        'https://merlinford.com/used-inventory/?pag=1',
        'https://kelleherford.com/used-inventory/sort_by/price/sort_order/desc/?pag=1',
        'https://www.rainbowford.ca/inventory/?condition=pre-owned',  # done
    ]
    start_time = time()
    done_for = []
    for url in url_list:
        car_count = 0
        logging.info(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            logging.info(one_car)
            car_return = crud.create(db, car_in=one_car, autocommit=True)
            car_count = car_count + 1 if car_return["in_db"] == "Added" else car_count
            logging.info(f'  --- Car status in DB: {car_return["in_db"]}')
        # db.commit()  # Uncomment if using autocommit=False
        logging.info(f'Total Cars added: {car_count}')
        del res
        gc.collect()
        # crud.create_car_dict(db, one_car, website=url)
    logging.info(f'Time in Hours: {(time() - start_time) / (60 * 60)}')
    logging.info(f'Time in Minutes: {(time() - start_time) / 60}')
    return done_for

@router.get("/add-few-sites")
async def add_few_sites(db: Session = Depends(get_db)):
    """ Adds cars to DB from a few websites """

    url_list = [ 'https://www.highriverford.com/used-cars-high-river-ab?sort=Sfield_Price&direction=desc', ]
    start_time = time()
    done_for = []
    for url in url_list:
        car_count = 0
        logging.info(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            logging.info(one_car)
            car_return = crud.create(db, car_in=one_car, autocommit=True)
            car_count = car_count + 1 if car_return["in_db"] == "Added" else car_count
            logging.info(f'  --- Car status in DB: {car_return["in_db"]}')
        logging.info(f'Total Cars added: {car_count}')
        # crud.create_car_dict(db, one_car, website=url)
    # db.commit()  # Uncomment if using autocommit=False
    logging.info(f'Time in Hours: {(time() - start_time) / (60 * 60)}')
    logging.info(f'Time in Minutes: {(time() - start_time) / 60}')
    return done_for


@router.get("/add-zarowny-n-others")
async def add_zarowny_n_others(db: Session = Depends(get_db)):
    url_list = [
        'https://www.zarownymotors.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.westlockford.com/inventory/search?stock_type=Used&page=1&page_length=100',
        'https://www.griffithsford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC&query=',
        'https://www.rainbowford.ca/inventory/search?stock_type=Used&page=1&page_length=100&sort_by=price&sort_order=DESC',
    ]
    start_time = time()
    done_for = []
    for url in url_list:
        car_count = 0
        logging.info(f'For url: {url}')
        res = get_car_info_from_web(url)
        done_for.append(url)
        for one_car in res:
            logging.info(one_car)
            car_return = crud.create(db, car_in=one_car, autocommit=True)
            car_count = car_count + 1 if car_return["in_db"] == "Added" else car_count
            logging.info(f'  --- Car status in DB: {car_return["in_db"]}')
        logging.info(f'Total Cars added: {car_count}')
        # crud.create_car_dict(db, one_car, website=url)
    # db.commit()  # Uncomment if using autocommit=False
    logging.info(f'Time in Hours: {(time() - start_time) / (60 * 60)}')
    logging.info(f'Time in Minutes: {(time() - start_time) / 60}')
    return done_for


@router.get("/add-hardcoded-car")
async def add_hardcoded_car( db: Session = Depends(get_db) ):
    car_info = {"car_name": "Honda city",
                "mileage": "12245km",
                "exterior": "white",
                "drivetrain": "4x4",
                "transmission": "auto",
                "engine": "vti",
                "date": "2020-11-10"}
    car_info = {'car_name': '2018 Ford F-350 Lariat | Nav | Quad Beams | BLIS | Only 37K!', 'price': 74221,
                'car_page_link': 'http://www.hardcodded-link.com/first-car-on-the-page',
                'website': 'http://www.hardcodded-link.com',
                'mileage': 37825, 'body_style': 'Truck', 'engine': '6.7L Power Stroke', 'exterior': 'White',
                'transmission': '6 Speed Automatic', 'drivetrain': '4x4',
                'img_link': 'https://chrome.cdn.searchoptics.com/inventory_parser/uploads/2019/ford/ranger/1FTER4FH8KLA92282/640/2019-ford-ranger-1486285608.jpg'}

    logging.info(car_info)
    car_return = crud.create(db, car_in=car_info, autocommit=True)
    logging.info(f'  --- Car status in DB: {car_return["in_db"]}')
    return car_return

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

                        # {"car_name": "Toyota GLI 3",
                        {"mileage": 200,
                        "exterior": "White",
                         "drivetrain": "4x4",
                         "price": 200_000,
                         "transmission": "auto",
                         "engine": "vti",
                         "entry_date": "2020-11-10"},

                        # {"car_name": "Hustler",
                        #  "mileage": 200,
                        #  "exterior": "Black",
                        #  "drivetrain": "4x4",
                        #  "price": 200_000,
                        #  "transmission": "auto",
                        #  "engine": "vti",
                        #  "entry_date": "2020-11-10"},
                        ]
    for one_car in list_of_car_info:
        res = crud.create(db, car_in=one_car, autocommit=True)
    return res

@router.get("/test/cars/")
async def read_item(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


