# Import libraries
#import pandas as pd
import time
import os
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException

#import token
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC76e55aab103ecc85c59dcb3b7189444e"
auth_token = '6003a2aa36d6aa34502e933033a4b386' #os.environ["TWILIO_AUTH_TOKEN"]

## Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")

# Silent download of drivers
logging.getLogger('WDM').setLevel(logging.NOTSET)
os.environ['WDM_LOG'] = 'False'

# Creating a driver objet to manage browser 
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

# Defining the url we want to scrape
url_pages = {"Travel Lodge": "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodations",} 

for page in url_pages:    
    # Ask the driver to direct us to the url
    driver.get(url_pages[page])
    print("Processing" , url_pages[page] )
    # Get table view
    time.sleep(2)
    
    select = Select(driver.find_element(By.ID,'box-widget_ProductSelection'))
    # select by visible text
    select.select_by_visible_text('Yosemite Valley Lodge')
    time.sleep(1)

    select = Select(driver.find_element(By.ID,'box-widget_UnitCount'))
    
    select.select_by_visible_text('3')

    select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[0]'))
    select.select_by_visible_text('1')
    select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[1]'))
    select.select_by_visible_text('1')
    select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[2]'))
    select.select_by_visible_text('1')
    
    driver.find_element(By.ID, "box-widget_ArrivalDate").click()

    select = Select(driver.find_element(By.CLASS_NAME,'ui-datepicker-month'))
    select.select_by_visible_text('Jun')

    days_selector = driver.find_elements(By.CSS_SELECTOR, 'tr')
    
    avail = driver.find_elements(By.CSS_SELECTOR, '.ui-datepickerAvail-significant:not(.ui-datepicker-unselectable), .ui-datepickerAvail-limited:not(.ui-datepicker-unselectable)')

    days = []

    try:
        for day in avail:
            if day.text != '':
                days.append(int(day.text))
    except StaleElementReferenceException as Exception:
         print('no hay dias disponibles')      

    finally:
        counter = 1
        for i,day in enumerate(days):
            if i == 0: 
                continue
            if days[i] == days[i-1] + 1:
                counter += 1
            else: 
                counter = 1

            if counter == 4:
                break

        if counter > 4:
            client = Client(account_sid, auth_token)
            message = client.messages.create( body="Hay disponibilidad!",from_="+18882985392",to="+15629556375")
    
