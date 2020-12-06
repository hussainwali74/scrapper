import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd

def process_mileage(raw_num='2,000  km'):
    comma_wala_num, distance_unit = raw_num.split()
    num_splitted = comma_wala_num.split(',')
    distance = "".join( num_splitted )
    return ' '.join( [distance, distance_unit] )

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
            car_info["mileage"] = process_mileage( res )

        if search_condition in elem:
            res = elem.split(search_condition)[1]
            car_info["condition"] = res

        if search_exterior in elem:
            res = elem.split(search_exterior)[1]
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

        if search_vin in elem:
            res = elem.split( search_vin )[1]
            car_info["vin"] = res

    return car_info

def get_car_info(soap):
    """ Return all the information in the car's card """
    car_info = {}

    car_info["car_name"] = get_car_name(soap)

    raw_car_specs = get_raw_car_specs(soap)

    car_specs = extract_car_specs(raw_car_specs)

    car_info.update(car_specs)

    return car_info

def get_car_info_from_web(url_page='https://www.regalmotorsltd.com/used/used-vehicle-inventory.html'):
    url_page = 'https://www.regalmotorsltd.com/used/used-vehicle-inventory.html'

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Firefox(executable_path='/home/teemo/softwares/geckodriver')
    # get web page
    driver.get(url_page)

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
