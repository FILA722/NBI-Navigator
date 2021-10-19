from parsers.locators import NetstoreLocators, NetstoreDebtorClient
from parsers.confidential import NetstoreLoginData
from start_browser import driver
from debugers.check_ping_status import ping_status


def get_debtor_clients():
    try:
        browser = driver(NetstoreLoginData.netstore1_url)

        login = browser.find_element(*NetstoreLocators.LOGIN)
        login.send_keys(*NetstoreLoginData.netstore1_login)

        passwd = browser.find_element(*NetstoreLocators.PASSWD)
        passwd.send_keys(*NetstoreLoginData.netstore_passwd)

        enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
        enter_button.click()

        zvity_button = browser.find_element(*NetstoreDebtorClient.ZVITU_BUTTON)
        zvity_button.click()

        min_saldo_button = browser.find_element(*NetstoreDebtorClient.MIN_SALDO_BUTTON)
        min_saldo_button.click()

        

    finally:
        browser.quit()

    return debtor_clients_netstore1_list, debtor_clients_netstore2_list




