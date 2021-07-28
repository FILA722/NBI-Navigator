from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from locators import NetstoreLocators
from confidential import NetstoreLoginData
import time

def get_all_clients_from_netstore(browser, login_, passw):

    login = browser.find_element(*NetstoreLocators.LOGIN)
    login.send_keys(login_)

    passwd = browser.find_element(*NetstoreLocators.PASSWD)
    passwd.send_keys(passw)

    enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
    enter_button.click()

    open_all_clients_button = browser.find_element(*NetstoreLocators.GET_ALL_CLIENTS_PAGE)
    open_all_clients_button.click()

    dict_of_clients_from_netstore = {}

    active_clients_from_netstore = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST)
    for active_client in active_clients_from_netstore:
        name = active_client.find_element_by_css_selector('a')
        dict_of_clients_from_netstore[name.text] = name

    terminated_clients_from_netstore = browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
    for terminated_client in terminated_clients_from_netstore:
        name = terminated_client.find_element_by_css_selector('a')
        dict_of_clients_from_netstore[name.text] = name

    return dict_of_clients_from_netstore



