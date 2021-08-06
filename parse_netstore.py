from selenium.common.exceptions import NoSuchElementException
from start_browser import driver
from locators import NetstoreLocators, NetstoreClientPageLocators
from confidential import NetstoreLoginData, UnprocessedNames
import parse_cacti
import zones_parser
import re

def get_client_connection_preferences(ip_addresses, ip_mask_dictionary):
    client_connection_preferences = {}
    for ip_addr in ip_addresses:
        for ip_zone in ip_mask_dictionary.keys():
            if ip_addr in ip_zone:
                client_connection_preferences[ip_addr] = ip_mask_dictionary[ip_zone]

    return  client_connection_preferences

def get_ipaddr_and_switch_name_and_port_from_client_note(browser, note, switch_name_ip_dict):
    client_ip_addresses = tuple(ip_address.text for ip_address in browser.find_elements(*NetstoreClientPageLocators.IP_ADDRESSES))

    switches = re.findall(r'==[A-Za-z0-9-_\/. #]+==', note)
    switches = tuple(switch.strip('==') for switch in switches)

    # mac_addresses = re.findall(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', note)
    # mac_addresses += re.findall(r'\w\w\w\w-\w\w\w\w-\w\w\w\w', note)
    #
    # if len(mac_addresses) > len(client_ip_addresses):
    #     connection_interfaces = []
    #     for i in range(len(switches)-1):
    #         connection_interface = []
    #         for mac_address in mac_addresses:
    #             if note.index(switches[i]) < note.index(mac_address) < note.index(switches[i+1]):
    #                 connection_interface.append(mac_address)
    #         connection_interfaces.append(connection_interface)
    #
    #     index = -1
    #     connection_interface = []
    #     for _ in range(len(mac_addresses)):
    #         if not connection_interfaces:
    #             connection_interfaces = [mac_addresses]
    #         elif mac_addresses[index] not in connection_interfaces[-1]:
    #             connection_interface.append(mac_addresses[index])
    #             index -= 1
    #     connection_interfaces.append(connection_interface)
    #     mac_addresses = connection_interfaces

    client_connection_data = {}
    for i in range(len(client_ip_addresses)):
        if not switches:
            client_connection_data[client_ip_addresses[i]] = 'В нотатках клиента необходимо указать название свича и порт подключения в виде "==switch_name sw1#port==" где "switch_name sw1" - название свича из Cacti, "port" - порт подключения. Знаки "==" и "#" обязательны'
            break
        try:
            client_port = re.findall(r'#\d+', switches[i])
        except IndexError:
            client_port = re.findall(r'#\d+', switches[0])
        try:
            client_switch_name = switches[i][:switches[i].index('#')].strip()
        except IndexError:
            client_switch_name = switches[0][:switches[0].index('#')].strip()
        except ValueError:
            client_switch_name = switches[0].strip()
        try:
            client_switch_ip = switch_name_ip_dict[client_switch_name]
        except KeyError:
            client_switch_ip = 'ip адресс свича не найден'
        # try:
        #     client_mac_address = mac_addresses[i]
        # except IndexError:
        #     client_mac_address = 'ff:ff:ff:ff:ff:ff'
        # client_connection_data[client_ip_addresses[i]] = (client_switch, client_port[0], client_mac_address)
        try:
            client_connection_data[client_ip_addresses[i]] = (client_switch_name, client_switch_ip, client_port[0])
        except IndexError:
            client_connection_data = {'Ошибка в данных подключения, проверьте Нетсторе'}

    return client_connection_data

def collect_client_data(browser, clients):
    clients_name_url = []
    switch_name_ip_dict = parse_cacti.main()
    ip_mask_dictionary = zones_parser.main()

    for client in clients:
        client_object = client.find_element_by_tag_name('a')
        client_name = client_object.text
        client_netstore_url = client_object.get_attribute("href").replace('_properties', '_client')
        clients_name_url.append((client_name, client_netstore_url))

    client_data = {}
    for client in clients_name_url:
        client_name = client[0].lower()
        client_netstore_url = client[1]

        if client_name in UnprocessedNames.not_processed_clients:
            continue

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
        # client_connection_data = get_ipaddr_switch_name_port_macAddress_from_client_note(browser, client_notes)
        client_connection_data = get_ipaddr_and_switch_name_and_port_from_client_note(browser, client_notes, switch_name_ip_dict)
        client_connection_preferences = get_client_connection_preferences(client_connection_data.keys(), ip_mask_dictionary)
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
                                  client_connection_preferences,
                                  client_netstore_url)
    return client_data

def get_all_clients_from_netstore(url, login_, passw):
    try:
        browser = driver(url)

        login = browser.find_element(*NetstoreLocators.LOGIN)
        login.send_keys(login_)

        passwd = browser.find_element(*NetstoreLocators.PASSWD)
        passwd.send_keys(passw)

        enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
        enter_button.click()

        open_all_clients_button = browser.find_element(*NetstoreLocators.GET_ALL_CLIENTS_PAGE)
        open_all_clients_button.click()

        dict_of_clients_from_netstore = {}

        client_objects = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST) + browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
        dict_of_clients_from_netstore.update(collect_client_data(browser, client_objects))

    finally:
        browser.quit()
    return dict_of_clients_from_netstore

def update_clients():
    clients = {}
    # clients.update(get_all_clients_from_netstore(NetstoreLoginData.netstore1_url,
    #                                         NetstoreLoginData.netstore1_login,
    #                                         NetstoreLoginData.netstore_passwd,
    #                                         ))
    clients.update(get_all_clients_from_netstore(NetstoreLoginData.netstore2_url,
                                                NetstoreLoginData.netstore2_login,
                                                NetstoreLoginData.netstore_passwd,
                                                ))
    return clients



