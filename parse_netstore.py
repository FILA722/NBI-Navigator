from start_browser import driver
from locators import NetstoreLocators
from confidential import NetstoreLoginData
import json

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
        client_object = active_client.find_element_by_css_selector('a')
        dict_of_clients_from_netstore[client_object.text] = client_object.get_attribute("href").replace('_properties', '_client')

    terminated_clients_from_netstore = browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
    for terminated_client in terminated_clients_from_netstore:
        client_object = terminated_client.find_element_by_css_selector('a')
        dict_of_clients_from_netstore[client_object.text] = client_object.get_attribute("href").replace('_properties', '_client')

    return dict_of_clients_from_netstore

def get_client_netstore_info(url):
    client_page = driver(url)

def update_clients():
    try:
        browser = driver(NetstoreLoginData.netstore1_url)
        clients = get_all_clients_from_netstore(browser,
                                                NetstoreLoginData.netstore1_login,
                                                NetstoreLoginData.netstore_passwd,
                                                )

        browser = driver(NetstoreLoginData.netstore2_url)
        clients.update(get_all_clients_from_netstore(browser,
                                                    NetstoreLoginData.netstore2_login,
                                                    NetstoreLoginData.netstore_passwd,
                                                    ))

        json_clients_dict = json.dumps(clients, indent=2, sort_keys=True, ensure_ascii=False)
        with open('clients.json', 'w') as dict_with_clients:
            dict_with_clients.write(json_clients_dict)
        return 'Обновление списка клиентов успешно завершено'

    finally:
        browser.quit()



