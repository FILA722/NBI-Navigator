from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
import logging
import time

def driver(url):
    #Start browser in HEADLESS MODE
    options = FirefoxOptions()
    options.add_argument("--headless")
    try:
        browser = webdriver.Firefox(options=options)
        # browser.get(url)
    except WebDriverException:
        logging.info(f'WebDriverException with request to the {url}')
        time.sleep(15)
        browser = webdriver.Firefox(options=options)
        logging.info(f'WebDriverException again with request to the {url}')

    browser.get(url)

    #Start browser in VISUAL MODE
    # browser = webdriver.Firefox()
    # browser.get(url)

    return browser