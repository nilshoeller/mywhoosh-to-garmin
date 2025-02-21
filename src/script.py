import os
import time
import requests
from garminconnect import Garmin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from garth.exc import GarthHTTPError


MYWHOOSH_EMAIL = os.getenv("MYWHOOSH_EMAIL")
MYWHOOSH_PASSWORD = os.getenv("MYWHOOSH_PASSWORD")
GARMIN_USERNAME = os.getenv("GARMIN_USERNAME")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

# MyWhoosh login URL and activity page
MYWHOOSH_LOGIN_URL = "https://event.mywhoosh.com/auth/login"
MYWHOOSH_ACTIVITIES_URL = "https://event.mywhoosh.com/user/activities#profile"

download_dir = "/tmp/downloads"
download_wait_time = 5

# Setup download directory
def setup_dir():
    # Clear the download directory
    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)

    # Ensure the directory exists (recreate if necessary)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)


# Setup Selenium WebDriver
def setup_driver():
    # Set up Selenium with Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Configure Chrome to automatically download files to this directory without prompts
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set the download directory
        "download.prompt_for_download": False,  # Disable the download prompt
        "directory_upgrade": True  # Allow directory change
    })

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def login_mywhoosh(driver):
    """Logs in to MyWhoosh using Selenium."""
    driver.get(MYWHOOSH_LOGIN_URL)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(MYWHOOSH_EMAIL)
    driver.find_element(By.ID, "password").send_keys(MYWHOOSH_PASSWORD)
    driver.find_element(By.ID, "password").submit()

    WebDriverWait(driver, 10).until(EC.url_contains("user/activities"))
    print("Login to MyWhoosh successful.")


def get_latest_activity(driver):
    """Fetches the latest activity download URL from the button."""
    driver.get(MYWHOOSH_ACTIVITIES_URL)

    try:
        # Wait for the <a> element with the specific ID to be clickable
        nav_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-contact-tab3"))
        )
        
        # Force-click the <a> element using JavaScript
        driver.execute_script("arguments[0].click();", nav_tab)

        # Wait for the table or other content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btnDownload"))
        )

        # Find all buttons with the class 'btnDownload'
        buttons = driver.find_elements(By.CLASS_NAME, 'btnDownload')
        if buttons == []:
            print("No buttons found")
        
        # Choose the first button in the list
        first_button = buttons[0]

        # Click the first button
        driver.execute_script("arguments[0].click();", first_button)

        time.sleep(download_wait_time)

        # Check the download directory for the downloaded file
        downloaded_files = os.listdir(download_dir)
        # print(downloaded_files)

        print(f"Saved '{downloaded_files[0]}'.")

    except Exception as e:
        print("Error:", e)


def find_fit_file(download_dir="/tmp/downloads"):
    # List files in the download directory
    files = os.listdir(download_dir)
    
    # Filter out the .fit file (assuming only one file is expected)
    fit_files = [file for file in files if file.endswith(".fit")]
    
    if len(fit_files) == 1:
        return os.path.join(download_dir, fit_files[0])  # Return the full path of the .fit file
    else:
        print("No .fit file found or multiple .fit files found.")
        return None



def upload_to_garmin(fit_file):
    """Uploads the .fit file to Garmin Connect."""
    client = Garmin(GARMIN_USERNAME, GARMIN_PASSWORD)
    client.login()

    try:
        # Attempt to upload the .fit file
        client.upload_activity(fit_file)
        print(f"Uploaded {fit_file} to Garmin Connect")
    
    except GarthHTTPError as e:
        # Handle conflict errors (409) from the Garth library
        if "409 Client Error: Conflict" in str(e):
            print(f"Conflict error: The activity seems to already exist on Garmin Connect. Skipping upload.")
        else:
            print(f"GarthHTTPError: {e}")
            return  # Exit gracefully without raising an exception
    
    except requests.exceptions.HTTPError as e:
        # Handle other HTTP errors
        print(f"HTTPError: {e}")
        return  # Exit gracefully without raising an exception
    
    except Exception as e:
        # Handle any unexpected errors
        print(f"Unexpected error: {e}")
        return  # Exit gracefully without raising an exception


if __name__ == "__main__":
    setup_dir()
    driver = setup_driver()
    try:
        login_mywhoosh(driver)
        get_latest_activity(driver)
        fit_file = find_fit_file()
        upload_to_garmin(fit_file)
    finally:
        driver.quit()