from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver


def driver(url):
    #Start browser in HEADLESS MODE
    # options = FirefoxOptions()
    # options.add_argument("--headless")
    # browser = webdriver.Firefox(options=options)
    # browser.get(url)

    #Start browser in VISUAL MODE
    browser = webdriver.Firefox()
    browser.get(url)

    return browser