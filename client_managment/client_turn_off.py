import json
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
    with open('search_engine/check_client_balance.json', 'r') as check_clients_data:
        check_clients_dict = json.load(check_clients_data)
        new_check_clients_dict = {}
        for client_name in check_clients_dict.keys():
            client_object = check_clients_dict[client_name]
            date_time_close = datetime.fromisoformat(client_object[0])
            client_url = client_object[1]
            if date_time_now >= date_time_close:
                browser = netstore_authorisation(client_url)
                browser.get(client_url)
                if client_have_debt(browser):
                    close_client(browser, client_url)
                    edit_client_status_parameter_in_db(client_name, 'Неактивний')
                    client_object += ['Только после оплаты!']
                    new_check_clients_dict[client_name] = client_object
            else:
                new_check_clients_dict[client_name] = client_object

    with open('search_engine/check_client_balance.json', 'w') as check_clients_list:
        json.dump(new_check_clients_dict, check_clients_list, indent=2, sort_keys=True, ensure_ascii=False)


def check_client_debt_status(client_name):
    with open('search_engine/check_client_balance.json', 'r') as check_clients_data:
        check_clients_dict = json.load(check_clients_data)
    if client_name in check_clients_dict.keys():
        client_object = check_clients_dict[client_name]
        if client_object[-1] == 'Только после оплаты!':
            return 'Только после оплаты!'
        else:
            date_time_close_obj = datetime.fromisoformat(client_object[0])
            date_time_close = f'Включен до {date_time_close_obj.strftime("%d.%m.%Y")}'

            return date_time_close
    else:
        return 'False'