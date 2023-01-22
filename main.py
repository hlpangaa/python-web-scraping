import time
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import datetime
import json

## initalize headless driver config
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

options = webdriver.ChromeOptions()
options.headless = True
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
dmonth = '03'
ddate = '01'
ryear = '2023'
rmonth = '03'
rdate = '15'

## raw url
expedia_url = 'https://www.expedia.com.hk/Flights-Search?langid=2057&leg1=from%3AHong%20Kong%20%28HKG-Hong%20Kong%20Intl.%29%2Cto%3ALondon%20%28LHR-Heathrow%29%2Cdeparture%3A2023%2F02%2F05TANYT&leg2=from%3ALondon%20%28LHR-Heathrow%29%2Cto%3AHong%20Kong%20%28HKG-Hong%20Kong%20Intl.%29%2Cdeparture%3A2023%2F02%2F19TANYT&mode=search&options=carrier%3A%2A%2Ccabinclass%3A%2Cmaxhops%3A1%2Cnopenalty%3AN&pageId=0&passengers=adults%3A2%2Cchildren%3A0%2Cinfantinlap%3AN&trip=roundtrip'
skyscanner_url = 'https://www.skyscanner.com.hk/transport/flights/hkg/lhr/230205/230219/?adultsv2=2&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=false&rtn=1'

def update_url(url):
    ## @dev: setup url per config date
    domain = urlparse(url).netloc
    if domain == 'www.expedia.com.hk':
        url = url.replace("2023%2F02%2F05TANYT&leg2",f"{dyear}%2F{dmonth}%2F{ddate}TANYT&leg2").replace("2023%2F02%2F19TANYT&mode=search&options",f"{ryear}%2F{rmonth}%2F{rdate}TANYT&mode=search&options")
    if domain == 'www.skyscanner.com.hk':
        url = url.replace("230205/230219",f"{dyear[2:4]}{dmonth}{ddate}/{ryear[2:4]}{rmonth}{rdate}")
    return url

def fetch_data(site):
    driver = webdriver.Chrome(options=options, executable_path=r'.\chromedriver_mac64\chromedriver')
    if site == 'expedia':
        url = expedia_url
    if site == 'skyscanner':
        url = skyscanner_url

    driver.get(url)
    # driver.get_screenshot_as_file('/temp/fetch.png') 
    page_source = driver.page_source
    driver.quit()
    return page_source

def convert_to_json(site, page_source):

    ## expedia
    if site == 'expedia':
        print(f'..........start {site}:')
        soup = BeautifulSoup(page_source, 'lxml')
        items = soup.find_all('li', attrs={'data-test-id': 'offer-listing'})
        count = 0
        options_dict = {}

        for index, item in enumerate(items):

            option = index + 1
            departure_time = item.find('span', attrs={'data-test-id': 'departure-time'}).text
            arrival_departure = item.find('div', attrs={'data-test-id': 'arrival-departure'}).text
            journey_duration = item.find('div', attrs={'data-test-id': 'journey-duration'}).text
            flight_operated = item.find('div', attrs={'data-test-id': 'flight-operated'}).text
            lookup_price = item.find('span', class_='uitk-price-a11y is-visually-hidden').text
            created_at= str(datetime.datetime.now())

            options_dict[option] = {'departure_time': departure_time,
                                    'arrival_departure':  arrival_departure,
                                    'journey_duration': journey_duration,
                                    'flight_operated': flight_operated,
                                    'lookup_price': lookup_price,
                                    'created_at': created_at}

            # with open(f'./results/flight_{site}.txt', 'a+') as f:
            #     if index == 0:
            #         f.write(f'---------------------{datetime.datetime.now()}: {expedia_url}---------------------,\n')
            #     else: 
            #         f.write(f'option: {index},\n'
            #                 f'departure_time: {departure_time},\n'
            #                 f'arrival_departure: {arrival_departure},\n'
            #                 f'journey_duration: {journey_duration}\n'
            #                 f'flight_operated: {flight_operated}\n'
            #                 f'lookup_price: {lookup_price}\n'
            #                 f'created_at: {datetime.datetime.now()}\n')

            # print(f'departure_time: {departure_time},\n'
            #         f'arrival_departure: {arrival_departure},\n'
            #         f'journey_duration: {journey_duration}\n'
            #         f'flight_operated: {flight_operated}\n'
            #         f'lookup_price: {lookup_price}\n')
            count += 1
        
        with open(f'./results/flight_{site}.json', 'w+') as f:
            f.write(json.dumps(options_dict))
        print(f'--------------Search in {site} completed, {count} record returned.--------------')

    if site == 'skyscanner':
        print(f'..........start {site}:')
        soup = BeautifulSoup(page_source, 'lxml')
        items = soup.find_all('div', class_='BpkTicket_bpk-ticket__NTM0M')
        count = 0
        options_dict = {}

        for index, item in enumerate(items):

            option = index + 1
            departure_time=item.find('div',class_='LegInfo_routePartialDepart__NzEwY').find('span', class_='BpkText_bpk-text__ZWIzZ BpkText_bpk-text--subheading__MDhjZ').text
            departure = item.find('div', class_ ='LegInfo_routePartialDepart__NzEwY').find('div').find('span').text
            arrival = item.find('div', class_ ='LegInfo_routePartialArrive__Y2U1N').find('div').find('span').text
            arrival_departure= f"From {departure} to {arrival}"
            journey_duration= item.find('span', class_ ='BpkText_bpk-text__ZWIzZ BpkText_bpk-text--xs__MTAxY Duration_duration__NmUyM').text
            flight_operated= item.find('div', class_='LegLogo_legImage__MmY0Z').find('div').find('img')['alt']
            lookup_price=item.find('div', class_='Price_mainPriceContainer__MDM3O').find('span').text
            created_at= str(datetime.datetime.now())

            options_dict[option] = {'departure_time': departure_time,
                                    'arrival_departure':  arrival_departure,
                                    'journey_duration': journey_duration,
                                    'flight_operated': flight_operated,
                                    'lookup_price': lookup_price,
                                    'created_at': created_at}

            # with open(f'./results/flight_{site}.txt', 'a+') as f:
            #     if index == 0:
            #         f.write(f'---------------------{datetime.datetime.now()}: {skyscanner_url}---------------------,\n')
            #     else: 
            #         f.write(f'option: {index},\n'
            #                 f'departure_time: {departure_time},\n'
            #                 f'arrival_departure: {arrival_departure},\n'
            #                 f'journey_duration: {journey_duration}\n'
            #                 f'flight_operated: {flight_operated}\n'
            #                 f'lookup_price: {lookup_price}\n'
            #                 f'created_at: {datetime.datetime.now()}\n')

            # print(f'departure_time: {departure_time},\n'
            #         f'arrival_departure: {arrival_departure},\n'
            #         f'journey_duration: {journey_duration}\n'
            #         f'flight_operated: {flight_operated}\n'
            #         f'lookup_price: {lookup_price}\n')
            count += 1
        with open(f'./results/flight_{site}.json', 'w+') as f:
            f.write(json.dumps(options_dict))
        print(f'--------------Search in {site} completed, {count} record returned.--------------')

def run_pipline(data):
    print('working.......')
    return data
    # departure_time: 23:00,
    # arrival_departure: From 23:00 to 05:50,
    # journey_duration: 14h 50
    # flight_operated: British Airways
    # lookup_price: HK$8,648



#########################################################

# expedia_url = update_url(expedia_url)
skyscanner_url = update_url(skyscanner_url)

# expedia_page_source = fetch_data('expedia')
skyscanner_page_source = fetch_data('skyscanner')

#convert_to_json('expedia',expedia_page_source)
convert_to_json('skyscanner',skyscanner_page_source)

#run_pipline

## scheduler script: call main function

# if __name__ == '__main__':
#     while True:
#         find_jobs()
#         time_wait = 10
#         print(f'Waiting {time_wait} seconds...')
#         time.sleep((time_wait * 60))
