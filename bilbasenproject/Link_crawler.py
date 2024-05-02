import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import random
import time

from selenium.webdriver.chrome.options import Options

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Spoof user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def fetch_car_links_with_selenium(base_url, start_page, max_pages):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    all_links = set()

    try:
        for current_page in range(start_page, max_pages + 1):
            url = f"{base_url}&page={current_page}"
            driver.get(url)
            
            if current_page == start_page:  # Handle cookie consent on the first page
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.only-necessary-button"))
                    ).click()
                    print("Cookie consent handled successfully.")
                except TimeoutException:
                    print("Failed to locate or click the cookie consent button.")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Listing_link__6Z504"))
            )
            elements = driver.find_elements(By.CLASS_NAME, "Listing_link__6Z504")
            page_links = {element.get_attribute('href') for element in elements if element.get_attribute('href')}
            new_links_count = len(page_links - all_links)
            all_links.update(page_links)
            print(f"Page {current_page}: Collected {new_links_count} new links, Total unique links: {len(all_links)}.")

            if new_links_count == 0:  # If no new links were added
                print(f"No new links on page {current_page}. Stopping...")
                break

            # Randomize wait time to mimic human behavior more closely
            random_sleep_time = random.randint(10, 60)  # Wait between 10 to 60 seconds
            time.sleep(random_sleep_time)
            print(f"Waited for {random_sleep_time} seconds.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return list(all_links)

# Example usage
base_url = "https://www.bilbasen.dk/brugt/bil?fuel=3&pricetype=Retail"
links = fetch_car_links_with_selenium(base_url, 101, 317)  # Adjusted for pages 101 to 200

# Create and print DataFrame
df_links = pd.DataFrame(links, columns=['Car Links'])
print(df_links)
df_links.to_csv('all_electric_car_links_101to317.csv', index=False)
