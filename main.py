import time
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import datetime
import json
import pandas as pd
import numpy as np
import os


## initalize headless driver config
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

options = webdriver.ChromeOptions()
options.headless = False
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

## config
dyear = '2023'
dmonth = '02'
ddate = '01'

# dyear = '2023'
# dmonth = '03'
# ddate = '11'
# ryear = '2023'
# rmonth = '03'
# rdate = '21'
from_port = 'hkg'
to_port = 'lhr'

# from_port = 'lhr'
# to_port = 'hkg'

# 11/3 Hong Kong to Paris
# 21/3 London to Hong Kong

############utility functions

def text_to_seconds(text):
    import re
    if re.search(r'\d+$', text) is not None:
        text = text+'m'

    in_seconds = {'d': 60 *60* 60, 'h': 60 * 60, 'm': 60}
    seconds = sum(int(num) * in_seconds[weight] for num, weight in re.findall(r'(\d+)\s?(m|d|h)', text))
    return seconds

def get_count_in_directory(directory_name):
    import os
    path = os.path.join(os.getcwd(),directory_name) # /Users/doge/python-web-scraping/path
    return len(os.listdir(path))

###############

def map_port_name(site, port_code):
        
    if site == 'expedia':
        match port_code:
            case 'hkg':
                port_name = '%3AHong%20Kong%20%28HKG-Hong%20Kong%20Intl.%29%2C'
            case 'cdg':
                port_name = '%3AParis%20%28CDG%20-%20Roissy-Charles%20de%20Gaulle%29%2C'
            case 'lhr':
                port_name = '%3ALondon%20%28LHR-Heathrow%29%2C'
            case _:
                ''
    return port_name

def generate_url(site, from_port, to_port,dyear,dmonth,ddate):
    ## @dev: setup url per config date
    if site == 'expedia':
        from_port = map_port_name(site,from_port)
        to_port = map_port_name(site,to_port)
        departure = f'%3A{dyear}%2F{dmonth}%2F{ddate}'
        url = f'https://www.expedia.com.hk/Flights-Search?langid=2057&leg1=from{from_port}to{to_port}departure{departure}TANYT&mode=search&options=carrier%3A%2A%2Ccabinclass%3A%2Cmaxhops%3A1%2Cnopenalty%3AN&pageId=0&passengers=adults%3A1%2Cchildren%3A0%2Cinfantinlap%3AN&trip=oneway'

    if site == 'skyscanner':
        departure = f'{dyear[2:4]}{dmonth}{ddate}'
        url = f'https://www.skyscanner.com.hk/transport/flights/{from_port}/{to_port}/{departure}/?adults=1&adultsv2=1&cabinclass=economy&children=0&childrenv2=&destinationentityid=27544008&inboundaltsenabled=false&infants=0&originentityid=27542065&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0'

    return url

def fetch_data(site):
    driver = webdriver.Chrome(options=options, executable_path=r'.\chromedriver_mac64\chromedriver')
    if site == 'expedia':
        url = expedia_url
    if site == 'skyscanner':
        url = skyscanner_url

    driver.get(url)
    # driver.get_screenshot_as_file('/temp/fetch.png') 
    time.sleep((1 * 60))
    page_source = driver.page_source
    driver.quit()
    return page_source

def convert_to_json(site, page_source):

    ## expedia
    if site == 'expedia':
        soup = BeautifulSoup(page_source, 'lxml')
        items = soup.find_all('li', attrs={'data-test-id': 'offer-listing'})
        count = 0
        options_dict = {}

        for index, item in enumerate(items):

            option = f'{site}_{index + 1}'
            search_start = f'{dyear}{dmonth}{ddate}'
            departure_time = item.find('span', attrs={'data-test-id': 'departure-time'}).text            
            arrival_departure_texts = item.find('div', attrs={'data-test-id': 'arrival-departure'}).text.split('(')
            from_port = arrival_departure_texts[1].split(')')[0]
            to_port = arrival_departure_texts[2].split(')')[0]
            arrival_departure = f'{from_port} - {to_port}'
            journey_duration_texts = item.find('div', attrs={'data-test-id': 'journey-duration'}).text.split('(')
            journey_duration = journey_duration_texts[0]
            stop = journey_duration_texts[1][0:len(journey_duration_texts[1])-1]
            flight_operated = item.find('div', attrs={'data-test-id': 'flight-operated'}).text
            lookup_price_texts = item.find('span', class_='uitk-price-a11y is-visually-hidden').text.split('HK$')
            lookup_price = lookup_price_texts[1].replace(",", "")
            created_at= str(datetime.datetime.now())

            options_dict[option] = {'search_start': search_start,
                                    'departure_time': departure_time,
                                    'arrival_departure':  arrival_departure,
                                    'journey_duration': journey_duration,
                                    'stop': stop,
                                    'flight_operated': flight_operated,
                                    'lookup_price': lookup_price,
                                    'created_at': created_at}

            count += 1
        file_sequence = get_count_in_directory('results') + 1
        with open(f'./results/flight_{site}_{file_sequence}.json', 'w+') as f:
            f.write(json.dumps(options_dict))
        print(f'--------------Search in {site} completed, {count} record returned.--------------')

    if site == 'skyscanner':
        soup = BeautifulSoup(page_source, 'lxml')
        items = soup.find_all('div', class_='BpkTicket_bpk-ticket__NTM0M')
        count = 0
        options_dict = {}

        for index, item in enumerate(items):

            option = f'{site}_{index + 1}'
            search_start = f'{dyear}{dmonth}{ddate}'
            from_time = item.find('div', class_ ='LegInfo_routePartialDepart__NzEwY').find('span').find('div').find('span').text
            to_time = item.find('div', class_ ='LegInfo_routePartialArrive__Y2U1N').find('span').find('div').find('span').text
            departure_time= f"{from_time} - {to_time}"
            from_port = item.find('div', class_ ='LegInfo_routePartialDepart__NzEwY').find('span',class_='BpkText_bpk-text__ZWIzZ BpkText_bpk-text--body-default__MzkyN').find('div').find('span').text
            to_port = item.find('div', class_ ='LegInfo_routePartialArrive__Y2U1N').find('span',class_='BpkText_bpk-text__ZWIzZ BpkText_bpk-text--body-default__MzkyN').find('div').find('span').text
            arrival_departure = f"{from_port} - {to_port}"
            journey_duration= item.find('div',class_='LegInfo_stopsContainer__NWIyN').find('span', class_ ='BpkText_bpk-text__ZWIzZ BpkText_bpk-text--xs__MTAxY Duration_duration__NmUyM').text
            stop = item.find('div',class_='LegInfo_stopsLabelContainer__MmM0Z').find('span').text
            flight_operated= item.find('div', class_='LegLogo_legImage__MmY0Z').find('div').find('img')['alt']
            lookup_price_texts=item.find('div', class_='Price_mainPriceContainer__MDM3O').find('span').text.split('HK$')
            lookup_price = lookup_price_texts[1].replace(",", "")
            created_at= str(datetime.datetime.now())

            options_dict[option] = {'search_start': search_start,
                                    'departure_time': departure_time,
                                    'arrival_departure':  arrival_departure,
                                    'journey_duration': journey_duration,
                                    'stop': stop,
                                    'flight_operated': flight_operated,
                                    'lookup_price': lookup_price,
                                    'created_at': created_at}
            count += 1
        file_sequence = get_count_in_directory('results') + 1
        with open(f'./results/flight_{site}_{file_sequence}.json', 'w+') as f:
            f.write(json.dumps(options_dict))
        print(f'--------------Search in {site} completed, {count} record returned.--------------')

def run_pipline():
    print('--------------Pieline Start--------------')
    # Import libraries
    import glob
    import os
    import pandas as pd

    # Get CSV files list from a folder
    pwd = os.getcwd()
    path = os.path.join(pwd,"results")
    json_files = glob.glob(path + "/*.json")

    # Read each CSV file into DataFrame
    # This creates a list of dataframes
    df_list = (pd.read_json(file, orient = 'index') for file in json_files)

    # Concatenate all DataFrames
    big_df   = pd.concat(df_list, ignore_index=True)

    print('--------------Pieline completed--------------')
    return big_df


#########################################################

expedia_url = generate_url('expedia', from_port, to_port,dyear,dmonth,ddate)
skyscanner_url = generate_url('skyscanner', from_port, to_port,dyear,dmonth,ddate)

expedia_page_source = fetch_data('expedia')
skyscanner_page_source = fetch_data('skyscanner')

convert_to_json('expedia',expedia_page_source)
convert_to_json('skyscanner',skyscanner_page_source)





## Jupter notebook
#df = run_pipline()

## scheduler script: call main function

# if __name__ == '__main__':
#     while True:
#         find_jobs()
#         time_wait = 10
#         print(f'Waiting {time_wait} seconds...')
#         time.sleep((time_wait * 60))
