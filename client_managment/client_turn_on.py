import time
from parsers.locators import NetstoreClientPageLocators
from client_managment.login_into_netstore import netstore_authorisation
from selenium.common.exceptions import NoSuchElementException


def turn_on(client_url):
    browser = netstore_authorisation(client_url)
    browser.get(client_url)
    time.sleep(2)
    try:
        turn_on_button = browser.find_element(*NetstoreClientPageLocators.CLIENT_TURN_ON_BUTTON)
        turn_on_button.click()
    except NoSuchElementException:
        return False
    finally:
        browser.close()
    return True


