from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from time import sleep
import requests
import re

ZILLOW_URL = ("https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.30389632177734%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D")

G_DOCS_URL = "https://docs.google.com/forms/d/1xLcU2LoucUgo0XOgtxpLudZtg0a6XdkNhOddZNipQnE"

headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Sec-Ch-Ua-Platform": "\"Windows\""
}

flat_links = []
flat_prices = []
flat_addresses = []


web_page = requests.get(url=ZILLOW_URL, headers=headers)
print(web_page)

soup = BeautifulSoup(web_page.text, "html.parser")

flat_articles = soup.find_all('article', attrs={"data-test": "property-card"})


for flat in flat_articles:
    # Getting links
    flat_link = flat.find_next("a", attrs={"data-test": "property-card-link"}).get("href")
    if flat_link[0] == "/":
        flat_link = "https://www.zillow.com" + flat_link
    flat_links.append(flat_link)
    
    # Getting prices
    flat_price = flat.find_next("span", attrs={"data-test": "property-card-price"}).get_text()
    flat_prices.append(flat_price)

    # Getting addresses
    flat_address = flat.find_next("address", attrs={"data-test": "property-card-addr"}).get_text()
    flat_addresses.append(flat_address)


for p in range(len(flat_prices)):
    parsed_price_digits = re.findall(r"\d+", flat_prices[p])
    num_price = "$" + parsed_price_digits[0] + "," + parsed_price_digits[1]
    flat_prices[p] = num_price


# Filling in the Google form
chrome_driver_path = "E:\Projects\chromedriver_win32\chromedriver"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


for i in range(len(flat_addresses)):
    driver.get(G_DOCS_URL)

    sleep(5)
    address = driver.find_element(By.XPATH, "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input")
    address.send_keys(flat_addresses[i])
    
    price = driver.find_element(By.XPATH, "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
    price.send_keys(flat_prices[i])
    
    link = driver.find_element(By.XPATH, "//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")
    link.send_keys(flat_links[i])

    send_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Надіслати')]")
    send_btn.click()


driver.quit()

