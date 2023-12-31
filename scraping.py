import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_DRIVER_PATH = "/snap/bin/geckodriver"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0",
    "Accept-Language": "en-US, en;q=0.5",
}


def get_product_details(url):
    options = Options()
    options.add_argument("-headless")

    service = Service(GECKO_DRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)
    except Exception as e:
        print(f"Error accessing URL: {url}")
        print(f"Error message: {str(e)}")
        driver.quit()
        return None

    wait = WebDriverWait(driver, 10)
    product_name_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-size-large"))
    )

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    product_name = soup.select_one("span.a-size-large").text.strip()

    product_price = "Not available"
    price_element = soup.select_one("span.a-price-whole")
    if price_element:
        product_price = price_element.text.strip()

    rating = "Not available"
    rating_element = soup.select_one("span.a-icon-alt")
    if rating_element:
        rating = rating_element.text.strip().split(" ")[0]

    num_reviews = "Not available"
    reviews_element = soup.select_one("span#acrCustomerReviewText")
    if reviews_element:
        num_reviews = reviews_element.text.strip()

    description = "Not available"
    description_element = soup.select_one("div#productDescription")
    if description_element:
        description = description_element.text.strip()

    asin = "Not available"
    asin_element = soup.select_one("span.a-text-bold:-soup-contains('ASIN') + span")
    if asin_element:
        asin = asin_element.text.strip()
    else:
        asin_element = soup.select_one("th:-soup-contains('ASIN') + td")
        if asin_element:
            asin = asin_element.text.strip()

    product_description = "Not available"
    product_description_element = soup.select_one("div#productDescription")
    if product_description_element:
        product_description = product_description_element.text.strip()

    manufacturer = "Not available"
    manufacturer_element = soup.select_one(
        "span.a-text-bold:-soup-contains('Manufacturer') + span"
    )
    if manufacturer_element:
        manufacturer = manufacturer_element.text.strip()
    else:
        manufacturer_element = soup.select_one("th:-soup-contains('Manufacturer') + td")
        if manufacturer_element:
            manufacturer = manufacturer_element.text.strip()

    return [
        url,
        product_name,
        product_price,
        rating,
        num_reviews,
        description,
        asin,
        product_description,
        manufacturer,
    ]


def scrape_products():
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
    total_pages = 20
    total_products = 200

    with open("products.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "URL",
                "Product Name",
                "Product Price",
                "Rating",
                "Number of Reviews",
                "Description",
                "ASIN",
                "Product Description",
                "Manufacturer",
            ]
        )

        product_count = 0
        scraped_urls = []

        options = Options()
        options.add_argument("-headless")

        for page in range(1, total_pages + 1):
            url = base_url + str(page)
            service = Service(GECKO_DRIVER_PATH)
            driver = webdriver.Firefox(service=service, options=options)
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            product_links = soup.select("a.a-link-normal.a-text-normal")
            for link in product_links:
                if product_count >= total_products:
                    break

                product_url = "https://www.amazon.in" + link["href"]
                if product_url in scraped_urls:
                    continue

                try:
                    product_details = get_product_details(product_url)
                    writer.writerow(product_details)
                    product_count += 1
                    scraped_urls.append(product_url)
                except Exception as e:
                    print(f"Error scraping product at URL: {product_url}")
                    print(f"Error message: {str(e)}")

            driver.quit()

            print(f"Scraped products from page {page}.")

            if product_count >= total_products:
                break


scrape_products()
