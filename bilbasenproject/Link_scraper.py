import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def initialize_driver():
    """Initializes and returns a headless Chrome WebDriver with minimal logging."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def parse_url_for_details(url):
    """Extracts brand, model, and variant from the URL."""
    parts = url.split('/')
    brand = parts[5]
    model = parts[6]
    variant = parts[7].rsplit('-', 2)[0]
    return brand, model, variant

def fetch_car_details(driver, url, seller_type):
    """Fetches car details from the URL and returns a dictionary of these details."""
    car_details = {'Link': url, 'Seller Type': seller_type}
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'main')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    brand, model, variant = parse_url_for_details(url)
    car_details.update({
        'Brand': brand.capitalize(),
        'Model': model.upper(),
        'Variant': variant.replace('-', ' ').capitalize()
    })

    car_price = soup.select_one('#root > div.nmp-ads-layout__page > div.nmp-ads-layout__content > div.bas-Wrapper-wrapper > article > main > div.bas-MuiVipPageComponent-headerAndPrice > div.bas-MuiCarPriceComponent-container > div > div > span')
    car_details['Price'] = car_price.get_text(strip=True) if car_price else "Price not found"

    main_section = soup.find('main')
    for tbody in main_section.find_all('tbody'):
        for row in tbody.find_all('tr'):
            key = row.find('th').get_text(strip=True)
            value = row.find('td').get_text(strip=True)
            car_details[key] = value
            if key == "Døre":
                break
        if key == "Døre":
            break

    return car_details

def save_to_csv(car_details, filename='scraped_cars/all_data.csv'):
    """Saves the car details to a CSV file."""
    new_df = pd.DataFrame([car_details])
    try:
        df = pd.read_csv(filename)
        updated_df = pd.concat([df, new_df], ignore_index=True)
    except FileNotFoundError:
        updated_df = new_df
    updated_df.to_csv(filename, index=False, encoding='utf-8-sig')

def main(number_of_rows=None):
    """The main function to initialize the driver, scrape data, and handle exceptions."""
    driver = initialize_driver()
    try:
        file_path = 'scraped_links/merged_car_links.csv'
        df = pd.read_csv(file_path)
        if number_of_rows is not None:
            df = df.iloc[:number_of_rows]
        
        print(f"Processing {len(df)} rows")
        for index, row in df.iterrows():
            url = row['Car Links']
            seller_type = row['dealer/private']
            print(f"Processing {url}")
            car_details = fetch_car_details(driver, url, seller_type)
            save_to_csv(car_details)
            print(f"Data saved for {url}")
            time.sleep(1)
    finally:
        driver.quit()
        print("Scraping session completed.")

if __name__ == "__main__":
    main()  # Specify the number of rows. Empty = all
