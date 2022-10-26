from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from helpers import get_clean_address

def get_page_source(url):
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    sleep(0.5)
    return driver.page_source

def get_offices_info(city):
    url = f"https://kurs.kz/index.php?mode={city}"
    html = get_page_source(url)
    soup = BeautifulSoup(html, "html.parser")
    
    offices = []
    for office_elem in soup.select(".punkt-open"):
        office = {}

        office["name"] = office_elem.select_one(".tab").get_text()
        office["address"] = get_clean_address(office_elem.select_one("address").get_text())
        
        currencies_elems = office_elem.select(".currency")

        for i, curr in enumerate(["USD", "EUR", "RUB"]):
            spans = currencies_elems[i].find_all("span")
            purchase_text = spans[0].get_text()
            sale_text = spans[2].get_text()
            if purchase_text == "-" or sale_text == "-":
                break
            office[curr] = (float(purchase_text), float(sale_text))
        else:
            offices.append(office)
            continue
    
    return offices


def get_purchase_amount(office_info, sale_currency, purchase_currency, sale_amount):
    if sale_currency == "KZT":
        currency_rate = office_info[purchase_currency][1]
        return sale_amount / currency_rate
    elif purchase_currency == "KZT":
        currency_rate = office_info[sale_currency][0]
        return sale_amount * currency_rate
    else:
        currency_rate1 = office_info[sale_currency][0]
        kz_amount = sale_amount * currency_rate1

        currency_rate2 = office_info[purchase_currency][1]
        return kz_amount / currency_rate2
    

def find_best_offices(offices, sale_currency, purchase_currency, sale_amount):
    max_amount = 0
    best_offices = []
    for office_info in offices:
        purchase_amount = get_purchase_amount(office_info, sale_currency, purchase_currency, sale_amount)
        if purchase_amount > max_amount:
            best_offices = [office_info]
            max_amount = purchase_amount
        elif purchase_amount == max_amount:
            best_offices.append(office_info)
    
    return best_offices, max_amount



if __name__ == "__main__":
    offices = get_offices_info("astana")