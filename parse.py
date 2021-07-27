from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from confidential import NetstoreLocators
from confidential import LoginData
import time

def get_all_clients_from_netstore1():
    options = FirefoxOptions()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    # browser = webdriver.Firefox()
    browser.get('https://netstore.nbi.com.ua/index.php')

    login = browser.find_element(*NetstoreLocators.NETSTORE1_LOGIN)
    login.send_keys(LoginData.netstore1_login)

    passwd = browser.find_element(*NetstoreLocators.NETSTORE1_PASSWD)
    passwd.send_keys(LoginData.netstore_passwd)

    browser.find_element(*NetstoreLocators.NETSTORE1_ENTER_BUTTON).click()
    browser.find_element(*NetstoreLocators.GET_ALL_CLIENTS_PAGE).click()

    active_clients_from_netstore1 = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST)

    dict_of_active_clients_from_netstore1 = {}
    for client in active_clients_from_netstore1:
        name = client.find_element_by_css_selector('a')
        dict_of_active_clients_from_netstore1[name.text] = name

    # client_name = dict_of_active_clients_from_netstore1['ПЛАНЕТА 2020 ТОВ']
    # browser.execute_script("return arguments[0].scrollIntoView(true);", client_name)
    # client_name.click()
    browser.find_element(*NetstoreLocators.GET_INFO_ABOUT_THE_CLIENT).click()

    time.sleep(30)
    browser.quit()

get_all_clients_from_netstore1()


