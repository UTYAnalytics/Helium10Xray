import re
import os
import csv
import pandas as pd
import glob
from datetime import datetime, timedelta
import time
import tempfile

wait_time = 60

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import pyautogui
import time
from supabase import create_client, Client
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))

SUPABASE_URL = "https://sxoqzllwkjfluhskqlfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4b3F6bGx3a2pmbHVoc2txbGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDIyODE1MTcsImV4cCI6MjAxNzg1NzUxN30.FInynnvuqN8JeonrHa9pTXuQXMp9tE4LO0g5gj0adYE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

with tempfile.TemporaryDirectory() as download_dir:
    # and if it doesn't exist, download it automatically,
    # then add chromedriver to path
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        # "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.geolocation": 2,
        "download.default_directory": dir_path,
    }
    options = [
        # Define window size here
        "--ignore-certificate-errors",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        # "--remote-debugging-port=9222",
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "accept-language=en-US",
    ]
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_extension(dir_path + "/Helium-10.crx")
    
    for option in options:
        chrome_options.add_argument(option)


def helium_next_login(driver, username, password):
    driver.get("http://members.helium10.com")
    wait = WebDriverWait(driver, 30)
    print("login")
    try:
        username_field = wait.until(
            EC.visibility_of_element_located((By.ID, "loginform-email"))
        )
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "loginform-password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        # raise Exception
        print("Error during login:", e)


def start_driver(username, password, keyword):
    # chromedriver_path = os.path.join(dir_path, 'chromedriver.exe')  # Ensure this path is correct
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.delete_all_cookies()

    while len(driver.window_handles) == 1:
        pass
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    helium_next_login(driver, username, password)
    scrap_data_xray_product(driver, keyword)
    time.sleep(20)
    return driver


def get_newest_file(directory):
    files = glob.glob(os.path.join(directory, "*"))
    if not files:  # Check if the files list is empty
        return None
    newest_file = max(files, key=os.path.getmtime)
    return newest_file


def scrap_data_xray_product(driver, keyword):
    driver.get(f"https://www.amazon.com/s?k={keyword}")
    try:
        # Wait for the popup to be visible
        popup_visible = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "h10-serp-toolbar"))
        )
        # If the popup is visible, find and click the "Run New Search" button
        print("click Analyze Products")
        if popup_visible:
            driver.execute_script(
                """
                // Find the shadow host
                var shadowHost = document.querySelector('#h10-serp-toolbar > div');
                if (!shadowHost) {
                    console.log('Shadow host not found');
                    return;
                }
                // Access the shadow root
                var shadowRoot = shadowHost.shadowRoot;
                if (!shadowRoot) {
                    console.log('Shadow root not found');
                    return;
                }
                // Find all buttons within the shadow DOM
                var buttons = shadowRoot.querySelectorAll('button');
                console.log('Buttons found:', buttons.length);
                // Loop through buttons to find the 'Analyze Products' button and click it
                var buttonClicked = false;
                for (var i = 0; i < buttons.length; i++) {
                    console.log('Button text:', buttons[i].innerText);
                    if (buttons[i].innerText.includes('Analyze Products')) {
                        console.log('Clicking button');
                        buttons[i].click(); // Click the button
                        buttonClicked = true;
                        break; // Exit the loop once the button is found and clicked
                    }
                }
                if (!buttonClicked) {
                    console.log('Analyze Products button not found');
                }
            """
            )
            print("Download as CSV...")
            # Script to click the "Export" button inside the shadow DOM
            script = """
                return new Promise((resolve, reject) => {
                    const shadowHost = document.querySelector('#h10-xray > div');
                    if (!shadowHost) {
                        return reject(new Error('Shadow host not found'));
                    }
                    const shadowRoot = shadowHost.shadowRoot;
                    if (!shadowRoot) {
                        return reject(new Error('Shadow root not found'));
                    }

                    // Function to click the export as CSV button
                    const clickExportAsCSV = () => {
                        const csvButtons = shadowRoot.querySelectorAll('.sc-cWFgSD.jPCZvB');
                        for (let btn of csvButtons) {
                            if (btn.textContent.trim() === '...as a CSV file') {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    };

                    // Function to click the Export button and then the CSV export button
                    const attemptExportClick = () => {
                        const exportButtons = shadowRoot.querySelectorAll('button');
                        let exportButtonClicked = false;
                        for (let btn of exportButtons) {
                            if (btn.innerText.includes('Export') && !btn.disabled) {
                                btn.click(); // Click the Export button
                                exportButtonClicked = true;
                                break;
                            }
                        }

                        if (!exportButtonClicked) {
                            setTimeout(attemptExportClick, 10); // Retry clicking Export if not found
                        } else {
                            // Wait a bit for the CSV option to appear, then try to click it
                            setTimeout(() => {
                                const csvClicked = clickExportAsCSV();
                            }, 10); // Adjust timeout based on how long it usually takes for the CSV option to appear
                        }
                    };

                    // Start the process
                    attemptExportClick();
                });
                """
            # Execute the script and wait for the promise to resolve
            driver.execute_async_script(script)

    except Exception as e:
        # If the popup is not found within the timeout, handle it (e.g., by logging or skipping)
        file_path = dir_path

        newest_file_path = get_newest_file(file_path)
        # Get the current UTC time
        current_utc_time = datetime.utcnow()

        # Calculate the time difference for GMT+7
        gmt7_offset = timedelta(hours=7)
        # Get the current date and time in GMT+7
        current_time_gmt7 = current_utc_time + gmt7_offset
        if newest_file_path:
            data = pd.read_csv(newest_file_path)
            # data["sys_run_date"] = current_time_gmt7.strftime("%Y-%m-%d %H:%M:%S")
            data = data.replace("-", None)
            data = data.replace("n/a", None)
            data["sys_run_date"] = current_time_gmt7.strftime("%Y-%m-%d %H:%M:%S")
            data["keyword_main"] = keyword
            # Proceed with the database insertion
        else:
            print("No files found in the specified directory.")
        # Extract the header row
        headers = [
            "product_details",
            "asin",
            "url",
            "image_url",
            "brand",
            "price",
            "sales",
            "revenue",
            "bsr",
            "seller_country_region",
            "fees",
            "active_sellers",
            "ratings",
            "review_count",
            "images",
            "review_velocity",
            "buy_box",
            "category",
            "size_tier",
            "fulfillment",
            "dimensions",
            "weight",
            "aba_most_clicked",
            "creation_date",
            "sponsored",
            "sys_run_date",
            "keyword_main",
        ]

        numeric_columns = [
            "price",
            "sales",
            "revenue",
            "bsr",
            "fees",
            "active_sellers",
            "ratings",
            "review_count",
            "images",
            "weight",
        ]
        data.columns = headers
        for column in numeric_columns:  # Skip the first column if it's a text column
            data[column] = (
                data[column].astype(str).str.replace(",", "")
            )  # Replace comma
            data[column] = pd.to_numeric(data[column], errors="coerce")
        try:
            # Convert rows to list of dictionaries and handle NaN values
            rows_list = data.replace({np.nan: None}).to_dict(orient="records")

            # Insert the rows into the database using executemany
            response = (
                supabase.table("analyze_product_xray_helium")
                .upsert(rows_list)
                .execute()
            )

            if hasattr(response, "error") and response.error is not None:
                raise Exception(f"Error inserting rows: {response.error}")

            print(f"Rows inserted successfully")

        except Exception as e:
            print(f"Error with rows: {e}")
        print(e)


keywords = [
    "seaweed sandwich",
    "Seaweed crisps with pumpkin seeds and sesame seeds",
    "seaweed snack with almond and sesame seeds",
    "Seaweed snack with nuts",
    "Seaweed with Pumpkin Seed Original",
    "seaweed snack with almonds and cashews",
]
for keyword in keywords:
    start_driver("forheliumonly@gmail.com", "qz6EvRm65L3HdjM2!!@#$", keyword)
