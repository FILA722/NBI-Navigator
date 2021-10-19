from start_browser import driver
from parsers.locators import NetstoreLocators
from parsers.confidential import NetstoreLoginData
import re

def netstore_authorisation(client_url):

    is_this_netstore2 = re.search('netstore2', client_url)
    if is_this_netstore2:
        url = NetstoreLoginData.netstore2_url
        admin_login = NetstoreLoginData.netstore2_login
    else:
        url = NetstoreLoginData.netstore1_url
        admin_login = NetstoreLoginData.netstore1_login

    browser = driver(url)

    login = browser.find_element(*NetstoreLocators.LOGIN)
    login.send_keys(admin_login)

    passwd = browser.find_element(*NetstoreLocators.PASSWD)
    passwd.send_keys(*NetstoreLoginData.netstore_passwd)

    enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
    enter_button.click()

    return browser