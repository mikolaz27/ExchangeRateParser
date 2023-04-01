import os
import time

from selenium.webdriver.firefox.options import Options

from selenium import webdriver

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(executable_path='./geckodriver_32.exe', options=options)

driver.get("http://selenium.dev")

time.sleep(5)
driver.quit()
