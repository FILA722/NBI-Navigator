import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from start_browser import driver
from locators import NetstoreLocators, NetstoreClientPageLocators
from confidential import NetstoreLoginData
import re
import json

def get_ipaddr_switch_name_port_macAddress_from_client_note(browser, note):
    client_ip_addresses = tuple(ip_address.text for ip_address in browser.find_elements(*NetstoreClientPageLocators.IP_ADDRESSES))

    switches = re.findall(r'==[A-Za-z0-9-_\/. #]+==', note)
    switches = tuple(switch.strip('==') for switch in switches)
    mac_addresses = re.findall(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', note)

    client_connection_data = {}
    for i in range(len(client_ip_addresses)):
        client_port = re.findall(r'#\d+', switches[i])
        client_switch = switches[i].strip(client_port[0])
        client_mac_address = mac_addresses[i]
        client_connection_data[client_ip_addresses[i]] = (client_switch, client_port[0], client_mac_address)

    return client_connection_data

# def collect_client_data(browser, clients):
def collect_client_data(browser, clients):
    clients_name_url = []
    for client in clients:
        client_object = client.find_element_by_tag_name('a')
        client_name = client_object.text
        client_netstore_url = client_object.get_attribute("href").replace('_properties', '_client')
        clients_name_url.append((client_name, client_netstore_url))

    client_data = {}
    for client in clients_name_url:
        client_name = client[0]
        client_netstore_url = client[1]

        browser.get(client_netstore_url)

        client_tel = browser.find_element(*NetstoreClientPageLocators.TEL).get_attribute("value")
        client_email = browser.find_element(*NetstoreClientPageLocators.EMAIL).get_attribute("value")
        try:
            client_physical_address = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS).text
            client_physical_address_notes = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS_NOTES).text
        except NoSuchElementException:
            client_physical_address = None
            client_physical_address_notes = None

        client_is_active = browser.find_element(*NetstoreClientPageLocators.IS_ACTIVE).text
        client_is_converter = browser.find_element(*NetstoreClientPageLocators.IS_CONVERTER).get_attribute("checked")
        client_speed = browser.find_element(*NetstoreClientPageLocators.SPEED).get_attribute("value")
        client_notes = browser.find_element(*NetstoreClientPageLocators.NOTES).text
        client_connection_data = get_ipaddr_switch_name_port_macAddress_from_client_note(browser, client_notes)

        client_data[client_name] = (
                                  client_tel,
                                  client_email,
                                  client_physical_address,
                                  client_physical_address_notes,
                                  client_is_active,
                                  client_is_converter,
                                  client_speed,
                                  client_notes,
                                  client_connection_data,
                                  client_netstore_url)
    return client_data
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
    dict_of_clients_from_netstore.update(collect_client_data(browser, active_clients_from_netstore))

    terminated_clients_from_netstore = browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
    dict_of_clients_from_netstore.update(collect_client_data(browser, terminated_clients_from_netstore))

    return dict_of_clients_from_netstore

def update_clients():
    try:
        clients = {}
        browser = driver(NetstoreLoginData.netstore1_url)
        clients.update(get_all_clients_from_netstore(browser,
                                                NetstoreLoginData.netstore1_login,
                                                NetstoreLoginData.netstore_passwd,
                                                ))

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



