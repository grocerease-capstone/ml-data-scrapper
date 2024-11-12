import csv
import os

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def scrapper(key: str, categories: str, max_page: int, label: str):
    template_url: str = "https://www.klikindomaret.com/search/?key={key}&categories={categories}&productbrandid=&sortcol=&pagesize=54&page={page}&startprice=&endprice=&attributes=&ShowItem="

    products = []

    for page_index in range(1, max_page + 1):
        ua = UserAgent()
        options = Options()
        options.add_argument("-headless")
        options.add_argument(f"user-agent={ua.random}")
        driver: WebDriver = webdriver.Chrome(options=options)

        url: str = template_url.format(
            key=key,
            categories=categories,
            page=page_index,
        )
        print(f"percobaan ke-{page_index}: {url}")

        try:
            driver.get(url)

            try:
                wait = WebDriverWait(
                    driver=driver,
                    timeout=5,
                )
                wait.until(expected_conditions.presence_of_element_located((By.ID, 'site-content')))
            except:
                raise LookupError("tidak ada element dengan id site-content")

            content = driver.page_source
            soup = BeautifulSoup(content, features='html.parser')

            product_collection = soup.find('div', class_='product-collection')

            for item in product_collection.find_all('div', class_='item'):
                each_item_element = item.find('div', class_='each-item')

                wrp_media_element = each_item_element.find('div', class_='wrp-media')
                try:
                    image_url = wrp_media_element.find('img')['data-src']
                except:
                    image_url = ""

                wrp_content_element = each_item_element.find('div', class_='wrp-content')

                title = wrp_content_element.find('div', class_='title').text

                wrp_price_element = wrp_content_element.find('div', class_='wrp-price')
                price_element = wrp_price_element.find('div', class_='price')
                normal_price = price_element.find('span', class_='normal price-value').text

                products.append({
                    'title': title.strip(),
                    'normal_price': normal_price.strip(),
                    'label': label,
                    'image_url': image_url,
                })

        except Exception as e:
            print("terjadi error: ", e)

        driver.quit()

    return products


def save_to_csv(data, filename):
    folder_name = 'data'

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    filepath = os.path.join(folder_name, f"{filename}.csv")

    with open(filepath, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"berhasil menyimpan ke file {filepath}")


if __name__ == '__main__':
    categories = [
        {
            'key': 'Makanan',
            'categories': 'Makanan',
            'max_page': 18,
            'label': 'makanan',
        },
    ]

    for category in categories:
        data = scrapper(
            key=category['key'],
            categories=category['categories'],
            label=category['label'],
            max_page=category['max_page'],
        )

        save_to_csv(data, filename=category['label'])
