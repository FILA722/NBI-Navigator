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
        # browser = webdriver.Firefox(options=options, executable_path='/usr/local/bin/geckodriver')
        browser.get(url)
    except WebDriverException:
        time.sleep(60)
        browser = webdriver.Firefox(options=options)
        # browser = webdriver.Firefox(options=options, executable_path='/usr/local/bin/geckodriver')

    browser.get(url)

    #Start browser in VISUAL MODE
    # browser = webdriver.Firefox()
    # browser.get(url)

    return browser