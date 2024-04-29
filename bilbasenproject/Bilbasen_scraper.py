# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

# Selenium WebDriver Chrome options
options = webdriver.ChromeOptions()
# This option allows the Chrome window to stay open even after the script finishes executing.
options.add_experimental_option("detach", True)

# Start a new Chrome WebDriver session with the specified options.
driver = webdriver.Chrome(options=options)
# Define the URL of the page to scrape
url = 'https://www.bilbasen.dk/brugt/bil?fuel=3&pricetype=Retail'

# Open the URL in the Chrome browser
driver.get(url)

# Create lists to store data for each car attribute.
lst_model = []
lst_prices = []
lst_registration = []
lst_mileage = []
lst_range = []

# Define the number of pages to scrape
num_pages = 3

# Flag to handle one-time actions like iframe switching
first_iteration = True

# Loop through the specified number of pages
for _ in range(num_pages):
    try:
        if first_iteration:
            # Wait for the iframe containing the cookie consent form to load, and switch to it
            wait = WebDriverWait(driver, 10)
            iframe = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "sp_message_iframe_893480")))

            # Wait for the cookie consent button to become clickable, and click it
            consent_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Tillad alle']")))
            consent_button.click()

            # Return to the main content of the webpage after handling the cookie consent
            driver.switch_to.default_content()
            first_iteration = False  # Set to False to avoid repeating iframe handling

        # Sleep to ensure all elements load, especially after navigation
        sleep(5)

        # Locate all car row elements on the page based on their common structure
        car_rows = driver.find_elements(By.XPATH, '//div[@class="Listing_listingWrap__41B9X"]')

        # Loop over each car row and extract details
        for WebElement in car_rows:
            elementHTML = WebElement.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML, 'html.parser')

            # Extract the model of the car
            temp_model = elementSoup.find("div", {"class": "Listing_makeModel__7yqgs"})
            model = temp_model.find("h3", {"class": "font-bold"})
            lst_model.append(model.text.strip())

            # Extract the price of the car
            temp_price = elementSoup.find("div", {"class": "Listing_price__6B3kE"})
            price = temp_price.find("h3", {"class": "font-bold color-primary"})
            lst_prices.append(price.text.strip())

            # Extract registration, mileage, and range from details section
            temp_details = elementSoup.find("div", {"class": "Listing_details__bkAK3"})
            li_elements = temp_details.find_all("li")
            registration = li_elements[0].text.strip() if len(li_elements) > 0 else "N/A"
            mileage = li_elements[1].text.strip() if len(li_elements) > 1 else "N/A"
            range = li_elements[2].text.strip() if len(li_elements) > 2 else "N/A"

            # Append the extracted details to their respective lists
            lst_registration.append(registration)
            lst_mileage.append(mileage)
            lst_range.append(range)

        # Navigate to the next page by clicking the "Next" button
        next_button = driver.find_element(By.XPATH, "//a[@data-e2e='pagination-next']")
        driver.execute_script("arguments[0].click();", next_button)

    # Handle common exceptions that might occur during scraping
    except NoSuchElementException as e:
        print(f"An element was not found: {e}")
        break
    except TimeoutException:
        print("Timed out waiting for page to load.")
        break
    except ElementClickInterceptedException:
        print("Element was not clickable.")
        break

# Print the collected data (optional)
# print(lst_registration, lst_mileage, lst_range, lst_prices, lst_model)

# Create a DataFrame from the collected data
data = {
    'Model': lst_model,
    'Price': lst_prices,
    'Registration': lst_registration,
    'Mileage': lst_mileage,
    'Range': lst_range
}
df = pd.DataFrame(data)
print(df)

# Optionally, save the DataFrame to a CSV file
# df.to_csv('bilbasen_data.csv', index=False)


