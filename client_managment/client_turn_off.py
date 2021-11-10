from datetime import datetime
from client_managment.login_into_netstore import netstore_authorisation
from parsers.locators import NetstoreClientPageLocators
from selenium.common.exceptions import NoSuchElementException
from parsers.update_clients_database import edit_client_status_parameter_in_db

def close_client(browser, url):
    browser.get(url)

    try:
        turn_off_button = browser.find_element(*NetstoreClientPageLocators.CLIENT_TURN_OFF_BUTTON)
        turn_off_button.click()
    except NoSuchElementException:
        pass


def client_have_debt(browser):
    personal_account = browser.find_element(*NetstoreClientPageLocators.CLIENT_PERSONAL_ACCOUNT)
    personal_account.click()

    client_debt = float(browser.find_element(*NetstoreClientPageLocators.CLIENT_DEBT).text)
    client_have_debt_status = client_debt <= -50.0
    return client_have_debt_status


def turn_off_clients():
    date_time_now = datetime.now()
    with open('search_engine/check_client_balance.txt', 'r') as check_clients_list:
       new_check_clients_list = []
       for client_info in check_clients_list.readlines():
            client_object = client_info.split(' | ')
            client_name = client_object[0]
            date_time_close = datetime.fromisoformat(client_object[1])
            client_url = client_object[2]
            if date_time_now >= date_time_close:
                browser = netstore_authorisation(client_url)
                browser.get(client_url)
                if client_have_debt(browser):
                    close_client(browser, client_url)
                    edit_client_status_parameter_in_db(client_name, 'Неактивний')
            else:
                new_check_clients_list.append(client_info)

    with open('search_engine/check_client_balance.txt', 'w') as check_clients_list:
        for client in new_check_clients_list:
            check_clients_list.write(client)
