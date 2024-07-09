import csv
import os
import re
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def sanitize_filename(url):
    # Remove characters that are not allowed in filenames
    return re.sub(r'[\\/*?:"<>|]', "_", url)

def close_popups(driver):
    main_window = driver.current_window_handle
    popups_detected = False
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            print(f"Closing popup window: {driver.current_url}")
            driver.close()
            popups_detected = True
    driver.switch_to.window(main_window)
    return popups_detected

def take_screenshot(driver, rank, url, screenshot_path):
    try:
        driver.get(url)
        # Wait for the page to load completely
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        # Additional wait to ensure all elements load
        WebDriverWait(driver, 15).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        # Close any pop-up windows
        popups_detected = close_popups(driver)
        if popups_detected:
            print(f"Pop-ups detected for: {url}")
            return False
        # Wait for an additional 2 seconds to ensure rendering
        time.sleep(2)
        # Take a screenshot and save it
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for: {url}")
        return True
    except (WebDriverException, TimeoutException, NoSuchWindowException) as e:
        print(f"Failed to load: {url} (Error: {e})")
        return False

def process_website(driver, rank, url, screenshots_dir):
    sanitized_url = sanitize_filename(url)
    screenshot_filename = f"{rank}_{sanitized_url}.png"
    screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(take_screenshot, driver, rank, url, screenshot_path)
        try:
            result = future.result(timeout=15)
            if not result:
                return False
        except concurrent.futures.TimeoutError:
            print(f"Timeout occurred for: {url}")
            return False
    return True

def main():
    input_file = 'top_1200_south_korea_websites.csv'
    screenshots_dir = 'screenshots'
    failed_file = 'failed_websites.csv'

    # Create screenshots directory if it doesn't exist
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    options = Options()
    options.headless = True  # Run Firefox in headless mode
    binary_path = "C:\\Program Files\\Firefox Nightly\\firefox.exe" 
    options.binary_location = binary_path

    # Block pop-ups
    options.set_preference("dom.popup_maximum", 0)
    options.set_preference("privacy.popups.showBrowserMessage", False)
    options.set_preference("dom.disable_open_during_load", True)

    print(f"Using Firefox binary at: {binary_path}")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    
    failed_list = []

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            rank, url = row
            if not process_website(driver, rank, url, screenshots_dir):
                failed_list.append((rank, url))
        
    driver.quit()

    # Write failed websites to CSV
    with open(failed_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Rank', 'URL'])
        writer.writerows(failed_list)

if __name__ == '__main__':
    main()
