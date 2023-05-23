# Import libraries
import time
import datetime
import os
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from twilio.rest import Client
from token_twilio import account_twilio, key_twilio, to_phone, from_phone, alt_phone


# Set Twilio to send sms messages
# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = account_twilio
auth_token = key_twilio #os.environ["TWILIO_AUTH_TOKEN"]


## Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")

# Silent download of drivers
logging.getLogger('WDM').setLevel(logging.NOTSET)
os.environ['WDM_LOG'] = 'False'

# Creating a driver objet to manage browser 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Defining the url we want to scrape
url_pages = {"Travel Lodge": "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodations",} 

# Get data from the webpage of interest
for page in url_pages:    
    # Ask the driver to direct us to the url
    driver.get(url_pages[page])
    print("\n","Processing" , url_pages[page], datetime.datetime.now() )

    time.sleep(2)
    
    select = Select(driver.find_element(By.ID,'box-widget_ProductSelection'))

    # select Lodge of interest by visible text
    select.select_by_visible_text('Yosemite Valley Lodge')
    time.sleep(1)

    # select Number of rooms by visible text
    select = Select(driver.find_element(By.ID,'box-widget_UnitCount'))
    select.select_by_visible_text('1')

    # select Number of children in the room by visible text
    select = Select(driver.find_element(By.ID,'box-widget_Children'))
    select.select_by_visible_text('1')
    # The following lines are for setting multiple rooms
    #select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[0]'))
    #select.select_by_visible_text('1')
    #select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[1]'))
    #select.select_by_visible_text('1')
    #select = Select(driver.find_element(By.ID,'box-widget_MultiUnitCount_Children[2]'))
    #select.select_by_visible_text('1')
    time.sleep(1)

    # open calendar of check-in dates
    driver.find_element(By.ID, "box-widget_ArrivalDate").click()

    # select month of check-in to evaluate
    chosen_month = 'Jun'
    select = Select(driver.find_element(By.CLASS_NAME,'ui-datepicker-month'))
    select.select_by_visible_text(chosen_month)
    
    time.sleep(1)
    days_selector = driver.find_elements(By.CSS_SELECTOR, 'tr')
    
    avail = driver.find_elements(By.CSS_SELECTOR, '.ui-datepickerAvail-significant:not(.ui-datepicker-unselectable), .ui-datepickerAvail-limited:not(.ui-datepicker-unselectable)') #
    
    days = []
    try:
        for day in avail:
            if day.text != '':
                days.append(int(day.text))
    except StaleElementReferenceException as Exception:
        #pass
        print('no hay dias disponibles')      

    finally:
        counter = 1
        for i,day in enumerate(days):
            print(day)
            if i == 0: 
                continue
            if days[i] == days[i-1] + 1:
                counter += 1
            else:
                # restart counter
                counter = 1

            if counter == 4:
                break
    
        interesting_dates = [8,9,10,11]        
        if (counter == 4) & set(interesting_dates).issubset(days):
            client  = Client(account_sid, auth_token)
            print('Hay disponibilidad ')
            print(' ,'.join(str(day) for day in days))
            message = client.messages.create( body='Hay disponibilidad en ' + chosen_month + ' ' + ' ,'.join(str(day) for day in days),from_=from_phone,to=to_phone)
            message = client.messages.create( body='Hay disponibilidad en ' + chosen_month + ' ' + ' ,'.join(str(day) for day in days),from_=from_phone,to=alt_phone)