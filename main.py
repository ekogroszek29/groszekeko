from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from deta import Deta
import datetime
from collections import defaultdict
# Słownik kategorii
produkty_spozywcze = [
    # Owoce
    "jabłko", "banan", "pomarańcza", "kiwi", "gruszka", "mango", "winogrona", 
    "truskawki", "maliny", "jeżyny", "czereśnie", "awokado", "ananas", 
    "grejpfrut", "limonka", "cytryna", "mandarynka", "kaki", "brzoskwinia", 
    "nektarynka", "papaja", "liczi", "daktyle", "figi", "karambola", 
    "kokos", "granat", "durian", "rambutan", "żurawina", "borówki", 
    "agrest", "porzeczki", "aronia", "jagody", "kiwano",

    # Warzywa
    "marchew", "pomidor", "ogórek", "papryka", "brokuły", "kalafior", 
    "szpinak", "sałata", "rukola", "kukurydza", "groch", "fasola", 
    "soczewica", "cebula", "czosnek", "por", "pietruszka", "seler", 
    "kalarepa", "burak", "rzodkiewka", "kapusta", "brukselka", "bakłażan", 
    "dynia", "zucchini", "szparagi", "karczochy", "bataty", "ziemniaki",
    "ogórki kiszone","papryczki",

    # Zboża i produkty zbożowe
    "ryż", "makaron", "kasza", "quinoa", "chleb", "bułka", "rogal", 
    "bagietka", "croissant", "chleb pełnoziarnisty", "pumpernikiel", 
    "tortilla", "pita",

    # Wypieki i ciasta
    "ciasto", "ciastka", "tort", "babka", "sernik", "szarlotka", "rogaliki", 
    "pączki", "drożdżówki",

    # Przekąski i słodycze
    "chipsy", "paluszki", "chrupki", "popcorn", "orzeszki", "migdały", 
    "nasiona słonecznika", "pestki dyni", "orzechy włoskie", "orzechy laskowe", 
    "orzechy brazylijskie", "orzechy pekan", "orzechy macadamia", "pistacje", 
    "kaszew", "czekolada", "cukierki", "żelki", "Prażynki","batony", "marmolada",
    "baton","płatki","krakersy","gofry","krówka"

    # Nabiał
    "mleko", "jogurt", "ser żółty", "ser biały", "twaróg", "kefir", 
    "śmietana","śmietanka", "maślanka", "masło", "margaryna", "jaja",

    # Słodziki i dodatki
    "miód", "dżem", "konfitura", "nutella", "ketchup", "musztarda", "majonez", 
    "sos sojowy", "ocet", "oliwa", "olej",

    # Przyprawy i zioła
    "cukier", "sól", "pieprz", "papryka", "kurkuma", "bazylia", "oregano", 
    "tymianek", "rozmaryn", "szczypiorek", "kminek", "koper", "kolendra", 
    "kardamon", "goździki", "cynamon", "wanilia", "imbir", "gałka muszkatołowa",
    "chili",

    # Mięso i produkty mięsne
    "kurczak", "wołowina", "wieprzowina", "baranina", "indyk", "kaczka", 
    "gęś", "królik", "dziczyzna", "salami", "szynka", "kiełbasa", "boczek",

    # Ryby i owoce morza
    "ryby", "łosoś", "pstrąg", "makrela", "tuńczyk", "sardynki", 
    "krewetki", "homar", "krab", "małże", "ostrygi", "kawior",

    # Napoje
    "woda", "sok", "napój gazowany", "cola", "lemoniada", "herbata", 
    "kawa", "kakao", "piwo", "wino", "whisky", "rum", "wódka", 
    "gin", "tequila", "likier", "szampan", "prosecco", "cydr",

    # Inne
    "tofu", "tempeh", "seitan", "miso", "kimchi", "sushi", "pierogi", 
    "pizza", "hamburger", "hot dog", "kebab", "falafel", "hummus",
    "napój owsiany","napój migdałowy",'błyskawiczna'

    # Dodatkowe sosy i przyprawy
    "pesto", "sos pomidorowy", "sos czosnkowy", "sos barbecue", "sos teriyaki", 
    "tabasco", "salsa", "guacamole", "tahini", "harissa", "chutney", 
    "wasabi", "soja", "hoisin", "sriracha", "aioli","drożdze",

    # Rośliny strączkowe
    "ciecierzyca", "fasolka szparagowa", "bób", "natto", "edamame","groszek",

    # Ziarna i nasiona
    "siemię lniane", "chia", "amarantus", "proso", "kasza gryczana", 
    "kasza jaglana", "kasza bulgur", "kasza kuskus", "owsianka", "muesli","owsiane",

    # Oleje i tłuszcze
    "olej rzepakowy", "olej lniany", "olej słonecznikowy", "olej sezamowy", 
    "olej arachidowy", "olej z orzechów włoskich", "olej kokosowy", 
    "smalec", "łój",

    # Produkty mleczne i zamienniki
    "ser camembert", "ser brie", "ser gouda", "ser edamski", "ser roquefort", 
    "ser feta", "ser mozzarella", "ser parmezan", "ser gorgonzola", 
    "mleko kokosowe", "mleko migdałowe", "mleko sojowe", "mleko owsiane", 
    "mleko ryżowe", "jogurt grecki", "jogurt naturalny",

    # Produkty mączne i pieczywo
    "mąka pszenna", "mąka żytnia", "mąka owsiana", "mąka kukurydziana", 
    "mąka orkiszowa", "mąka gryczana", "mąka kokosowa", "mąka migdałowa", 
    "mąka", "tost",
    "makaron ryżowy", "makaron jajeczny", "makaron soba", "makaron udon", 
    "spaghetti", "penne", "fusilli", "farfalle", "lasagne", "ravioli", 
    "gnocchi", "pizza", "focaccia", "pretzel", "bagel",

    # Przetwory mięsne i rybne
    "pasztet", "pate", "ryba wędzona", "ryba solona", "ryba marynowana", 
    "tuńczyk w puszce", "sardynki w puszce", "śledź w oleju", 

    # Słodycze i desery
    "lody", "sorbet", "galaretka", "tiramisu", "panna cotta", "creme brulee", 
    "fondue czekoladowe","czekolad", "macarons", "eclair", "profiterole", "trufle", 
    "beza", "pavlova", "kremówka", "kanapka lodowa", "wafle", "bezy","erbatniki",

    # Napoje alkoholowe i bezalkoholowe
    "sake", "mead", "martini", "mojito", "margarita", "piña colada", 
    "sangria", "absynt", "portwine", "vermouth", "brandy", "cognac", 
    "amaretto", "baijiu", "sok pomarańczowy", "sok jabłkowy", "sok winogronowy", 
    "sok żurawinowy", "sok warzywny", "smoothie", "frappe", "latte", "cappuccino", 
    "espresso", "macchiato", "americano", "flat white", "mrożona kawa", 

    # Przyprawy, zioła i dodatki
    "laur", "majeranek", "mięta", "melisa", "szałwia", "lebiodka", 
    "ziele angielskie", "anyż", "fenkuł", "kurkuma", "szafran", "sumak", 
    "asafetida", "fenugreek", "mustard seeds", "zatar", "curry","proszek do pieczenia", "pudding",
    "kinder"
]


kategorie_spozywcze = {
    "Ryż": ["ryż"],
    "Mąka": ["mąka pszenna", "mąka żytnia", "mąka owsiana", "mąka kukurydziana", "mąka orkiszowa", "mąka gryczana", "mąka kokosowa", "mąka migdałowa", "mąka"],
    "Pieczywo": ["chleb", "bułka", "rogal", "bagietka", "croissant", "chleb pełnoziarnisty", "pumpernikiel", "tortilla", "pita", "tost"],
    "Makarony": ["makaron", "makaron ryżowy", "makaron jajeczny", "makaron soba", "makaron udon", "spaghetti", "penne", "fusilli", "farfalle", "lasagne", "ravioli", "gnocchi"],
    "Mięso": ["kurczak", "wołowina", "wieprzowina", "baranina", "indyk", "kaczka", "gęś", "królik", "dziczyzna", "salami", "szynka", "kiełbasa", "boczek"],
    "Ryby i owoce morza": ["ryby", "łosoś", "pstrąg", "makrela", "tuńczyk", "sardynki", "krewetki", "homar", "krab", "małże", "ostrygi", "kawior"],
    "Mleko, sery i jaja": ["mleko", "jogurt", "ser żółty", "ser biały", "twaróg", "kefir", "śmietana", "śmietanka", "maślanka", "masło", "margaryna", "jaja"],
    "Oleje i tłuszcze": ["olej rzepakowy", "olej lniany", "olej słonecznikowy", "olej sezamowy", "olej arachidowy", "olej z orzechów włoskich", "olej kokosowy", "smalec", "łój"],
    "Owoce": ["jabłko", "banan", "pomarańcza", "kiwi", "gruszka", "mango", "winogrona", "truskawki", "maliny", "jeżyny", "czereśnie", "awokado", "ananas", "grejpfrut", "limonka", "cytryna", "mandarynka", "kaki", "brzoskwinia", "nektarynka", "papaja", "liczi", "daktyle", "figi", "karambola", "kokos", "granat", "durian", "rambutan", "żurawina", "borówki", "agrest", "porzeczki", "aronia", "jagody", "kiwano"],
    "Warzywa": ["marchew", "pomidor", "ogórek", "papryka", "brokuły", "kalafior", "szpinak", "sałata", "rukola", "kukurydza", "groch", "fasola", "soczewica", "cebula", "czosnek", "por", "pietruszka", "seler", "kalarepa", "burak", "rzodkiewka", "kapusta", "brukselka", "bakłażan", "dynia", "zucchini", "szparagi", "karczochy", "bataty", "ziemniaki", "ogórki kiszone", "papryczki"],
    "Cukier": ["cukier"],
    "Napoje bezalkoholowe": ["woda", "sok", "napój gazowany", "cola", "lemoniada", "herbata", "kawa", "kakao"],
    "Napoje alkoholowe i wyroby tytoniowe": ["piwo", "wino", "whisky", "rum", "wódka", "gin", "tequila", "likier", "szampan", "prosecco", "cydr", "sake", "mead", "martini", "mojito", "margarita", "piña colada", "sangria", "absynt", "portwine", "vermouth", "brandy", "cognac", "amaretto", "baijiu"],
    "Pozostałe": ["tofu", "tempeh", "seitan", "miso", "kimchi", "sushi", "pierogi", "pizza", "hamburger", "hot dog", "kebab", "falafel", "hummus", "napój owsiany", "napój migdałowy", "błyskawiczna", "pesto", "sos pomidorowy", "sos czosnkowy", "sos barbecue", "sos teriyaki", "tabasco", "salsa", "guacamole", "tahini", "harissa", "chutney", "wasabi", "soja", "hoisin", "sriracha", "aioli", "drożdze", "ciecierzyca", "fasolka szparagowa", "bób", "natto", "edamame", "groszek", "siemię lniane", "chia", "amarantus", "proso", "kasza gryczana", "kasza jaglana", "kasza bulgur", "kasza kuskus", "owsianka", "muesli", "owsiane", "pasztet", "pate", "ryba wędzona", "ryba solona", "ryba marynowana", "tuńczyk w puszce", "sardynki w puszce", "śledź w oleju", "lody", "sorbet", "galaretka", "tiramisu", "panna cotta", "creme brulee", "fondue czekoladowe", "czekolad", "macarons", "eclair", "profiterole", "trufle", "beza", "pavlova", "kremówka", "kanapka lodowa", "wafle", "bezy", "erbatniki", "laur", "majeranek", "mięta", "melisa", "szałwia", "lebiodka", "ziele angielskie", "anyż", "fenkuł", "kurkuma", "szafran", "sumak", "asafetida", "fenugreek", "mustard seeds", "zatar", "curry", "proszek do pieczenia", "pudding", "kinder"]
}

def assign_product_name(name, product_names):
    for product in product_names:
        if product in name.lower():
            return product
    return 'Inny'

def find_category(word, categories_dict):
    for category, words in categories_dict.items():
        if word in words:
            return category
    return "Nieznana kategoria"

def scrape_page(url):
    # Opcje dla Selenium, aby symulować normalną przeglądarkę
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument('headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

    # Ustawienie usługi WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    products = []
    kategoria_lista = []
    products2 = []

    try:
        # Otwarcie URL
        driver.get(url)
        
        # Czekanie na załadowanie produktów
        time.sleep(3)  # Możesz dostosować opóźnienie w razie potrzeby

        # Ekstrakcja danych
        product_name_elements = driver.find_elements(By.CSS_SELECTOR, 'div.MuiBox-root a h3.MuiButtonBase-root')
        product_price_elements = driver.find_elements(By.CSS_SELECTOR, 'div.jss331')

        for name_el, price_el in zip(product_name_elements, product_price_elements):
            name = name_el.text.strip()
            price_whole = price_el.find_element(By.CSS_SELECTOR, 'div.MuiTypography-h1').text.strip()
            price_fraction = price_el.find_element(By.CSS_SELECTOR, 'div.MuiTypography-h3').text.strip()
            price = f"{price_whole},{price_fraction}"
            today_1 = datetime.datetime.today()
            today = today_1.strftime('%Y-%m-%d')
            kategoria = assign_product_name(name, produkty_spozywcze)
            kategoria_2 =find_category(kategoria, kategorie_spozywcze)
            kategoria_3 = str(kategoria)+ "|" + str(kategoria_2)
            products.append((name, price, today,kategoria_3))

    finally:
        # Zamknięcie przeglądarki
        driver.quit()

    return products


# URL bazowy
base_url = "https://www.carrefour.pl/artykuly-spozywcze"
num_pages = 85
all_products = []

for page in range(1, num_pages + 1):
    # Konstrukcja URL dla bieżącej strony
    url = f"{base_url}?page={page}"
    
    # Scrapowanie bieżącej strony
    products = scrape_page(url)
    all_products.extend(products)


    # Odczekanie 1 minuty przed przetworzeniem kolejnej strony
    if page < num_pages:
        time.sleep(1)



#załadowanie danych do bazy
def insert_period(key,products):
    return db.put({"key": key, "product":products})


DETA_KEY = 'a0ofp2m7nqr_ipmzDm3KGiVGNcSwyo1XeGMJcuXgjUnR'
deta = Deta(DETA_KEY)
db = deta.Base("ceny")

today_1 = datetime.datetime.today()
today = today_1.strftime('%Y-%m-%d')


half_length = len(all_products) // 2
first_half = all_products[:half_length]
secound_half = all_products[half_length:]


key = str(today)+"_carrefour1"
insert_period(key,first_half)

deta = Deta(DETA_KEY)
db = deta.Base("ceny")


key = str(today)+"_carrefour2"
insert_period(key,secound_half)





agregacja = defaultdict(lambda: defaultdict(list))

# Agregowanie cen w odpowiednich kategoriach
for produkt, cena, data, pierwsza_kategoria, szersza_kategoria in all_products:
    cena_float = float(cena.replace(',', '.'))
    agregacja[data][szersza_kategoria].append(cena_float)

# Obliczanie średniej ceny dla każdej kombinacji daty i szerszej kategorii
wyniki_agregacji = []
for data, kategorie in agregacja.items():
    for kategoria, ceny in kategorie.items():
        srednia_cena = sum(ceny) / len(ceny)
        wyniki_agregacji.append((data, kategoria, round(srednia_cena, 2)))





DETA_KEY = 'a0wxvo5biy4_41tn1eFLGHqGQ7zb4zLruDxrvjCWZJJg'
deta = Deta(DETA_KEY)
db = deta.Base("ceny")

today_1 = datetime.datetime.today()
today = today_1.strftime('%Y-%m-%d')

key = str(today)+"_carrefour"
insert_period(key,wyniki_agregacji)























