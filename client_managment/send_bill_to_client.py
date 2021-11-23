from client_managment import login_into_netstore
from parsers.locators import NetstoreClientPageLocators
from selenium.common.exceptions import NoSuchElementException


def send_bill_via_email(url):
    try:
        browser = login_into_netstore.netstore_authorisation(url)
        bill_url = url.replace('client', 'bill', 1)

        browser.get(bill_url)
        bill_btn = browser.find_element(*NetstoreClientPageLocators.CLIENT_SEND_BILL)
        bill_btn.click()
        return True

    except NoSuchElementException:
        return False

    finally:
        browser.quit()