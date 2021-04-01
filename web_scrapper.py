# import urllib.request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
import logging
from os import getenv
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

FAIL_SAFE_RUNS = 3
FIREFOX_BIN = getenv("FIREFOX_BIN", "/usr/bin/firefox")
firefox_binary_path = FirefoxBinary(FIREFOX_BIN)
GECKODRIVER_PATH = getenv("GECKODRIVER_PATH", "/home/teemo/softwares/geckodriver")
CAR_CUT_PRICE = 20_000

ENV = getenv("ENV")

# ==========  Helper functions ==========
def process_mileage(raw_num='2,000  km'):
    """ :returns : mileage in Kilometers """
    try:
        comma_wala_num, distance_unit = raw_num.split()
        num_splitted = comma_wala_num.split(',')
        distance = "".join( num_splitted )
        mileage_km = distance
    except:
        mileage_km = None
    return mileage_km

def extract_integer(price_string):
    try:
        # price = re.sub(r'[^\d.]', '', price_string)
        price = re.sub(r'[^\d]', '', price_string)  # removed . to get only integers
        price = int(price)
    except:
        price = None
    return price

def cars_found(main_soap, html_tag='h3', attrs: dict = None):
    """ Cars found on the website """
    cars_count_html = main_soap.find(html_tag, attrs=attrs)
    car_count_str = cars_count_html.getText()
    return extract_integer( car_count_str )

def cars_count_in_soup(main_soap, html_tag='div', attrs: dict = None):
    """ Cars currently loaded in the main-soup object """
    all_div_cars_cards = main_soap.find_all(html_tag, attrs=attrs)
    return len(all_div_cars_cards)

def get_main_soup_n_driver(page_url, cf_tag=None, cf_class_attrs=None, cars_count_in_soup=cars_count_in_soup,
                           cs_tag=None, cs_class_attrs=None):

    logging.info(page_url)
    # Part of slow scroll
    # scroll_down_units = 500
    try:
        if ENV == "prod":
            opts = webdriver.FirefoxOptions()
            opts.add_argument("--headless")
            driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH, options=opts)
        else:
            driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
        # get web page
        driver.get(page_url)
        time.sleep(6)
        page = driver.page_source
        main_soup = BeautifulSoup(page, 'html.parser')

        cars_in_soup = 0
        total_cars = cars_found(main_soup, html_tag=cf_tag, attrs=cf_class_attrs)
        logging.info(f'Total cars on page: {total_cars}')
        current_loop_runs = 0
        while cars_in_soup < total_cars:
            current_loop_runs += 1
            # execute script to scroll down the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            # execute script to scroll down the page slowly
            # driver.execute_script(f"window.scrollTo(0, {str(scroll_down_units)} )")
            # scroll_down_units += 500
            time.sleep(5)
            page = driver.page_source
            main_soup = BeautifulSoup(page, 'html.parser')

            cars_in_soup = cars_count_in_soup(main_soup, html_tag=cs_tag, attrs=cs_class_attrs)

            logging.info(f'Cars currently in soup: {cars_in_soup}')
            if current_loop_runs == FAIL_SAFE_RUNS:
                break

        # Part of slow scroll
        # driver.execute_script(f"window.scrollTo(0, {str(scroll_down_units)} )")
        # for i in range(10):
        #     driver.execute_script(f"window.scrollTo(0, {str(scroll_down_units)} )")
        #     scroll_down_units += 500
        #     time.sleep(1)

    except Exception as e:
        logging.error(f'Unable to return website BeautifulSoup - {e}')
        driver.quit()
        return None, None

    return main_soup, driver


def main_soup_n_driver_scroll_down(url, driver=None):
    if driver is None:
        if ENV == "prod":
            opts = webdriver.FirefoxOptions()
            opts.add_argument("--headless")
            driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH,
                                       options=opts)
        else:
            driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
    driver.get(url)
    # execute script to scroll down the page
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    page = driver.page_source
    main_soup = BeautifulSoup(page, 'html.parser')
    return main_soup, driver


def get_car_page_links(soap, html_tag='a', attrs: dict = None):
    car_page_links = []
    links_in_soap = soap.find_all(html_tag, attrs=attrs)
    for single_link_soap in links_in_soap:
        car_page_links.append(single_link_soap["href"])

    return car_page_links

def get_all_car_page_links(url='https://www.hansenford.ca/inventory/used-vehicles/price-40000--/srp-page-1/',
                           base_url='https://www.hansenford.ca') -> list:
    car_page_links = []

    page = requests.get(url)
    main_soup = BeautifulSoup(page.content, 'html.parser')

    total_cars = cars_found(main_soup, html_tag='div', attrs={"class": "sc-puHdH fiyXIl"})
    logging.info(f'Total cars on page: {total_cars}')
    current_loop_runs = 0
    while len(car_page_links) < total_cars:
        current_loop_runs += 1
        time.sleep(2)
        car_page_links.extend(get_car_page_links(main_soup, 'a', attrs={'class': 'sc-oTAMn cEnJNJ'}))
        try:
            next_page_soup = main_soup.find_all('a', attrs={'class': 'sc-ptbNe hCFcIE'})[-1]
        except:
            next_page_soup = None
        if next_page_soup is not None and next_page_soup.getText() == 'Next':
            next_page_link = next_page_soup["href"]
            next_page_link = base_url + next_page_link

            page = requests.get(next_page_link)
            main_soup = BeautifulSoup(page.content, 'html.parser')

        logging.info(f'Cars currently in car_page_link: {len(car_page_links)}')
        if current_loop_runs == FAIL_SAFE_RUNS:
            break
    return car_page_links


# ========== main function ==========
def filter_cars(car: dict) -> bool:
    """ function designed to be called in filter function """

    if car["price"] is not None and car["price"] > CAR_CUT_PRICE:
        return True
    else:
        return False

def get_car_info_from_web(url: str) -> list:
    logging.info(" ------- Starting Scrapping ------- ")
    logging.info(f'firefox: {FIREFOX_BIN}')
    logging.info(f'Gecko: {GECKODRIVER_PATH}')
    list_of_cars = None
    if "regalmotors" in url:
        # list_of_cars = regal_n_junct_north(url)
        list_of_cars = collegefordlincoln(url)
    elif "junctionmotors" in url:
        # list_of_cars = regal_n_junct_north(url)
        list_of_cars = collegefordlincoln(url)
    elif "northstarfordsales" in url:
        # list_of_cars = regal_n_junct_north(url)
        list_of_cars = collegefordlincoln(url)
    elif "collegefordlincoln" in url:
        list_of_cars = collegefordlincoln(url)
    elif "truenorthford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "lambford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "metroford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "cslford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "norrisford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "patriciafordsales" in url:
        list_of_cars = collegefordlincoln(url)
    elif "castleford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "collegefordtaber" in url:
        list_of_cars = collegefordlincoln(url)
    elif "westergardford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "royalford.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "jubileeford" in url:
        list_of_cars = collegefordlincoln(url)
    elif "senchuk" in url:
        list_of_cars = collegefordlincoln(url)
    elif "centennialford.sk.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "formomotors.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "meritford.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "twowayservice.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "northlandford.mb.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "rhinelandcar.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "steeltownford.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "gimliford.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "hometownford.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "kelleherforddauphin.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "metcalfesgarage.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "roblinfordsales.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "virdenford.ca" in url:
        list_of_cars = collegefordlincoln(url)
    elif "westwardford.com" in url:
        list_of_cars = collegefordlincoln(url)
    elif "woodridgeford" in url:
        list_of_cars = woodridgeford(url)
    elif "okotoksford" in url:
        list_of_cars = woodridgeford(url)
    elif "advantageford" in url:
        list_of_cars = woodridgeford(url)
    elif "countryford.ca" in url:
        list_of_cars = woodridgeford(url)
    elif "zarownymotors" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "westlockford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "griffithsford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "bigmford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "jerryford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "draytonvalleyford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "harwoodford" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "discoveryfordsales.com" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "langenburgmotors.com" in url:
        try:
            list_of_cars = zarowny_n_westlock(url)
        except:
            list_of_cars = zarowny_n_westlock(url)
    elif "melodymotors.com" in url:
        try:
            list_of_cars = zarowny_n_westlock(url)
        except:
            list_of_cars = zarowny_n_westlock(url)
    elif "valleyfordhague.ca" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "fairwayford.ca" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "coldlakeford.com" in url:
        list_of_cars = zarowny_n_westlock(url)
    elif "fourlaneford" in url:
        list_of_cars = fourlane(url)
    elif "aspenford" in url:
        list_of_cars = fourlane(url)
    elif "webbsford" in url:
        list_of_cars = fourlane(url)
    elif "suncityford" in url:
        list_of_cars = fourlane(url)
    elif "pineridgeford.com" in url:
        list_of_cars = fourlane(url)
    elif "wilfselieford.ca" in url:
        list_of_cars = fourlane(url)
    elif "marlborough" in url:
        list_of_cars = marlborough(url)
    elif "universalford" in url:
        list_of_cars = universalford(url)
    elif "camclarkfordairdrie" in url:
        list_of_cars = camclarkfordairdrie(url)
    elif "integrityford" in url:
        list_of_cars = camclarkfordairdrie(url)
    elif "moosejawfordsales" in url:
        list_of_cars = camclarkfordairdrie(url)
    elif "bennettdunlopford" in url:
        list_of_cars = camclarkfordairdrie(url)
    elif "rivercityford" in url:
        list_of_cars = camclarkfordairdrie(url)
    elif "zenderford" in url:
        list_of_cars = zenderford(url)
    elif "boundaryford" in url:
        list_of_cars = zenderford(url)
    elif "denhamford" in url:
        list_of_cars = zenderford(url)
    elif "maclinfordcalgary" in url:
        list_of_cars = zenderford(url)
    elif "legacyfordponoka" in url:
        list_of_cars = zenderford(url)
    elif "legacyfordrimbey" in url:
        list_of_cars = zenderford(url)
    elif "vegford" in url:
        list_of_cars = zenderford(url)
    elif "vickarford" in url:
        list_of_cars = zenderford(url)
    elif "mid-townford" in url:
        list_of_cars = zenderford(url)
    # multi-page
    elif "greatplainsford" in url:
        list_of_cars = zenderford(url)
    elif "esterhazyford.ca" in url:
        list_of_cars = zenderford(url)
    elif "futureford.ca" in url:
        list_of_cars = zenderford(url)
    elif "highriverford" in url:
        list_of_cars = highriverford(url)
    elif "hansenford" in url:
        list_of_cars = hansenford(url)
    elif "windsorford" in url:
        list_of_cars = windsorford(url)
    elif "northstarfordcarsandtrucks" in url:
        list_of_cars = northstarfordcarsandtrucks(url)
    elif "strathmoreford" in url:
        list_of_cars = strathmoreford(url)
    elif "revolutionford" in url:
        list_of_cars = revolutionford(url)
    elif "novlanbros.com" in url:
        list_of_cars = novlanbros(url)
    elif "knightfordlincoln.ca" in url:
        list_of_cars = knightfordlincoln_n_capitalfordlincoln(url)
    elif "capitalfordlincoln.com" in url:
        list_of_cars = knightfordlincoln_n_capitalfordlincoln(url)
    elif "capitalfordwinnipeg.ca" in url:
        list_of_cars = knightfordlincoln_n_capitalfordlincoln(url)
    elif "cypressmotors.com" in url:
        list_of_cars = cypressmotors(url)
    elif "birchwoodford.ca" in url:
        list_of_cars = birchwoodford(url)
    elif "merlinford.com" in url:
        list_of_cars = merlinford(url)
    elif "kelleherford.com" in url:
        list_of_cars = kelleherford(url)
    elif "rainbowford" in url:
        list_of_cars = rainbowford(url)

    # elif "westlockford" in url:
    #     list_of_cars = westlockford(url)

    # # # Apply universal checks
    if list_of_cars is not None:
        logging.info("get_car_info_from_web() Filtering cars now based on price")
        itr_object = filter( filter_cars, list_of_cars )
        return list( itr_object )
    else:
        logging.info("get_car_info_from_web() List_of_cars list is None")
        return []


# ========== Web scrapping functions ==========
def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict, base_url=None, car_name=""):
    try:
        image_soap = soap.find(html_tag, attrs=attrs)
        logging.debug(f'img soup: {image_soap}')
        if base_url is not None:
            save_path = base_url + image_soap["src"]
        else:
            save_path = image_soap["src"]
    except Exception as err:
        logging.error(f'Car: {car_name}')
        logging.error(f'Error in get_car_image_link() err - {err}')
        save_path = ""
    return save_path


def regal_n_junct_north(url: str = 'https://www.regalmotorsltd.com/used/used-vehicle-inventory.html') -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """
    def get_car_name(soap):
        """ Intended to return single name """
        html_car_name = soap.find('h2', attrs={'class': 'centered'})

        single_name = html_car_name.find_all("span")
        car_name_pieces = []
        for prop in single_name:
            car_name_pieces.append(prop.getText())
        #             print(prop.getText())
        concat_car_name = " ".join(car_name_pieces)
        #     print(concat_car_name)
        return concat_car_name

    def get_car_price(soap):
        try:
            price_html = soap.find('span', attrs={'class': 'price-header', 'data-field': 'selected_price'})
            price = price_html.getText()
            price = extract_integer(price)
        except:
            price = None
        return price

    def get_raw_car_specs(soap):
        """Made to handle single car's specs
        :return List containing pieces of car's information
        """
        car_specs = []

        ul_enLayout = soap.find('ul', attrs={'class': 'enLayout'})
        all_li = ul_enLayout.find_all('li')
        for li in all_li:
            car_specs.append(li.getText())

        return car_specs

    def extract_car_specs(raw_car_specs: list):
        search_mileage = 'Mileage: '
        search_exterior = 'Exterior: '
        search_drivetrain = 'Drivetrain: '
        search_transmission = 'Transmission: '
        search_engine = 'Engine: '
        search_vin = 'vin: '

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                res = process_mileage(res)
                car_info["mileage"] = extract_integer(res)

            if search_exterior in elem:
                res = elem.split(search_exterior)[1]
                car_info["exterior"] = res

            if search_drivetrain in elem:
                res = elem.split(search_drivetrain)[1]
                car_info["drivetrain"] = res

            if search_transmission in elem:
                res = elem.split(search_transmission)[1]
                car_info["transmission"] = res

            if search_engine in elem:
                res = elem.split(search_engine)[1]
                car_info["engine"] = res

            if search_vin in elem:
                res = elem.split(search_vin)[1]
                car_info["vin"] = res

        return car_info

    def get_car_info(soap, website):
        """ Return all the information in the car's card """
        car_info = { "car_name": get_car_name(soap), "price": get_car_price(soap), "website": website }

        raw_car_specs = get_raw_car_specs(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    # run firefox webdriver from executable path of your choice
    if ENV == "prod":
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH, options=opts)
    else:
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
    # get web page
    driver.get(url)

    # execute script to scroll down the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(9)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(4)
    # # Create Base Soup object
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    list_of_car_info = []
    all_div_table_row_lg = soup.find_all('div', attrs={'class': 'table-row lg'})
    for div_table_row_lg in all_div_table_row_lg:
        all_div_padding = div_table_row_lg.find_all('div', attrs={'class': 'padding'})
        for div_padding in all_div_padding:
            list_of_car_info.append(get_car_info(div_padding, url))

    # print(list_of_car_info)

    # This can be improved by using a context and having that quit it
    driver.quit()

    return list_of_car_info


def woodridgeford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping. Works for: okotoksford
    :param url: Website url from where to scrape
    :return:
    """
    def get_car_price(soap):
        try:
            price_html = soap.find_all('span', attrs={'itemprop': 'price'})[-1]
            price = extract_integer(price_html.getText())
        except:
            price = None
        return price

    def get_car_mileage(soap):
        """ Intended to return single value """
        html_mileage_payment = soap.find('span', attrs={'itemprop': 'mileageFromOdometer'})
        try:
            car_mileage = html_mileage_payment.getText()
            mileage = extract_integer(car_mileage)
        except:
            mileage = None
        return mileage

    def get_car_info(soap, website, base_url):
        """ Return all the information in the car's card """
        car_info = {"car_name": get_car_name(soap, html_tag='p', attrs={}), "price": get_car_price(soap),
                    "mileage": get_car_mileage(soap), "website": website,
                    "img_link": get_car_image_link(soap, 'img', {'itemprop': 'image'}),
                    "car_page_link": get_car_page_link(soap, 'a', {'class': 'stat-text-link'}, base_url)}

        raw_car_specs = get_car_specs_raw(soap, html_tag='tr', attrs={})

        search_dict = {"body_style": "Body Style: ", "exterior": "Exterior Colour:", "city": "City:",
                       "drivetrain": "Drivetrain:", "transmission": "Transmission:", "engine": "Engine:"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    if "woodridgeford" in url:
        base_url = "https://www.woodridgeford.com"
    elif "okotoksford.com" in url:
        base_url = "https://www.okotoksford.com"
    elif "advantageford.ca" in url:
        base_url = "https://www.advantageford.ca"
    elif "countryford.ca" in url:
        base_url = "https://www.countryford.ca"

    main_soup, driver = get_main_soup_n_driver(url, cf_tag='div', cf_class_attrs={"id": "total-vehicle-number"},
                                               cs_tag="div", cs_class_attrs={"class": "col-xs-12 col-sm-12 col-md-7"})

    list_of_car_info = []
    all_class_outside_box = main_soup.find_all('div', attrs={'class': 'col-xs-12 col-sm-12 col-md-12'})
    for class_outside_box in all_class_outside_box:
        list_of_car_info.append(get_car_info( class_outside_box, url, base_url) )

    driver.quit()

    return list_of_car_info


def zarowny_n_westlock(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping. Works for: griffithsford, rainbowford, bigmford
    :param url: Website url from where to scrape
    :return:
    """
    def get_car_name(soap, website):
        """ Intended to return single name """
        html_h4_car_name = soap.find('h4')
        html_h5_car_name = soap.find('h5')
        try:
            h4_name = html_h4_car_name.getText()
            h5_name = html_h5_car_name.getText()
            if len(h5_name):
                if "westlockford" in website:
                    h5_name = h5_name.split(",")[0]
                if "valleyfordhague" in website:
                    car_name = h4_name
                else:
                    car_name = h4_name + " - " + h5_name
            else:
                car_name = h4_name
        except:
            car_name = ""
        return car_name

    def get_car_specs_raw(soap) -> list:
        # search_mileage = 'Odometer'
        # search_exterior = 'Exterior Colour:'
        # search_drivetrain = 'Drivetrain:'
        # search_transmission = 'Transmission:'
        # search_engine = 'Engine:'
        # search_city = 'City:'

        car_specs_pieces = []
        car_specs = []
        for elem in soap.find('dl').findChildren():
            car_specs_pieces.append(elem.getText())

        for elem in range(0, len(car_specs_pieces), 2):
            car_specs.append(car_specs_pieces[elem] + car_specs_pieces[elem + 1])

        return car_specs

    def get_car_info(soap, website):
        """ Return all the information in the car's card """
        base_url = "/".join(url.split("/")[:3])
        car_name = get_car_name(soap, website)

        car_info = {"car_name": car_name,
                    "price": get_car_price(soap, html_tag='strong', attrs={'class': 'price _bpcolor'}),
                    "img_link": get_car_image_link(soap, 'img', {'class': 'img-defer'}, car_name=car_name),
                    "website": website, "car_page_link": get_car_page_link(soap, 'a', {'itemprop': 'url'}, base_url) }

        raw_car_specs = get_car_specs_raw(soap)

        search_dict = {"mileage": "Odometer", "exterior": "Color", "drivetrain": "Drivetrain",
                       "transmission": "Transmission", "engine": "Engine"}
        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    list_of_car_info = []
    main_soup, driver = get_main_soup_n_driver(url, cf_tag='div', cf_class_attrs={"class": "total-count"},
                                               cs_tag="li", cs_class_attrs={'class': 'vehicle-card-used'})

    all_class_vehicle_card = main_soup.find_all('li', attrs={'class': 'vehicle-card-used'})

    for class_vehicle_card in all_class_vehicle_card:
        list_of_car_info.append( get_car_info(class_vehicle_card, url) )

    driver.quit()

    return list_of_car_info


def fourlane(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """

    def get_car_city(soap: BeautifulSoup):
        """ soap should be car info page """
        car_title = soup.find('h1')
        city = car_title.getText().split('for sale in ')[1]
        return city

    def get_car_specs_raw(soap):
        car_specs = []
        for row, tr in enumerate(soap.find_all('tr')):
            if row == 0:  # handles mileage
                mileage_td = tr.find('td')
                car_specs.append(mileage_td.getText())
            if row == 2:  # Exterior
                exterior_td = tr.find('td')
                car_specs.append(exterior_td.getText())
            if row == 3:  # Drivetrain
                drivetrain_td = tr.find('td')
                try:
                    drivetrain_td.span.decompose()
                except AttributeError:
                    pass
                car_specs.append(drivetrain_td.getText())
            if row == 4:  # Engine
                engine_td = tr.find_all('td')[0]
                car_specs.append(engine_td.getText())

                transmission_td = tr.find_all('td')[1]
                try:
                    transmission_td.span.decompose()
                except AttributeError:
                    pass
                car_specs.append("Transmission: " + transmission_td.getText())

        return car_specs

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_mileage = 'Odometer: '
        search_exterior = 'Color: '
        search_drivetrain = 'Drivetrain: '
        search_transmission = 'Transmission: '
        search_engine = 'Engine: '

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                res = extract_integer(res)
                car_info["mileage"] = res

            if search_exterior in elem:
                res = elem.split(search_exterior)[1]
                car_info["exterior"] = res

            if search_drivetrain in elem:
                res = elem.split(search_drivetrain)[1]
                car_info["drivetrain"] = res

            if search_transmission in elem:
                res = elem.split(search_transmission)[1]
                car_info["transmission"] = res

            if search_engine in elem:
                res = elem.split(search_engine)[1]
                car_info["engine"] = res

        return car_info

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """
        car_name_soap = soap.find('h1')

        car_info = {"car_name": get_car_name(car_name_soap, 'span', attrs={}), "city": get_car_city(soap),
                    "website": website, "img_link": get_car_image_link(soap, 'img', {'class': 'single-image'},
                                                                       website, car_name=car_page_url),
                    "car_page_link": car_page_url}

        if "aspenford.ca" in base_url:
            car_info["price"] = get_car_price(soap, html_tag='div', attrs={'id': 'fd-vehicle-price'})
        else:
            car_info["price"] = get_car_price(soap, html_tag='span', attrs={'class': 'price-large'})

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if "aspenford" in url:
        base_url = 'https://www.aspenford.ca'
    elif "webbsford" in url:
        base_url = 'https://www.webbsford.com'
    elif "suncityford" in url:
        base_url = 'https://www.suncityford.ca'
    elif "pineridgeford.com" in url:
        base_url = 'https://www.pineridgeford.com'
    elif "wilfselieford.ca" in url:
        base_url = "https://www.wilfselieford.ca"
    else:
        base_url = 'https://www.fourlaneford.com'

    main_soup, driver = get_main_soup_n_driver(url, cf_tag='div', cf_class_attrs={"class": "matches"},
                                               cs_tag="a", cs_class_attrs={"class": "vehicle media"})
    list_of_car_info = []  # car_info: dict
    # Get links of all car's information page
    all_a_vehicle_media = main_soup.find_all('a', href=True, attrs={'class': 'vehicle media'})
    for a_vehicle_media in all_a_vehicle_media:
        if a_vehicle_media.has_attr("href"):
            url = a_vehicle_media["href"]
            page = requests.get(base_url + url)
            time.sleep(2)
            soup = BeautifulSoup(page.content, 'html.parser')

            list_of_car_info.append(get_car_info(soup, base_url, base_url + url))

    driver.quit()

    return list_of_car_info


def marlborough(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """

    def get_car_name(soap):
        """ soap should be car info page """
        try:
            car_name = soap.find('h1').getText().strip()
        except:
            car_name = ""
        return car_name

    def get_car_price(soap):
        try:
            price_html = soap.find('span', attrs={'class': 'price-value'})
            price = extract_integer(price_html.getText())
        except:
            price = None
        return price

    def get_car_specs_raw(soap):
        spec_list = []
        all_class_specification = soup.find_all('ul', attrs={'class': 'specification col-sm-6'})
        for class_specification in all_class_specification:
            for li in class_specification.find_all('li'):
                raw_li = li.getText().strip()
                spec_list.append(raw_li.replace('\n', ' '))

        return spec_list

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_mileage = 'Kilometrs: '
        search_exterior = 'Exterior: '
        search_drivetrain = 'Drive: '
        search_transmission = 'Transmission: '
        search_engine = 'Engine: '

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                car_info["mileage"] = extract_integer(res)

            if search_exterior in elem:
                res = elem.split(search_exterior)[1]
                car_info["exterior"] = res

            if search_drivetrain in elem:
                res = elem.split(search_drivetrain)[1]
                car_info["drivetrain"] = res

            if search_transmission in elem:
                res = elem.split(search_transmission)[1]
                car_info["transmission"] = res

            if search_engine in elem:
                res = elem.split(search_engine)[1]
                car_info["engine"] = res

        return car_info

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """

        image_soap = soap.find('div', {'class': 'gallery-media'})
        car_info = {"car_name": get_car_name(soap), "price": get_car_price(soap), "website": website,
                    "img_link": get_car_image_link(image_soap, 'img', {}, car_name=car_page_url),
                    "car_page_link": car_page_url}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if ENV == "prod":
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH, options=opts)
    else:
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
    # get web page
    driver.get(url)
    # execute script to scroll down the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(3)

    # # Create Base Soup object
    page = driver.page_source
    main_soup = BeautifulSoup(page, 'html.parser')

    list_of_car_info = []  # car_info: dict

    # Get links of all car's information page
    all_class_v_title = main_soup.find_all('div', attrs={'class': 'v-title'})
    for class_v_title in all_class_v_title:
        class_title_link = class_v_title.find('a')
        if class_title_link.has_attr("href"):
            single_page_url = class_title_link["href"]
            time.sleep(2)
            page = requests.get( single_page_url )
            soup = BeautifulSoup(page.content, 'html.parser')

            list_of_car_info.append( get_car_info(soup, url, single_page_url) )

    driver.quit()

    return list_of_car_info


def universalford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """

    def get_car_name(soap):
        try:
            car_name = soap.find('h1').getText()
        except:
            car_name = ""
        return car_name

    def get_car_price(soap):
        try:
            price_html = soap.find('span', attrs={'class': 'final-price'})
            price = extract_integer(price_html.getText())
        except:
            price = None
        return price

    def get_car_specs_raw(soap):
        spec_list = []
        all_class_specification = soap.find_all('ul', attrs={'class': 'specification col-sm-6'})
        for class_specification in all_class_specification:
            for li in class_specification.find_all('li'):
                raw_li = li.getText().strip()
                spec_list.append(raw_li.replace('\n', ' '))
        #     print(li.getText())
        return spec_list

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_mileage = 'Mileage: '
        search_exterior = 'Exterior: '
        search_drivetrain = 'Drivetrain: '
        search_transmission = 'Transmission: '
        search_engine = 'Engine: '

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                car_info["mileage"] = extract_integer(res)

            if search_exterior in elem:
                res = elem.split(search_exterior)[1]
                car_info["exterior"] = res

            if search_drivetrain in elem:
                res = elem.split(search_drivetrain)[1]
                car_info["drivetrain"] = res

            if search_transmission in elem:
                res = elem.split(search_transmission)[1]
                car_info["transmission"] = res

            if search_engine in elem:
                res = elem.split(search_engine)[1]
                car_info["engine"] = res

        return car_info

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """
        image_soap = soap.find('div', {'class': 'gallery-media'})

        car_info = {"car_name": get_car_name(soap), "price": get_car_price(soap), "website": website,
                    "img_link": get_car_image_link(image_soap, 'img', {}, car_name=car_page_url),
                    "car_page_link": car_page_url}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    def get_cars_from_single_page(main_soap, website):
        list_of_car_info = []  # car_info: dict
        # Get links of all car's information page
        all_class_vehicle_title = main_soap.find_all('div', attrs={'class': 'vehicle-title'})
        for class_vehicle_title in all_class_vehicle_title:
            class_title_link = class_vehicle_title.find('a')
            if class_title_link.has_attr("href"):
                car_page_url = class_title_link["href"]
                time.sleep(2)
                page = requests.get(car_page_url)
                soup = BeautifulSoup(page.content, 'html.parser')

                list_of_car_info.append( get_car_info(soup, website, car_page_url) )

        return list_of_car_info

    # # # Function Main

    page = requests.get(url)
    main_soup = BeautifulSoup(page.content, 'html.parser')

    list_of_car_info = []
    pagination_next = main_soup.find('a', attrs={'class': 'pagination-next'})
    while pagination_next.has_attr('href'):
        next_page_link = pagination_next["href"]

        page = requests.get(next_page_link)
        main_soup = BeautifulSoup(page.content, 'html.parser')
        list_of_car_info.extend( get_cars_from_single_page(main_soup, url) )

        # Repeat
        pagination_next = main_soup.find('a', attrs={'class': 'pagination-next'})
        if pagination_next is None:
            break

    return list_of_car_info


def camclarkfordairdrie(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_body_style = 'Body Style '
        search_mileage = 'Kilometres '
        search_exterior = 'Exterior Colour '
        search_drivetrain = 'Drive Train '
        search_transmission = 'Transmission '
        search_engine = 'Engine '

        car_info = {}

        for elem in raw_car_specs:
            if search_body_style in elem:
                res = elem.split(search_body_style)[1]
                car_info["body_style"] = res

            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                car_info["mileage"] = extract_integer(res)

            if search_exterior in elem:
                res = elem.split(search_exterior)[1]
                car_info["exterior"] = res

            if search_drivetrain in elem:
                res = elem.split(search_drivetrain)[1]
                car_info["drivetrain"] = res

            if search_transmission in elem:
                res = elem.split(search_transmission)[1]
                car_info["transmission"] = res

            if search_engine in elem:
                res = elem.split(search_engine)[1]
                car_info["engine"] = res

        return car_info

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """
        image_soap = soup.find('div', {'class': 'photo-gallery__image--main'})

        car_info = {"car_name": get_car_name(soap, html_tag='h1', attrs={'class': 'vdp-title'}),
                    "price": get_car_price(soap, html_tag='span', attrs={'class': 'df aifs'}), "website": website,
                    "img_link": get_car_image_link(image_soap, 'img', {}, car_name=car_page_url),
                    "car_page_link": car_page_url}

        raw_car_specs = get_car_specs_raw(soap, html_tag='div', attrs={'class': 'detailed-specs__single-content'})

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if 'camclarkfordairdrie' in url:
        main_soup, driver = get_main_soup_n_driver(url, cf_tag='p',
                                                   cf_class_attrs={"class": "srp__found-header wrapper"},
                                                   cs_tag="div", cs_class_attrs={"class": "mb-lg grid-view col"})
    else:
        main_soup, driver = get_main_soup_n_driver(url, cf_tag='h5',
                                                   cf_class_attrs={"class": "srp__found-header wrapper"},
                                                   cs_tag="div", cs_class_attrs={"class": "mb-lg grid-view col"})

    list_of_car_info = []  # car_info: dict
    try:
        all_a_vehicle = main_soup.find_all('a', href=True,
                                           attrs={'class': 'button gtm_vehicle_tile_cta vehicle-card__cta'})
    except Exception as e:
        logging.error(f'Unable to scrape {url}')
        return list_of_car_info

    for a_vehicle in all_a_vehicle:
        if a_vehicle.has_attr("href"):
            single_car_url = a_vehicle["href"]
            logging.debug(f'page url: {single_car_url}')
            driver.get(single_car_url)
            page = driver.page_source
            time.sleep(2)
            soup = BeautifulSoup(page, 'html.parser')

            list_of_car_info.append( get_car_info(soup, url, single_car_url) )

    driver.quit()

    return list_of_car_info


def get_car_page_link(soap, html_tag='a', attrs: dict = None, base_url: str = None, car_name=""):
    try:
        link_soap = soap.find(html_tag, attrs=attrs)
        if base_url is None:
            link = link_soap["href"]
        else:
            link = base_url + link_soap["href"]
    except Exception as err:
        logging.error(f'Car Name: {car_name}')
        logging.error(f'Error in get_car_page_link() err - {err}')
        link = ""
    return link

def get_car_name(soap, html_tag='h1', attrs: dict = None):
    try:
        car_name = soap.find(html_tag, attrs=attrs).getText().strip()
    except:
        car_name = ""
    return car_name

def get_car_price(soap, html_tag='div', attrs=None):
    """
    :param soap:
    :param html_tag: e.g. div, ul, li
    :param dict attrs: e.g. {'class': 'price-block__price'}
    :return:
    """
    try:
        price_html = soap.find(html_tag, attrs=attrs)
        price = extract_integer( price_html.getText() )
    except:
        price = None
    return price

def get_car_specs_raw(soap, html_tag='li', attrs=None):
    """
    :param soap:
    :param html_tag: e.g. div, ul, li
    :param dict attrs: e.g. {'class': 'detailed-specs__single'}
    :return:
    """
    # Get car specs raw
    spec_list = []
    car_specs = soap.find_all(html_tag, attrs=attrs)
    for spec in car_specs:
        spec_list.append( spec.getText().strip() )

    return spec_list

def extract_car_specs(raw_car_specs: list, search_dict=None) -> dict:
    """
    :param list raw_car_specs: list of dictionaries. Each dict has car's specs
    :param dict search_dict: its keys are based on database name, values are search criterion e.g.
            {"body_style": "Body Style: ", "mileage": "Kilometres: ", "exterior": "Exterior Colour: "}

    Compressed form of

    search_body_style = 'Body Style: '
    search_mileage = 'Kilometres: '
    search_exterior = 'Exterior Colour: '
    search_drivetrain = 'Drive Train: '
    search_transmission = 'Transmission: '
    search_engine = 'Engine: '
    car_info = {}
    for elem in raw_car_specs:
        if search_body_style in elem:
            res = elem.split( search_body_style )[1]
            car_info["body_style"] = res

        if search_mileage in elem:
            res = elem.split( search_mileage )[1]
            car_info["mileage"] = extract_integer(res)

        if search_exterior in elem:
            res = elem.split( search_exterior )[1]
            car_info["exterior"] = res

        if search_drivetrain in elem:
            res = elem.split( search_drivetrain )[1]
            car_info["drivetrain"] = res

        if search_transmission in elem:
            res = elem.split( search_transmission )[1]
            car_info["transmission"] = res

        if search_engine in elem:
            res = elem.split( search_engine )[1]
            car_info["engine"] = res
    return car_info
    """
    car_info = {}

    for elem in raw_car_specs:
        for key, search_criterion in search_dict.items():
            if search_criterion in elem and key == "mileage":
                result = elem.split(search_criterion)[1]
                car_info[key] = extract_integer(result)
            elif search_criterion in elem:
                result = elem.split(search_criterion)[1]
                car_info[key] = result

    return car_info

def collegefordlincoln(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping. Works for: truenorthford,
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            logging.debug(f'img soup: {soap.find(html_tag, attrs=attrs)}')
            image_url = soap.find(html_tag, attrs=attrs)["data-original"]
        except Exception as err:
            logging.error(f'Error in get_car_image_link_n_save() err - {err}')
            image_url = ""
        return image_url

    def cars_count_in_soup(main_soap, html_tag='div', attrs: dict = None):
        """ Cars currently loaded in the main-soup object """
        count = 0
        all_div_table_row_lg = main_soap.find_all(html_tag, attrs=attrs)
        for div_table_row_lg in all_div_table_row_lg:
            all_div_padding = div_table_row_lg.find_all('div', attrs={'class': 'padding'})
            count += len(all_div_padding)

        return count

    # def get_car_name(soap):
    #     """ Intended to return single name """
    #     html_car_name = soap.find('h2', attrs={'class': 'centered'})
    #
    #     single_name = html_car_name.find_all("span")
    #     car_name_pieces = []
    #     for prop in single_name:
    #         car_name_pieces.append(prop.getText())
    #     concat_car_name = " ".join(car_name_pieces)
    #     return concat_car_name

    def get_car_info(soap, website, driver):
        """ Return all the information in the car's card """
        logging.debug("Collegeford.get_car_info() before image_link_n_save")
        car_page_url_soap = soap.find('span', {'class': 'image'})

        car_info = {"website": website, "img_link": get_car_image_link(soap, 'img', {'class': 'img-responsive'}),
                    "car_page_link": get_car_page_link(car_page_url_soap, 'a', {}) }

        if "royalford.ca" in website:
            raw_car_name = get_car_name(soap, html_tag='h2', attrs={'class': 'centered'})
            car_name_pieces = raw_car_name.split('\n')[:4]
            car_info["car_name"] = " ".join(car_name_pieces)
        else:
            car_info["car_name"] = get_car_name(soap, html_tag='h2', attrs={'class': 'centered'})

        # For Price
        if "northlandford.mb.ca" in website:
            car_info["price"] = get_car_price(soap, html_tag='span', attrs={'class': 'fee-value'})
        else:
            # For "formomotors.com"
            price_html = soap.find('span', attrs={'data-field': 'selected_price'})
            dealer_price = price_html.find('div', attrs={'class': 'fee-row dealerPrice'})
            if dealer_price is None:
                car_info["price"] = get_car_price(soap, html_tag='span', attrs={'data-field': 'selected_price'})
            else:
                car_info["price"] = get_car_price(soap, html_tag='div', attrs={'class': 'fee-row dealerPrice'})

        raw_car_specs = get_car_specs_raw(soap, html_tag='li')

        search_dict = {"body_style": "Body Style: ", "mileage": "Mileage: ", "exterior": "Exterior: ",
                       "drivetrain": "Drivetrain: ", "transmission": "Transmission: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    if "royalford.ca" in url or "hometownford.ca" in url:
        main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={"class": "match-count"},
                                                   cars_count_in_soup=cars_count_in_soup,
                                                   cs_tag="div", cs_class_attrs={'class': 'table-row lg md'})
    else:
        main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={"class": "match-count"},
                                                   cars_count_in_soup=cars_count_in_soup,
                                                   cs_tag="div", cs_class_attrs={'class': 'table-row lg'})

    list_of_car_info = []
    if "royalford.ca" in url or "hometownford.ca" in url:
        all_div_table_row_lg = main_soup.find_all('div', attrs={'class': 'table-row lg md'})
    else:
        all_div_table_row_lg = main_soup.find_all('div', attrs={'class': 'table-row lg'})
    for div_table_row_lg in all_div_table_row_lg:
        all_div_padding = div_table_row_lg.find_all('div', attrs={'class': 'padding'})
        for div_padding in all_div_padding:
            list_of_car_info.append( get_car_info(div_padding, url, driver) )

    driver.quit()

    return list_of_car_info

def zenderford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping. Works for: denhamford, maclinfordcalgary
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_max_pages(main_soap):
        try:
            max_page_str = main_soap.find('div', attrs={'class': 'pagination__numbers'}).span.getText()
            max_page_num = extract_integer(max_page_str)
        except:
            max_page_num = 1
        return max_page_num

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """
        image_soap = soap.find('div', {'class': 'photo-gallery__main'})

        car_info = {"car_name": get_car_name(soap, html_tag='h1', attrs={'class': 'vdp-title'}),
                    "price": get_car_price(soap, html_tag='div', attrs={'class': 'price-block__price'}),
                    "website": website, "img_link": get_car_image_link(image_soap, 'img', {}),
                    "car_page_link": car_page_url}

        raw_car_specs = get_car_specs_raw(soap, html_tag='li', attrs={'class': 'detailed-specs__single'})

        search_dict = {"body_style": "Body Style: ", "mileage": "Kilometres: ", "exterior": "Exterior Colour: ",
                       "drivetrain": "Drive Train: ", "transmission": "Transmission: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if "zenderford" in url:
        cf_tag = 'h3'
        cf_class_attrs = {"class": "srp__vehicle-count"}
    else:
        cf_tag = 'h5'
        cf_class_attrs = {"class": "srp__found-header wrapper"}
    main_soup, driver = get_main_soup_n_driver(url, cf_tag=cf_tag, cf_class_attrs=cf_class_attrs,
                                               cs_tag="div", cs_class_attrs={"class", "mb-lg grid-view col"})

    list_of_car_info = []  # car_info: dict

    if 'greatplainsford' in url or "esterhazyford.ca" in url or "futureford.ca" in url:
        # Cars on multiple pages
        max_pages = get_max_pages(main_soup)
        current_page = 1

        current_loop_runs = 0
        while current_page <= max_pages:
            current_loop_runs += 1

            # Scrape all cars on a single page
            all_a_vehicle = main_soup.find_all('a', href=True,
                                               attrs={'class': 'button gtm_vehicle_tile_cta vehicle-card__cta'})
            for a_vehicle in all_a_vehicle:
                if a_vehicle.has_attr("href"):
                    single_car_url = a_vehicle["href"]

                    driver.get(single_car_url)
                    page = driver.page_source
                    time.sleep(2)
                    soup = BeautifulSoup(page, 'html.parser')

                    list_of_car_info.append(get_car_info(soup, url, single_car_url))

            # visi all pages
            url = url.replace(f'pg={current_page}', f'pg={current_page + 1}')
            current_page += 1
            time.sleep(2)
            driver.get(url)
            page = driver.page_source
            main_soup = BeautifulSoup(page, 'html.parser')
            # print(f'loop status: ', current_loop_runs, FAIL_SAFE_RUNS)
            if current_loop_runs > FAIL_SAFE_RUNS:
                # print(current_loop_runs, FAIL_SAFE_RUNS)
                break
    else:
        # All cars on single page
        all_a_vehicle = main_soup.find_all('a', href=True,
                                           attrs={'class': 'button gtm_vehicle_tile_cta vehicle-card__cta'})
        for a_vehicle in all_a_vehicle:
            if a_vehicle.has_attr("href"):
                single_car_url = a_vehicle["href"]

                driver.get(single_car_url)
                page = driver.page_source
                time.sleep(2)
                soup = BeautifulSoup(page, 'html.parser')

                list_of_car_info.append( get_car_info(soup, url, single_car_url) )

    driver.quit()

    return list_of_car_info


def highriverford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_specs_raw(soap) -> list:
        """ This is specific to highriverford website """
        # Get car specs raw
        spec_list = []
        for spec_key in ['miles', 'exteriorcolor', 'standardbody', 'drivetrain', 'transmission', 'enginedescription']:
            try:
                car_spec = soap.find('span', attrs={'class': f'spec-value spec-value-{spec_key}'})
                spec_list.append(f'{spec_key}: {car_spec.getText()}')
            except:
                pass
        return spec_list

    def get_car_info(soap, website):
        """ Return all the information in the car's card """
        image_soap = soap.find('span', {'class': 'v-image-inner'})
        car_page_link_soap = soap.find('div', attrs={'class': 'v-title'})

        car_info = {"car_name": get_car_name(soap, html_tag='div', attrs={'class': 'v-title'}),
                    "price": get_car_price(soap, html_tag='span', attrs={'class': 'starting-price-value'}),
                    "website": website, "img_link": get_car_image_link(image_soap, 'img', {}),
                    "car_page_link": get_car_page_link(car_page_link_soap, 'a')}

        raw_car_specs = get_car_specs_raw(soap)

        search_dict = {"mileage": "miles: ", "exterior": "exteriorcolor: ", "engine": "enginedescription: ",
                       "transmission": "transmission: ", "body_style": "standardbody: ", "drivetrain": "drivetrain: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={"class": "total-found"},
                                               cs_tag="div", cs_class_attrs={'class': 'vehicle transformed'})
    list_of_car_info = []
    all_vehicle_cards = main_soup.find_all('div', attrs={'class': 'vehicle transformed'})
    for vehicle_card in all_vehicle_cards:
        list_of_car_info.append(get_car_info(vehicle_card, url))

    driver.quit()

    return list_of_car_info


def hansenford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_price(soap):
        try:
            price_soap = soap.find('div', {'class': 'jzl-pricing-viewer-root'})
            price = price_soap.find_all('div', {'class': 'row'})[-2].getText()
            price = extract_integer(price)
        except:
            price = None
        return price

    def get_car_specs_raw(soap):
        # Website specific. Get car specs raw
        spec_list = []
        spec_soup = soup.find('div', attrs={
            'class': 'elementor-element elementor-element-f64281c elementor-widget elementor-widget-jazel-vdp-details'})
        car_specs = spec_soup.find_all('span')
        for i in range(0, len(car_specs), 2):
            spec_list.append(f'{car_specs[i].getText()} {car_specs[i + 1].getText()}')
        return spec_list

    def get_car_info(soap, website, car_page_link):
        """ Return all the information in the car's card """
        image_soap = soap.find('div', {'class': 'main-slider__slide'})
        image_soap = str(image_soap).split("url('//")
        image_link = image_soap[1].split("')")[0]

        car_info = {"car_name": get_car_name(soap, html_tag='h1',
                                             attrs={'class': 'elementor-heading-title elementor-size-default'}),
                    "price": get_car_price(soap), "website": website, "img_link": image_link,
                    "car_page_link": car_page_link}

        raw_car_specs = get_car_specs_raw(soap)

        search_dict = {"body_style": "Body Style: ", "mileage": "Odometer: ", "exterior": "Ext. Color: ",
                       "drivetrain": "Drivetrain: ", "transmission": "Trans.: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    car_page_links = get_all_car_page_links(url='https://www.hansenford.ca/inventory/used-vehicles/price-40000--/srp-page-1/',
                                            base_url='https://www.hansenford.ca')

    list_of_car_info = []  # car_info: dict
    for single_car_page_link in car_page_links:
        page = requests.get(single_car_page_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        time.sleep(3)
        list_of_car_info.append(get_car_info(soup, url, single_car_page_link))

    return list_of_car_info


def windsorford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_car_page_links(soap, html_tag='a', attrs: dict = None, base_url=""):
        car_page_links = []
        links_in_soap = soap.find_all(html_tag, attrs=attrs)
        for single_link_soap in links_in_soap:
            a_soup = single_link_soap.find('a')
            car_page_links.append(base_url + a_soup["href"])

        return car_page_links

    def get_all_car_page_links(url='https://www.windsorford.com/inventory/Used/?page=1',
                               base_url='https://www.windsorford.com'):
        car_page_links = []
        curr_page_number = 1

        page = requests.get(url)
        main_soup = BeautifulSoup(page.content, 'html.parser')

        max_page_number = int(main_soup.find('div', attrs={'class': 'inner-count pagination-max-page'}).getText())
        total_cars = cars_found(main_soup, html_tag='span', attrs={"class": "search-vehicle-count"})
        logging.info(f'Total cars on page: {total_cars}')

        current_loop_runs = 0
        while curr_page_number <= max_page_number:
            current_loop_runs += 1
            car_page_links.extend(get_car_page_links(main_soup, 'div', attrs={'class': 'inventory-vehicle-header'},
                                                     base_url=base_url))
            url = url.replace(f"page={curr_page_number}", f"page={curr_page_number + 1}")

            time.sleep(2)
            page = requests.get(url)
            main_soup = BeautifulSoup(page.content, 'html.parser')

            # Termination logic
            curr_page_number += 1

            logging.info(f'Cars currently in car_page_link: {len(car_page_links)}')
            if current_loop_runs == FAIL_SAFE_RUNS:
                break
        return car_page_links

    def get_car_info(soap, website, car_page_link):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, html_tag='h1', attrs={'class': 'detail-vehicle-header'}),
                    "website": website, "car_page_link": car_page_link,
                    "img_link": get_car_image_link(soap, 'img', {'itemprop': 'image', 'name': 'image'}) }

        price_soup = soap.find('p', attrs={'class': 'final-price mt-4'})
        car_info["price"] = get_car_price(price_soup, 'span')

        raw_car_specs = get_car_specs_raw(soap, html_tag='div', attrs={'class': 'info-item'})

        search_dict = {"body_style": "Body Style: ", "mileage": "Odometer:", "exterior": "Exterior:",
                       "drivetrain": "Drivetrain:", "transmission": "Transmission:", "engine": "Engine:"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    car_page_links = get_all_car_page_links(url='https://www.windsorford.com/inventory/Used/?page=1',
                                            base_url='https://www.windsorford.com')

    list_of_car_info = []  # car_info: dict
    for single_car_page_link in car_page_links:
        page = requests.get(single_car_page_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        time.sleep(3)
        list_of_car_info.append(get_car_info(soup, url, single_car_page_link))

    return list_of_car_info


def northstarfordcarsandtrucks(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            logging.debug(f'img soup: {soap.find(html_tag, attrs=attrs)}')
            image_url = soap.find(html_tag, attrs=attrs)["data-original"]
        except Exception as err:
            logging.error(f'Error in get_car_image_link_n_save() err - {err}')
            image_url = ""
        return image_url

    def get_car_info(soap, website, car_page_link):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, html_tag='b', attrs={'class': 'bold'}),
                    "price": get_car_price(soap, html_tag='div',
                                           attrs={'class': 'price-header vehiclePriceWidgetSelectedPrice'}),
                    "website": website, "car_page_link": car_page_link,
                    "img_link": get_car_image_link(soap, 'img', {'class': 'img-responsive'})}

        raw_car_specs = get_car_specs_raw(soap, html_tag='li', attrs={'class': 'module-vehicleBulletsWidget'})

        search_dict = {"body_style": "Body Style: ", "mileage": "ODOMETER: ", "exterior": "EXTERIOR: ",
                       "drivetrain": "Drivetrain: ", "transmission": "TRANSMISSION: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={"class": "match-count"},
                                               cs_tag="div", cs_class_attrs={"class": "table-row xs"})

    list_of_car_info = []  # car_info: dict
    car_cards_soup_list = main_soup.find_all('div', attrs={"class": "table-row xs"})
    for car_cards_soup in car_cards_soup_list:
        link_soup = car_cards_soup.find('a', href=True, attrs={'class': 'button quick-view'})
        if link_soup.has_attr("href"):
            single_car_url = link_soup["href"]

            page = requests.get(single_car_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            time.sleep(3)

            list_of_car_info.append(get_car_info(soup, url, single_car_url))

    driver.quit()

    return list_of_car_info


def strathmoreford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_car_page_link(soap, html_tag='a', attrs: dict = None, base_url=None):
        try:
            link_soap = soap.find(html_tag, attrs=attrs)
            link = base_url + link_soap["href"]
        except Exception as err:
            logging.error(f'Error in get_car_page_link() err - {err}')
            link = ""
        return link

    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            image_soap = soap.find(html_tag, attrs=attrs)
            if image_soap.get("data-src") is None:
                image_url = image_soap["src"]
            else:
                image_url = image_soap["data-src"]
        except Exception as err:
            logging.error(f'Error in get_car_image_link() err - {err}')
            logging.error(f'Image soup: {image_soap}')
            image_url = ""
        return image_url

    def get_car_specs_raw(soap) -> list:
        """ Website specific function """
        car_specs_pieces = []
        car_specs = []
        for single_dl_soap in soap.find_all('dl'):
            for elem in single_dl_soap.findChildren():
                car_specs_pieces.append(elem.getText())

            for elem in range(0, len(car_specs_pieces), 3):
                car_specs.append(car_specs_pieces[elem] + car_specs_pieces[elem + 1])

        return car_specs

    def get_car_info(soap, website, base_url):
        """ Return all the information in the car's card """
        image_soup = soup.find('div', {'class': 'media'})

        car_info = {"car_name": get_car_name(soup, 'h3', attrs={'class': 'fn'}),
                    "price": get_car_price(soup, 'span', attrs={'class': 'internetPrice final-price'}),
                    "website": website, "car_page_link": get_car_page_link(soap, 'a', {}, base_url),
                    "img_link": get_car_image_link(soap, 'img', {}) }

        raw_car_specs = get_car_specs_raw(soup)

        search_dict = {"mileage": "Kilometres:", "exterior": "Exterior Colour:",
                       "drivetrain": "Drive Line:", "transmission": "Transmission:", "engine": "Engine:"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    base_url = 'https://www.strathmoreford.com/'
    page = requests.get(url)
    main_soup = BeautifulSoup(page.content, 'html.parser')
    start = 0
    cars_on_single_page = 16
    total_cars = cars_found(main_soup, 'span', attrs={'class': 'vehicle-count'})
    list_of_car_info = []  # car_info: dict

    current_loop_runs = 0
    while len(list_of_car_info) < total_cars:
        current_loop_runs += 1
        cars_card_soups = main_soup.find_all('div', attrs={'class': 'hproduct auto ford has-sales-taxes'})
        for soup in cars_card_soups:
            list_of_car_info.append(get_car_info(soup, url, base_url))

        url = url.replace(f"start={start}", f"start={start + cars_on_single_page}")
        start += cars_on_single_page
        time.sleep(2)
        page = requests.get(url)
        main_soup = BeautifulSoup(page.content, 'html.parser')

        if current_loop_runs >= FAIL_SAFE_RUNS:
            break

    return list_of_car_info


def revolutionford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_max_pages(soap):
        page_num_links = soap.find_all('a', attrs={'class': 'page-numbers'})
        lst = []
        for single_link in page_num_links:
            try:
                lst.append( int( single_link.getText() ) )
            except:
                pass
        return max( lst )

    def get_car_price(soap, html_tag='div', attrs=None):
        """ Website specific """
        try:
            price_html = soap.find(html_tag, attrs=attrs)
            price = extract_integer(price_html["value"])
        except:
            price = None
        return price

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, 'h1', attrs={'class': 'title h2'}), "website": website,
                    "price": get_car_price(soap, 'input', attrs={'class': 'numbersOnly vehicle_price'}),
                    "img_link": get_car_image_link(soap, 'img', {'class': 'img-responsive wp-post-image'}),
                    "car_page_link": car_page_url }

        raw_specs = get_car_specs_raw(soap, 'tr', attrs={})
        raw_car_specs = list(map(lambda s: s.strip(), raw_specs))

        search_dict = {"mileage": "Odometer", "exterior": "Exterior Color", "body_style": "Body Type",
                       "drivetrain": "Drivetrain", "transmission": "Transmission", "engine": "Engine Description"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)
        for key, val in car_specs.items():
            if type(val) is str:
                car_specs[key] = val.strip()

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if ENV == "prod":
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH, options=opts)
    else:
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)

    # get web page
    driver.get(url)
    page = driver.page_source
    main_soup = BeautifulSoup(page, 'html.parser')

    list_of_car_info = []

    max_pages = get_max_pages(main_soup)
    current_page = 1

    current_loop_runs = 0
    while current_page <= max_pages:
        current_loop_runs += 1

        # Scrape all cars on a single page
        car_page_links = main_soup.find_all('a', attrs={'class': 'rmv_txt_drctn'})
        for car_page_link_soup in car_page_links:
            car_page_url = car_page_link_soup['href']
            time.sleep(2)
            driver.get(car_page_url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            list_of_car_info.append(get_car_info(soup, url, car_page_url))

        # visit all pages
        url = url.replace(f'page/{current_page}', f'page/{current_page + 1}')
        current_page += 1
        time.sleep(2)
        driver.get(url)
        page = driver.page_source
        main_soup = BeautifulSoup(page, 'html.parser')
        # print(f'loop status: ', current_loop_runs, FAIL_SAFE_RUNS)
        if current_loop_runs > FAIL_SAFE_RUNS:
            # print(current_loop_runs, FAIL_SAFE_RUNS)
            break

    driver.quit()

    return list_of_car_info


def novlanbros(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_info(soap, website):
        """ Return all the information in the car's card """
        website = website.split('#')[0]
        image_url_raw = soap.find('div', {'class': 'l-image'})["style"]
        match = re.search(r'url\(.*\)', image_url_raw)
        image_url_raw = match.group(0)
        image_url = re.sub(r'url\(|\)', '', image_url_raw)

        car_info = {"car_name": get_car_name(soap, 'h2', attrs={'class': 'fn'}),
                    "price": get_car_price(soap, 'dd', {'class': 'vehicle_price'}), "website": website,
                    "img_link": image_url, "car_page_link": get_car_page_link(soap, 'a', {'itemprop': 'url'}) }

        raw_car_specs = soap.find('div', attrs={'class': 'e-description description'}).getText().split('\n')

        search_dict = {"mileage": "Odometer: ", "exterior": "Exterior: ",
                       "transmission": "Transmission: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={"class": "stock stock-size"},
                                               cs_tag="div",
                                               cs_class_attrs={"class": "h-product hproduct vehicleModule"})
    list_of_car_info = []
    all_class_outside_box = main_soup.find_all('div', attrs={'class': 'h-product hproduct vehicleModule'})
    for class_outside_box in all_class_outside_box:
        list_of_car_info.append(get_car_info(class_outside_box, url))

    driver.quit()

    return list_of_car_info


def knightfordlincoln_n_capitalfordlincoln(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            logging.debug(f'img soup: {soap.find(html_tag, attrs=attrs)}')
            image_url = soap.find(html_tag, attrs=attrs)["data-background"]
        except Exception as err:
            logging.error(f'Error in get_car_image_link_n_save() err - {err}')
            image_url = ""
        return image_url

    # Website specific function
    def get_max_pages(main_soap):
        try:
            max_page_str = main_soap.find('div', attrs={'class': 'pagination-state'}).getText()
            max_page_str = max_page_str.split('of')[-1]
            max_page_num = extract_integer(max_page_str)
        except:
            max_page_num = 1
        return max_page_num

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, html_tag='h1', attrs={}),
                    "price": get_car_price(soap, html_tag='span', attrs={'class': 'pricing-item__price'}),
                    "website": website, "car_page_link": car_page_url,
                    "img_link": get_car_image_link(soap, 'div', {'class': 'vehicle-image-bg'})}

        raw_car_specs = get_car_specs_raw(soap, html_tag='li', attrs={'class': 'basic-info-item'})

        search_dict = {"mileage": "Odometer:\n", "exterior": "Exterior:\n",
                       "drivetrain": "Drivetrain:\n", "transmission": "Transmission:\n", "engine": "Engine:\n"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    main_soup, driver = get_main_soup_n_driver(url, cf_tag='span', cf_class_attrs={'id': 'results-title'},
                                               cs_tag="div",
                                               cs_class_attrs={"class": "result-wrap used-vehicle stat-image-link"})

    list_of_car_info = []  # car_info: dict
    max_pages = get_max_pages(main_soup) - 1  # It starts from 0
    current_page = 0

    current_loop_runs = 0
    while current_page <= max_pages:
        current_loop_runs += 1

        all_car_cards = main_soup.find_all('div', attrs={'class': 'result-wrap used-vehicle stat-image-link'})
        for car_card in all_car_cards:
            link_soup = car_card.find('a', {'class': 'hit-link'}, href=True)
            car_page_link = link_soup["href"]

            # Visit car page
            page = requests.get(car_page_link)
            soup = BeautifulSoup(page.content, 'html.parser')
            time.sleep(1)
            list_of_car_info.append(get_car_info(soup, url, car_page_link))

        # visi all pages
        url = url.replace(f'_p={current_page}', f'_p={current_page + 1}')
        current_page += 1
        time.sleep(2)
        driver.get(url)
        page = driver.page_source
        main_soup = BeautifulSoup(page, 'html.parser')
        # print(f'loop status: ', current_loop_runs, FAIL_SAFE_RUNS)
        if current_loop_runs > FAIL_SAFE_RUNS:
            # print(current_loop_runs, FAIL_SAFE_RUNS)
            break

    driver.quit()

    return list_of_car_info


def cypressmotors(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """
    def get_car_page_link(soap, html_tag='a', attrs: dict = None):
        base_url = "https://www.cypressmotors.com"
        try:
            link_soap = soap.find(html_tag, attrs=attrs)
            link = base_url + link_soap["href"]
        except Exception as err:
            logging.error(f'Error in get_car_page_link() err - {err}')
            link = ""
        return link

    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            image_soap = soap.find(html_tag, attrs=attrs)
            if image_soap.get("data-src") is None:
                image_url = image_soap["src"]
            else:
                image_url = image_soap["data-src"]
            image_url = image_url[2:]
        except Exception as err:
            logging.error(f'Error in get_car_image_link() err - {err}')
            logging.error(f'Image soup: {image_soap}')
            image_url = ""
        return image_url

    def get_car_city(soap, html_tag='span', attrs=None):
        """ soap should be car info page """
        try:
            city = soap.find(html_tag, attrs=attrs).getText().strip()
        except:
            city = ""
        return city

    def get_car_info(soap, website):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, html_tag='a', attrs={'class': 'vehicle-title'}),
                    "price": get_car_price(soap, html_tag='div', attrs={'class': 'price_value'}),
                    "city": get_car_city(soap, html_tag='span', attrs={'class': 'inventory-item_sub-title_item'}),
                    "website": website, "car_page_link": get_car_page_link(soap, 'a', {'class': 'vehicle-title'} ),
                    "img_link": get_car_image_link(soap, 'img', {'class': 'img-responsive'})}

        raw_car_specs = get_car_specs_raw(soap, html_tag='li', attrs={})

        search_dict = {"mileage": "Mileage: ", "drivetrain": "Drivetrain: ", "transmission": "Transmission:\n",
                       "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    if ENV == "prod":
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH, options=opts)
    else:
        driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
    driver.get(url)
    page = driver.page_source
    main_soup = BeautifulSoup(page, 'html.parser')
    car_count_str = main_soup.find('div', {'class': 'inventory-heading_count'}).getText()
    total_cars = extract_integer(car_count_str)
    driver.quit()
    url = url + f'?limit={total_cars}'

    main_soup, driver = get_main_soup_n_driver(url, cf_tag='div', cf_class_attrs={'class': 'inventory-heading_count'},
                                               cs_tag="div",
                                               cs_class_attrs={"class": "inventory-item clearfix js-vehicle-item"})

    list_of_car_info = []
    all_vehicle_cards = main_soup.find_all('div', attrs={"class": "inventory-item clearfix js-vehicle-item"})
    for vehicle_card in all_vehicle_cards:
        list_of_car_info.append(get_car_info(vehicle_card, url))

    driver.quit()

    return list_of_car_info


def birchwoodford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_all_car_page_links(url='https://www.birchwoodford.ca/vehicles/?results_page=1&condition=used&sort=price',
                               base_url='https://www.birchwoodford.ca') -> list:
        # All car page links
        car_page_links = []

        page = requests.get(url)
        main_soup = BeautifulSoup(page.content, 'html.parser')

        total_cars = cars_found(main_soup, html_tag='span', attrs={'class': 'result-count'})
        print(f'Total cars on page: {total_cars}')
        current_page = 1
        current_loop_runs = 0
        while len(car_page_links) < total_cars:
            current_loop_runs += 1
            time.sleep(2)

            # Get car page links
            car_card_soups = main_soup.find_all('div', {'class': 'phoenix4-vehiclecard'})
            for car_card in car_card_soups:
                link_in_list = get_car_page_links(car_card)
                car_page_links.append(base_url + link_in_list[0])

            # Go to next page
            url = url.replace(f'results_page={current_page}', f'results_page={current_page + 1}')
            current_page += 1
            page = requests.get(url)
            main_soup = BeautifulSoup(page.content, 'html.parser')

            print(f'Cars currently in car_page_link: {len(car_page_links)}')
            if current_loop_runs == FAIL_SAFE_RUNS:
                break

        return car_page_links

    def get_car_info(soap, website, car_page_url):
        """ Return all the information in the car's card """
        image_soap = soap.find('a', {'class': 'main-image has-image'})

        car_info = {"car_name": get_car_name(soap, html_tag='h1', attrs={}),
                    "price": get_car_price(soap, 'span', {'class': 'price-value'}), "website": website,
                    "car_page_link": car_page_url, "img_link": get_car_image_link(image_soap, 'img', {})}

        li_soap = soap.find('ul', {'class': 'feature-or-specification-list'})
        raw_car_specs = get_car_specs_raw(li_soap, html_tag='li', attrs={})

        search_dict = {"city": "Location: ", "mileage": "Mileage: ", "exterior": "Exterior Colour: ",
                       "drivetrain": "Drive Type: ", "transmission": "Transmission: ", "engine": "Engine: "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    if "birchwoodford.ca" in url:
        base_url = 'https://www.birchwoodford.ca'
    else:
        base_url = None
    car_page_links = get_all_car_page_links(url, base_url)

    list_of_car_info = []  # car_info: dict
    for single_car_page_link in car_page_links:
        page = requests.get(single_car_page_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        time.sleep(2)
        list_of_car_info.append(get_car_info(soup, url, single_car_page_link))

    return list_of_car_info


def merlinford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_image_link(soap: BeautifulSoup, html_tag: str, attrs: dict):
        try:
            image_soap = soap.find(html_tag, attrs=attrs)
            if image_soap.get("data-src") is None:
                image_url = image_soap["src"]
            else:
                image_url = image_soap["data-src"]
        except Exception as err:
            logging.error(f'Error in get_car_image_link() err - {err}')
            logging.error(f'Image soup: {image_soap}')
            image_url = ""
        return image_url

    def get_car_page_link(soap, html_tag='a', attrs: dict = None):
        base_url = 'https://merlinford.com'
        try:
            link_soap = soap.find(html_tag, attrs=attrs)
            link = base_url + link_soap["href"]
        except Exception as err:
            logging.error(f'Error in get_car_page_link() err - {err}')
            link = ""
        return link

    def main_soup_n_driver_scroll_down(url, driver=None):
        if driver is None:
            if ENV == "prod":
                opts = webdriver.FirefoxOptions()
                opts.add_argument("--headless")
                driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH,
                                           options=opts)
            else:
                driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
        driver.get(url)
        # execute script to scroll down the page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        page = driver.page_source
        main_soup = BeautifulSoup(page, 'html.parser')
        return main_soup, driver

    def get_car_mileage(soap, html_tag='span', attrs: dict = None):
        try:
            price_html = soap.find(html_tag, attrs=attrs)
            price = extract_integer(price_html.getText())
        except:
            price = None
        return price

    def get_car_info(soap, website):
        """ Return all the information in the car's card """
        car_name = get_car_name(soap, 'h3', {'class': 'pt-4'}).split('\n')[0]

        car_info = {"car_name": car_name, "mileage": get_car_mileage(soap, 'span', {'class': 'mileage-value'}),
                    "price": get_car_price(soap, 'strong', {'class': 'price-label'}),
                    "website": website,"car_page_link": get_car_page_link(soap, 'a', {'class': 'title-link'}),
                    "img_link": get_car_image_link(soap, 'img', {'class': 'img-4-to-3 main-img'})[2:] }

        raw_car_specs = get_car_specs_raw(soap, html_tag='div', attrs={'class': 'w-4/5'})

        search_dict = {"exterior": "Exterior:\xa0", "drivetrain": "Drivetrain:\xa0",
                       "transmission": "Transmission:\xa0", "engine": "Engine:\xa0"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    main_soup, driver = main_soup_n_driver_scroll_down(url)

    list_of_car_info = []
    total_cars = cars_found(main_soup, html_tag='p',
                            attrs={'class': 'text-4xl font-semibold leading-none text-primary lg:pr-2 total-value'})
    current_page = 1
    current_loop_runs = 0
    while len(list_of_car_info) < total_cars:
        current_loop_runs += 1
        logging.info(f'Scraping on Page: {current_page}')
        # Scrape all cars on a single page
        all_vehicle_card = main_soup.find_all('div', {'class': 'vehicle-card'})
        for vehicle_card_soup in all_vehicle_card:
            list_of_car_info.append(get_car_info(vehicle_card_soup, url))

        # visi all pages
        url = url.replace(f'pag={current_page}', f'pag={current_page + 1}')
        current_page += 1
        time.sleep(2)

        main_soup, driver = main_soup_n_driver_scroll_down(url, driver)

        if current_loop_runs > FAIL_SAFE_RUNS:
            # print(current_loop_runs, FAIL_SAFE_RUNS)
            break

    driver.quit()

    return list_of_car_info


def kelleherford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def main_soup_n_driver_scroll_down(url, driver=None):
        if driver is None:
            if ENV == "prod":
                opts = webdriver.FirefoxOptions()
                opts.add_argument("--headless")
                driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH,
                                           options=opts)
            else:
                driver = webdriver.Firefox(firefox_binary=firefox_binary_path, executable_path=GECKODRIVER_PATH)
        driver.get(url)
        # execute script to scroll down the page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        page = driver.page_source
        main_soup = BeautifulSoup(page, 'html.parser')
        return main_soup, driver

    def get_car_info(soap, website, base_url):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap, 'a', {'class': 'title'}),
                    "price": get_car_price(soap, 'strong', {'class': 'sale-price-value'}),
                    "website": website, "car_page_link": get_car_page_link(soap, 'a', {'class': 'title'}, base_url),
                    "img_link": get_car_image_link(soap, 'img', {'class': 'w-full main-pic'})[2:]}

        raw_car_specs = get_car_specs_raw(soap, 'li', {'class': 'text-secondary'})

        search_dict = {"mileage": "Mileage: ", "exterior": "Exterior: ", "drivetrain": "Drivetrain: ",
                       "transmission": "Transmission: ", "engine": "Engine:  "}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        return car_info

    # # # Function Main
    main_soup, driver = main_soup_n_driver_scroll_down(url)

    list_of_car_info = []
    base_url = 'https://kelleherford.com'
    total_cars = cars_found(main_soup, html_tag='p', attrs={'class': 'text-primary'})
    logging.info(f'Total cars: {total_cars}')
    current_page = 1
    current_loop_runs = 0
    while len(list_of_car_info) < total_cars:
        current_loop_runs += 1
        logging.info(f'Scraping on Page: {current_page}')
        # Scrape all cars on a single page
        all_vehicle_card = main_soup.find_all('div', {'class': 'card-1-inventory-item'})
        for vehicle_card_soup in all_vehicle_card:
            list_of_car_info.append(get_car_info(vehicle_card_soup, url, base_url))

        # print(f'Cars done: {len(list_of_car_info)}')
        # visi all pages
        url = url.replace(f'pag={current_page}', f'pag={current_page + 1}')
        current_page += 1
        time.sleep(2)

        main_soup, driver = main_soup_n_driver_scroll_down(url, driver)

        if current_loop_runs > FAIL_SAFE_RUNS:
            # print(current_loop_runs, FAIL_SAFE_RUNS)
            break

    driver.quit()

    return list_of_car_info


def rainbowford(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return list: list of car_info dictionaries
    """

    def get_car_info(soap, car_image_link, url, car_page_url):
        """ Return all the information in the car's card """

        car_price = get_car_price(soap, html_tag='span', attrs={'class': 'h3'})
        if car_price is None:
            car_price = get_car_price(soap, html_tag='td', attrs={'class': 'table-rw'})

        car_info = {"car_name": get_car_name(soap, 'h1', {'class': 'title h2'}),
                    "price": car_price, "car_page_link": car_page_url,
                    "img_link": car_image_link, "website": url}

        raw_car_specs = get_car_specs_raw(soap, html_tag='tr', attrs={})

        search_dict = {"body_style": "Bodystyle\n", "mileage": "Mileage\n", "exterior": "Exterior Color\n",
                       "drivetrain": "Drivetrain\n", "transmission": "Transmission\n", "engine": "Engine\n"}

        car_specs = extract_car_specs(raw_car_specs, search_dict)

        car_info.update(car_specs)

        logging.info(f'Done for car: {car_info["car_name"]}')

        return car_info

    # # # Function Main
    main_soup, driver = main_soup_n_driver_scroll_down(url)

    # script
    list_of_car_info = []
    # Scrape First Page
    car_cards_list = main_soup.find_all('div', {'class': 'listing-list-loop'})
    for car_card in car_cards_list:
        # Get picture link
        car_image_link = car_card.find('img', {'class': 'img-responsive wp-post-image'})["src"]

        single_car_url = car_card.find('a', {'class': 'rmv_txt_drctn'})["href"]
        soup, driver = main_soup_n_driver_scroll_down(single_car_url, driver)

        list_of_car_info.append(get_car_info(soup, car_image_link, url, single_car_url))

    # Scrape Rest of the pages
    next_page_link_html = main_soup.find("a", {'class': 'next page-numbers'})
    while next_page_link_html is not None:
        next_page_link = next_page_link_html["href"]

        # Go to next page
        main_soup, driver = main_soup_n_driver_scroll_down(next_page_link, driver)

        car_cards_list = main_soup.find_all('div', {'class': 'listing-list-loop'})
        for car_card in car_cards_list:
            # Get picture link
            car_image_link = car_card.find('img', {'class': 'img-responsive wp-post-image'})["src"]

            single_car_url = car_card.find('a', {'class': 'rmv_txt_drctn'})["href"]
            soup, driver = main_soup_n_driver_scroll_down(single_car_url, driver)

            list_of_car_info.append(get_car_info(soup, car_image_link, url, single_car_url))

        # Check next page
        next_page_link_html = main_soup.find("a", {'class': 'next page-numbers'})

    driver.quit()

    return list_of_car_info
