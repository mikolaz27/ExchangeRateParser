import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

# Set up Firefox options
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Initialize WebDriver
driver = webdriver.Firefox(executable_path='./geckodriver_32.exe', options=options)

try:
    # Open YouTube
    driver.get("https://www.youtube.com")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "search_query")))

    # Locate the search bar and search for a video
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.send_keys("Your favorite video title")  # Replace with the video title
    search_box.send_keys(Keys.RETURN)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "contents")))

    # Click on the first video in the search results
    first_video = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer ytd-thumbnail"))
    )
    first_video.click()

    # Allow the video to play for 10 seconds
    time.sleep(30)

finally:
    # Quit the driver
    driver.quit()
