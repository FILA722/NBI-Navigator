from client_managment import login_into_netstore
from parsers.locators import NetstoreLocators, NetstoreClientPageLocators
from debugers.check_ping_status import ping_status


def send_bill_via_email(url):
    try:
       browser = login_into_netstore.netstore_authorisation(url)
       #нужно перейти на страницу выставленных счетов
       return True

    finally:
        browser.quit()