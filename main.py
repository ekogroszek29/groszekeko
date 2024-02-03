import requests
from bs4 import BeautifulSoup
import datetime
from deta import Deta

#załadowanie danych do bazy
def insert_period(key,products):
    return db.put({"key": key, "product":products})

# Define the URL of the website to scrape
url = 'https://sklep.tauron.pl/'

# Use requests to fetch the content of the page
response = requests.get(url)

# If the page was fetched successfully, parse the content with BeautifulSoup
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize an empty list to hold the product names and prices
    products = []

    # Find all product info containers for both classes
    product_containers_md = soup.find_all('div', class_='col-md-7 info product-info-right')
    product_containers_sm = soup.find_all('div', class_='col-sm-7 info product-info-right')
    
    # Combine both lists of containers
    product_containers = product_containers_md + product_containers_sm

    for container in product_containers:
        # Extract the product name
        name = container.find('h3').text.strip()
        
        # Try to find the price, if available
        price_tag = container.find('p', class_='price magenta')
        if price_tag:
            # Extract text, remove " zł" and non-numeric characters, then convert to int
            price_text = price_tag.text.strip().replace(' zł', '').replace(' ', '').replace(',', '.')
            # Assuming prices are in a format that includes decimals, convert to float then to int
            price = int(float(price_text))
        else:
            price = 'Price not available'

        # Append the product name and price to the list
        products.append({'name': name, 'price': price})


DETA_KEY = 'a0zywtxbhxo_osDe6U3TNRFKqhMvVRiWTVLW4B6G55kH'
deta = Deta(DETA_KEY)
db = deta.Base("ekogroszek")

today_1 = datetime.datetime.today()
today = today_1.strftime('%Y-%m-%d')

key = str(today)
insert_period(key,products)



##################################################################################################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from deta import Deta
import datetime

#załadowanie danych do bazy
def insert_period(key,products):
    return db.put({"key": key, "product":products})

def scrape_pgg_products_with_selenium(url):
    options = Options()
    #options.add_argument("--no-sandbox")
    #options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    products = []

    try:
        driver.get(url)
        time.sleep(10)  # Adjust this delay as necessary

        product_elements = driver.find_elements(By.CSS_SELECTOR, 'a.text-dark span.font-weight-bold')
        price_elements = driver.find_elements(By.CSS_SELECTOR, 'div.col-4.col-md-2.pt-3.text-center span.text-4.font-weight-bold')
        description_elements = driver.find_elements(By.CSS_SELECTOR, 'a.text-dark') # Assuming description is within this element

        for product_element, price_element, description_element in zip(product_elements, price_elements, description_elements):
            product_name = product_element.text.strip()
            product_price = price_element.text.strip()
            product_description = description_element.text.strip() # Extract the full text including the description
            products.append((product_name, product_price, product_description))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return products

url = "https://sklep.pgg.pl"
products = scrape_pgg_products_with_selenium(url)



DETA_KEY = 'a0zywtxbhxo_osDe6U3TNRFKqhMvVRiWTVLW4B6G55kH'
deta = Deta(DETA_KEY)
db = deta.Base("ekogroszek")

today_1 = datetime.datetime.today()
today = today_1.strftime('%Y-%m-%d')

key = str(today)+"pgg"
insert_period(key,products)

