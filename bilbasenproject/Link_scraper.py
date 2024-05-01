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
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--window-size=1920x1080")  # Set window size for consistency
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress logging
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def parse_url_for_details(url):
    parts = url.split('/')
    brand = parts[5]
    model = parts[6]
    variant = parts[7].rsplit('-', 2)[0]  # Assuming the format is always like 'variant-5d-id'
    return brand, model, variant

def fetch_car_details(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'main')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        brand, model, variant = parse_url_for_details(url)
        car_details = {
            'Link': url,
            'Brand': brand.capitalize(),
            'Model': model.upper(),
            'Variant': variant.replace('-', ' ').capitalize()
        }

        car_price = soup.select_one('#root > div.nmp-ads-layout__page > div.nmp-ads-layout__content > div.bas-Wrapper-wrapper > article > main > div.bas-MuiVipPageComponent-headerAndPrice > div.bas-MuiCarPriceComponent-container > div > div > span')
        car_details['Price'] = car_price.get_text(strip=True) if car_price else "Price not found"

        main_section = soup.find('main')
        for tbody in main_section.find_all('tbody', class_='bas-MuiTableBody-root'):
            for row in tbody.find_all('tr', class_='bas-MuiTableRow-root'):
                key = row.find('th', class_='bas-MuiTableCell-root').get_text(strip=True)
                value = row.find('td', class_='bas-MuiTableCell-root').get_text(strip=True)
                car_details[key] = value
                if key == "Døre":
                    break
            else:
                continue
            break
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        car_details = {'Link': url, 'Error': 'Failed to load data'}
    return car_details

def save_to_csv(car_details, filename='C:\\Cand.merc.BI\\2. Semester\\Data Science Project\\Project\\BilbasenProject\\scraped_car_data.csv'):
    new_df = pd.DataFrame([car_details])
    try:
        df = pd.read_csv(filename)
        updated_df = pd.concat([df, new_df], ignore_index=True)
    except FileNotFoundError:
        updated_df = new_df
    updated_df.to_csv(filename, index=False, encoding='utf-8-sig')

def main():
    driver = initialize_driver()
    try:
        file_path = 'C:\\Cand.merc.BI\\2. Semester\\Data Science Project\\Project\\BilbasenProject\\all_electric_car_links - Copy.csv'
        df = pd.read_csv(file_path)
        urls = df['Car Links'].iloc[5611:].tolist()  # Start from where you stopped last

        for url in urls:
            car_details = fetch_car_details(driver, url)
            save_to_csv(car_details)
            print(f"Data saved for {url}")
            time.sleep(2)  # Moderate the request rate to avoid being blocked

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
