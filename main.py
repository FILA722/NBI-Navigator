from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from locators import NetstoreLocators
from confidential import NetstoreLoginData
import parse_netstore
import time

def driver(url):
    #Start browser in HEADLESS MODE
    options = FirefoxOptions()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    browser.get(url)

    #Start browser in VISUAL MODE
    # browser = webdriver.Firefox()
    # browser.get(url)
    return browser

def main():
    try:
        browser = driver(NetstoreLoginData.netstore1_url)
        clients = parse_netstore.get_all_clients_from_netstore(browser,
                                                                NetstoreLoginData.netstore1_login,
                                                                NetstoreLoginData.netstore_passwd,
                                                               )

        browser = driver(NetstoreLoginData.netstore2_url)
        clients.update(parse_netstore.get_all_clients_from_netstore(browser,
                                                                     NetstoreLoginData.netstore2_login,
                                                                     NetstoreLoginData.netstore_passwd,
                                                                     ))
    finally:
        browser.quit()
    # client_name = clients['ПЛАНЕТА 2020 ТОВ']
    # browser.execute_script("return arguments[0].scrollIntoView(true);", client_name)
    # client_name.click()
    # browser.find_element(*NetstoreLocators.GET_INFO_ABOUT_THE_CLIENT).click()

    # time.sleep(30)


main()