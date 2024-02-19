import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


chrome_options = Options()

chrome_driver_path = './chromedriver.exe'

driver = webdriver.Firefox()


base_url = "https://app.apollo.io/#/people?finderViewId=5b6dfc5a73f47568b2e5f11c&contactLabelIds[]=65c48b8b02f3ae00011e2c57&prospectedByCurrentTeam[]=yes&page="
csv_file_name = 'RealEstate.csv'


current_page = 1

time.sleep(2)

def find_email_address(page_source):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, page_source)

def filter_emails(emails, excluded_domain):
    filtered = [email for email in emails if not email.endswith(excluded_domain)]
    return filtered[:2]

def split_name(name):
    parts = name.split()
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return first_name, last_name

while True:
    try:
        driver.get(f"{base_url}{current_page}")
        time.sleep(20)  # Wait for the page to load
        loaded_section_selector = "[data-cy-loaded='true']"
        loaded_section = driver.find_element(By.CSS_SELECTOR, loaded_section_selector)

        tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
        if not tbodies:
            break

        for tbody in tbodies:
            first_anchor_text = tbody.find_element(By.TAG_NAME, 'a').text
            first_name, last_name = split_name(first_anchor_text)

            linkedin_url = ''
            for link in tbody.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href')
                if 'linkedin.com' in href:
                    linkedin_url = href
                    break

            job_title_element = tbody.find_element(By.CLASS_NAME, 'zp_Y6y8d')
            job_title = job_title_element.text if job_title_element else ''

            company_name = ''
            for link in tbody.find_elements(By.TAG_NAME, 'a'):
                if 'accounts' in link.get_attribute('href'):
                    company_name = link.text
                    break

            phone_number = tbody.find_elements(By.TAG_NAME, 'a')[-1].text

            button_classes = ["zp-button", "zp_zUY3r", "zp_hLUWg", "zp_n9QPr", "zp_B5hnZ", "zp_MCSwB", "zp_IYteB"]
            
            try:
                button = tbody.find_element(By.CSS_SELECTOR, "." + ".".join(button_classes))
                if button:
                    button.click()
                    email_addresses = find_email_address(driver.page_source)
                    filtered_emails = filter_emails(email_addresses, 'sentry.io')
                    with open(csv_file_name, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        print(f"{first_name} has been scraped")
                        if len(filtered_emails) == 1:
                            writer.writerow([first_name, last_name, job_title, company_name, filtered_emails[0], '', linkedin_url, phone_number])
                        elif len(filtered_emails) == 2:
                            writer.writerow([first_name, last_name, job_title, company_name, filtered_emails[0], filtered_emails[1], linkedin_url, phone_number])
                    button.click()
                    tbody_height = driver.execute_script("return arguments[0].offsetHeight;", tbody)
                    driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", loaded_section, tbody_height)
            except NoSuchElementException:
                continue





        current_page += 1


        time.sleep(5)   

    except Exception as e:
        error_message = str(e)
        if "element click intercepted" in error_message:
            print("Your leads are ready")
            break
        else:
            print(f"An error occurred: {error_message}")
            break

driver.quit()