# import urllib.request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
# import pandas as pd

# ==========  Helper functions ==========
def process_mileage(raw_num='2,000  km'):
    try:
        comma_wala_num, distance_unit = raw_num.split()
        num_splitted = comma_wala_num.split(',')
        distance = "".join( num_splitted )
        result = ' '.join( [distance, distance_unit] )
    except:
        result = ""
    return result


def extract_integer(price_string):
    try:
        price = re.sub(r'[^\d.]', '', price_string)
    except:
        price = None
    return price
# ========== main function ==========
def get_car_info_from_web(url: str) -> list:

    if "regalmotors" in url:
        return regal_n_junct_north(url)
    elif "junctionmotors" in url:
        return regal_n_junct_north(url)
    elif "northstarfordsales" in url:
        return regal_n_junct_north(url)
    elif "woodridgeford" in url:
        return wood(url)
    elif "zarownymotors" in url:
        return zarowny_n_westlock(url)
    elif "westlockford" in url:
        return zarowny_n_westlock(url)
    elif "fourlaneford" in url:
        return fourlane(url)
    elif "marlborough" in url:
        return marlborough(url)
    elif "universalford" in url:
        return universalford(url)
    # elif "westlockford" in url:
    #     return westlockford(url)

# ========== Web scrapping functions ==========


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
        search_condition = 'Condition: '
        search_exterior = 'Exterior: '
        search_drivetrain = 'Drivetrain: '
        search_transmission = 'Transmission: '
        search_engine = 'Engine: '
        search_vin = 'vin: '

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
                car_info["mileage"] = process_mileage(res)

            if search_condition in elem:
                res = elem.split(search_condition)[1]
                car_info["condition"] = res

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

    def get_car_info(soap):
        """ Return all the information in the car's card """
        car_info = {"car_name": get_car_name(soap), "price": get_car_price(soap)}

        raw_car_specs = get_raw_car_specs(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
    # get web page
    driver.get(url)

    # execute script to scroll down the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(9)
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
            list_of_car_info.append(get_car_info(div_padding))

    # print(list_of_car_info)

    # This can be improved by using a context and having that quit it
    driver.quit()

    return list_of_car_info


def wood(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """
    def get_car_name(soap):
        """ Intended to return single name """
        html_car_name = soap.find('p')
        try:
            car_name = html_car_name.getText()
        except:
            car_name = ""
        return car_name

    def get_car_mileage(soap):
        """ Intended to return single value """
        search_mileage = 'Mileage:'

        html_mileage_payment = soap.find('p', attrs={'class': 'mileage-payment'})
        try:
            car_mileage = html_mileage_payment.getText()
            car_mileage = car_mileage.split(search_mileage)[1]
            mileage = process_mileage(car_mileage)
        except:
            mileage = ""
        return mileage

    def get_car_specs_raw(soap):
        """Made to handle single car's specs
        :return List containing pieces of car's information
        """
        car_specs = []
        for tr in soap.find_all('tr'):
            car_specs.append(tr.getText())
        return car_specs

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_body_style = 'Body Style:'
        search_exterior = 'Exterior Colour:'
        search_drivetrain = 'Drivetrain:'
        search_transmission = 'Transmission:'
        search_engine = 'Engine:'
        search_city = 'City:'

        car_info = {}

        for elem in raw_car_specs:
            if search_body_style in elem:
                res = elem.split(search_body_style)[1]
                car_info["body_style"] = res

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

            if search_city in elem:
                res = elem.split(search_city)[1]
                car_info["city"] = res

        return car_info

    def get_car_info(soap):
        """ Return all the information in the car's card """
        car_info = {"car_name": get_car_name(soap), "mileage": get_car_mileage(soap)}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
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
    soup = BeautifulSoup(page, 'html.parser')

    list_of_car_info = []
    all_class_outside_box = soup.find_all('div', attrs={'class': 'row listing-page-row-margin-0'})
    for class_outside_box in all_class_outside_box:
        list_of_car_info.append(get_car_info(class_outside_box))

    driver.quit()

    return list_of_car_info


def zarowny_n_westlock(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """
    def get_car_name(soap):
        """ Intended to return single name """
        html_h4_car_name = soap.find('h4')
        html_h5_car_name = soap.find('h5')
        try:
            h4_name = html_h4_car_name.getText()
            h5_name = html_h5_car_name.getText()
            if len(h5_name):
                if "westlockford" in url:
                    h5_name = h5_name.split(",")[0]
                car_name = h4_name + " - " + h5_name
            else:
                car_name = h4_name
        except:
            car_name = ""
        return car_name

    def get_car_specs_raw(soap) -> dict:
        search_mileage = 'Odometer'
        search_exterior = 'Exterior Colour:'
        search_drivetrain = 'Drivetrain:'
        search_transmission = 'Transmission:'
        search_engine = 'Engine:'
        search_city = 'City:'

        car_info = {}
        car_specs_pieces = []
        car_specs = []
        for elem in soap.find('dl').findChildren():
            car_specs_pieces.append(elem.getText())

        for elem in range(0, len(car_specs_pieces), 2):
            car_specs.append(car_specs_pieces[elem] + car_specs_pieces[elem + 1])

        return car_specs

    def extract_car_specs(raw_car_specs: list) -> dict:
        search_mileage = 'Odometer'
        search_exterior = 'Color'
        search_drivetrain = 'Drivetrain'
        search_transmission = 'Transmission'
        search_engine = 'Engine'

        car_info = {}

        for elem in raw_car_specs:
            if search_mileage in elem:
                res = elem.split(search_mileage)[1]
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

    def get_car_info(soap):
        """ Return all the information in the car's card """
        car_info = {"car_name": get_car_name(soap)}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
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
    soup = BeautifulSoup(page, 'html.parser')

    list_of_car_info = []
    all_class_vehicle_card = soup.find_all('li', attrs={'class': 'vehicle-card-used'})

    for class_vehicle_card in all_class_vehicle_card:
        list_of_car_info.append( get_car_info(class_vehicle_card) )

    driver.quit()

    return list_of_car_info

def fourlane(url: str) -> list:
    """
    This Major function has minor website specific functions. They are defined in this function to avoid
    function's names overlapping.
    :param url: Website url from where to scrape
    :return:
    """

    def get_car_name_n_city(soap):
        """ soap should be car info page """
        car_info = {}
        car_title = soap.find('h1')
        car_name = car_title.find('span')
        city = car_title.getText().split('for sale in ')[1]
        car_info["car_name"] = car_name.getText()
        car_info["city"] = city
        return car_info

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

    def get_car_info(soap):
        """ Return all the information in the car's card """
        car_info = get_car_name_n_city(soap)

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
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
    base_url = 'https://www.fourlaneford.com'
    # Get links of all car's information page
    all_a_vehicle_media = main_soup.find_all('a', href=True, attrs={'class': 'vehicle media'})
    for a_vehicle_media in all_a_vehicle_media:
        if a_vehicle_media.has_attr("href"):
            url = a_vehicle_media["href"]
            driver.get(base_url + url)
            # execute script to scroll down the page
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            time.sleep(1)

            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')

            list_of_car_info.append(get_car_info(soup))

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
                car_info["mileage"] = res + ' km'

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

    def get_car_info(soap):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap)}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
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
            url = class_title_link["href"]
            print(class_title_link["href"])
            time.sleep(2)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            list_of_car_info.append(get_car_info(soup))

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

    def get_car_info(soap):
        """ Return all the information in the car's card """

        car_info = {"car_name": get_car_name(soap)}

        raw_car_specs = get_car_specs_raw(soap)

        car_specs = extract_car_specs(raw_car_specs)

        car_info.update(car_specs)

        return car_info

    def get_cars_from_single_page(main_soap):
        list_of_car_info = []  # car_info: dict
        # Get links of all car's information page
        all_class_vehicle_title = main_soap.find_all('div', attrs={'class': 'vehicle-title'})
        for class_vehicle_title in all_class_vehicle_title:
            class_title_link = class_vehicle_title.find('a')
            if class_title_link.has_attr("href"):
                url = class_title_link["href"]
                print(class_title_link["href"])
                time.sleep(2)
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')

                list_of_car_info.append( get_car_info(soup) )

        return list_of_car_info

    page = requests.get(url)
    main_soup = BeautifulSoup(page.content, 'html.parser')

    list_of_car_info = []
    pagination_next = main_soup.find('a', attrs={'class': 'pagination-next'})
    while pagination_next.has_attr('href'):
        next_page_link = pagination_next["href"]

        page = requests.get(next_page_link)
        main_soup = BeautifulSoup(page.content, 'html.parser')
        list_of_car_info.extend( get_cars_from_single_page(main_soup) )

        # Repeat
        pagination_next = main_soup.find('a', attrs={'class': 'pagination-next'})

    return list_of_car_info


# ========== It might not be needed
# def westlockford(url: str) -> list:
#     """
#     This Major function has minor website specific functions. They are defined in this function to avoid
#     function's names overlapping.
#     :param url: Website url from where to scrape
#     :return:
#     """
#
#     def get_car_name(soap):
#         """ Intended to return single name """
#         html_h4_car_name = soap.find('h4')
#         html_h5_car_name = soap.find('h5')
#         try:
#             h4_name = html_h4_car_name.getText()
#             h5_name = html_h5_car_name.getText()
#             if len(h5_name):
#                 h5_name = h5_name.split(",")[0]
#                 car_name = h4_name + " - " + h5_name
#             else:
#                 car_name = h4_name
#         except:
#             car_name = ""
#         return car_name
#
#     def get_car_specs_raw(soap) -> list:
#
#         car_info = {}
#         car_specs_pieces = []
#         car_specs = []
#         for elem in soap.find('dl').findChildren():
#             car_specs_pieces.append(elem.getText())
#
#         for elem in range(0, len(car_specs_pieces), 2):
#             car_specs.append(car_specs_pieces[elem] + car_specs_pieces[elem + 1])
#
#         return car_specs
#
#     def extract_car_specs(raw_car_specs: list) -> dict:
#         search_mileage = 'Odometer'
#         search_exterior = 'Color'
#         search_drivetrain = 'Drivetrain'
#         search_transmission = 'Transmission'
#         search_engine = 'Engine'
#
#         car_info = {}
#
#         for elem in raw_car_specs:
#             if search_mileage in elem:
#                 res = elem.split(search_mileage)[1]
#                 car_info["mileage"] = res
#
#             if search_exterior in elem:
#                 res = elem.split(search_exterior)[1]
#                 car_info["exterior"] = res
#
#             if search_drivetrain in elem:
#                 res = elem.split(search_drivetrain)[1]
#                 car_info["drivetrain"] = res
#
#             if search_transmission in elem:
#                 res = elem.split(search_transmission)[1]
#                 car_info["transmission"] = res
#
#             if search_engine in elem:
#                 res = elem.split(search_engine)[1]
#                 car_info["engine"] = res
#
#         return car_info
#
#     def get_car_info(soap):
#         """ Return all the information in the car's card """
#         car_info = {"car_name": get_car_name(soap)}
#
#         raw_car_specs = get_car_specs_raw(soap)
#
#         car_specs = extract_car_specs(raw_car_specs)
#
#         car_info.update(car_specs)
#
#         return car_info
#
#     driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
#     # get web page
#     driver.get(url)
#     # execute script to scroll down the page
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
#     time.sleep(2)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
#     time.sleep(4)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
#     time.sleep(3)
#
#     page = driver.page_source
#     main_soup = BeautifulSoup(page, 'html.parser')
#
#     list_of_car_info = []
#     all_class_vehicle_card = main_soup.find_all('li', attrs={'class': 'vehicle-card-used'})
#
#     for class_vehicle_card in all_class_vehicle_card:
#         list_of_car_info.append(get_car_info(class_vehicle_card))
#     #     print( get_car_info(class_vehicle_card) )
#
#     driver.quit()
#
#     return list_of_car_info
