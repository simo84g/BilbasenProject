from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def fetch_car_links_with_selenium(base_url, start_page, end_page):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    all_links = []

    try:
        for page in range(start_page, end_page + 1):
            url = f"{base_url}&page={page}"
            driver.get(url)
            
            # Handle cookie consent on the first page
            if page == start_page:
                try:
                    cookie_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.only-necessary-button"))
                    )
                    driver.execute_script("arguments[0].click();", cookie_button)
                    print("Cookie consent handled successfully.")
                except TimeoutException:
                    print("Failed to locate or click the cookie consent button.")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Listing_link__6Z504"))
            )
            elements = driver.find_elements(By.CLASS_NAME, "Listing_link__6Z504")
            page_links = [element.get_attribute('href') for element in elements if element.get_attribute('href')]
            all_links.extend(page_links)
            print(f"Page {page}: Collected {len(page_links)} links.")

            # Polite delay between page requests
            time.sleep(5)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return all_links

# Example usage
base_url = "https://www.bilbasen.dk/brugt/bil?fuel=3&pricetype=Retail"
links = fetch_car_links_with_selenium(base_url, 1, 314)

# Create and print DataFrame
df_links = pd.DataFrame(links, columns=['Car Links'])
print(df_links)
df_links.to_csv('all_electric_car_links.csv', index=False)
