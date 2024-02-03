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



