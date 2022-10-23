from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from helpers import get_clean_address

def get_url_source(url):
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    sleep(0.5)
    return driver.page_source

def get_offices_info(city):

    url = f"https://kurs.kz/index.php?mode={city}"
    html = get_url_source(url)
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
    

if __name__ == "__main__":
    get_offices_info("astana")