import logging
import time
from start_browser import driver
from debugers.check_ping_status import ping_status
from parsers.confidential import CactiLoginData
from parsers.locators import NetstoreLocators, NetstoreClientPageLocators
from debugers.find_switch_model import find_sw_model
from parsers import parse_cacti, parse_zones, confidential
from parsers.parse_cacti import update_clients_cacti_image_db
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib3.exceptions import MaxRetryError
from client_managment.login_into_netstore import netstore_authorisation
from datetime import datetime, timedelta
from parsers.pathes import Pathes
import json
import re


def update_switch_name_ip_file():
    switch_name_ip_dict = parse_cacti.main()

    with open(Pathes.switch_name_ip_dict_path, 'r') as switch_name_ip_data_old:
        switch_name_ip_dict_old = json.load(switch_name_ip_data_old)

    if switch_name_ip_dict != switch_name_ip_dict_old:
        update_clients_cacti_image_db()
        with open(Pathes.switch_name_ip_dict_path, 'w') as switch_name_ip_data:
            json.dump(switch_name_ip_dict, switch_name_ip_data, indent=2, sort_keys=True, ensure_ascii=False)

    return True


def add_client_into_contract_name_dict(client_name, client_url):
    with open(Pathes.client_contract_name_dict_path, 'r') as client_contract_name_data:
        client_contract_name_dict = json.load(client_contract_name_data)

    browser = netstore_authorisation(client_url)
    client_contracts = get_client_contracts(browser, client_url)

    if len(client_contracts) == 1:
        client_contracts_for_dict = client_contracts[0]
    else:
        client_contracts_for_dict = ''
        for client_contract in client_contracts:
            client_contracts_for_dict += f'{client_contract}+'

    client_contract_name_dict[client_contracts_for_dict.strip('+')] = client_name

    with open(Pathes.client_contract_name_dict_path, 'w') as client_contract_name_data:
        json.dump(client_contract_name_dict, client_contract_name_data, sort_keys=True, indent=2, ensure_ascii=False)


def update_client_contract_name_dict():
    with open(Pathes.clients_path, 'r') as clients_data:
        clients_dict = json.load(clients_data)

    client_contract_name_dict = {}
    for client_name in clients_dict.keys():
        client_contracts = clients_dict[client_name][10]
        if len(client_contracts) == 1:
            client_contracts_key = client_contracts[0]
        else:
            client_contracts_key = ''
            for client_contract in client_contracts:
                client_contracts_key += f'{client_contract}+'
        client_contract_name_dict[client_contracts_key.strip('+')] = client_name

    with open(Pathes.client_contract_name_dict_path, 'w') as client_contract_name_data:
        json.dump(client_contract_name_dict, client_contract_name_data, sort_keys=True, indent=2, ensure_ascii=False)


def add_client_into_ip_name_dict(client_name, client_ips):
    with open(Pathes.client_ip_name_dict_path, 'r') as client_ip_name_data:
        client_ip_name_dict = json.load(client_ip_name_data)

    if len(client_ips) == 1:
        client_ips_for_dict = client_ips[0]
    else:
        client_ips_for_dict = ''
        for client_ip in client_ips:
            client_ips_for_dict += f'{client_ip}+'

    client_ip_name_dict[client_ips_for_dict.strip('+')] = client_name

    with open(Pathes.client_ip_name_dict_path, 'w') as client_ip_name_data:
        json.dump(client_ip_name_dict, client_ip_name_data, indent=2, ensure_ascii=False)


def update_client_ip_name_dict():
    with open(Pathes.clients_path, 'r') as clients_data:
        clients_dict = json.load(clients_data)

    client_ip_name_dict = {}
    for client_name in clients_dict.keys():
        client_ip_addresses = clients_dict[client_name][8].keys()
        if len(client_ip_addresses) == 1:
            client_ips = list(client_ip_addresses)[0]
        else:
            client_ips = ''
            for client_ip in client_ip_addresses:
                client_ips += f'{client_ip}+'
        client_ip_name_dict[client_ips.strip('+')] = client_name

    with open(Pathes.client_ip_name_dict_path, 'w') as client_ip_name_data:
        json.dump(client_ip_name_dict, client_ip_name_data, indent=2, ensure_ascii=False)


def update_clients_ip_gateway_mask_file():
    clients_ip_gateway_mask_dict = parse_zones.get_zone_data()

    if clients_ip_gateway_mask_dict:
        clients_ip_gateway_mask_dict_json = {}
        for key in clients_ip_gateway_mask_dict.keys():
            value = clients_ip_gateway_mask_dict[key]
            key_json = str(key).replace(r"'", '').strip('()')
            clients_ip_gateway_mask_dict_json[key_json.replace(' ', '')] = value

        with open(Pathes.clients_ip_gateway_mask_dict_path, 'w') as clients_ip_gateway_mask_data:
            json.dump(clients_ip_gateway_mask_dict_json, clients_ip_gateway_mask_data, indent=2, sort_keys=True, ensure_ascii=False)

def update_closed_clinents_name_url_dict(url, closed_clients_netstore_url):
    closed_clients_name_url_dict = {}
    for closed_client_object in closed_clients_netstore_url:
        closed_clients_name_url_dict[closed_client_object[0]] = closed_client_object[1]

    if 'netstore2' in url:
        with open(Pathes.closed_clients_name_url_data_path, 'r') as closed_clients_name_url_data_from_netst1:
            closed_clients_name_url_dict_from_netst1 = json.load(closed_clients_name_url_data_from_netst1)

        closed_clients_name_url_dict.update(closed_clients_name_url_dict_from_netst1)

    with open(Pathes.closed_clients_name_url_data_path, 'w') as closed_clients_name_url_data:
        json.dump(closed_clients_name_url_dict, closed_clients_name_url_data, indent=2, sort_keys=True, ensure_ascii=False)


def edit_client_status_parameter_in_db(client_name, client_status):
    with open(Pathes.clients_path, 'r') as open_clients_db:
        clients = json.loads(open_clients_db.read())
        clients[client_name][4] = client_status
        client_url = clients[client_name][9]

    with open(Pathes.clients_path, 'w') as save_clients_db:
        json.dump(clients, save_clients_db, indent=2, sort_keys=True, ensure_ascii=False)

    return client_url


def migrate_client_from_terminated_to_active(client_name):
    with open(Pathes.terminated_clients_name_url_data_path, 'r') as terminated_clients_name_url_data:
        terminated_clients_name_url_dict = json.load(terminated_clients_name_url_data)
        if client_name in terminated_clients_name_url_dict.keys():
            client_url = terminated_clients_name_url_dict[client_name]
            del terminated_clients_name_url_dict[client_name]

            with open(Pathes.active_clients_name_url_data_path, 'r') as active_clients_name_url_data:
                active_clients_name_url_dict = json.load(active_clients_name_url_data)
                active_clients_name_url_dict[client_name] = client_url

            with open(Pathes.terminated_clients_name_url_data_path, 'w') as terminated_clients_name_url_data_write:
                json.dump(terminated_clients_name_url_dict, terminated_clients_name_url_data_write, indent=2, sort_keys=True, ensure_ascii=False)

            with open(Pathes.active_clients_name_url_data_path, 'w') as active_clients_name_url_data_write:
                json.dump(active_clients_name_url_dict, active_clients_name_url_data_write, indent=2, sort_keys=True, ensure_ascii=False)


def remove_client_from_check_client_balance_data(client_name):
    with open(Pathes.check_client_balance_path, 'r') as check_client_balance_data:
        check_client_balance_dict = json.load(check_client_balance_data)
        if client_name in check_client_balance_dict.keys():
            del check_client_balance_dict[client_name]

            with open(Pathes.check_client_balance_path, 'w') as check_client_balance_data_write:
                json.dump(check_client_balance_dict, check_client_balance_data_write, indent=2, sort_keys=True, ensure_ascii=False)


def add_client_to_check_client_balance_data(client_name, client_url):
    check_client_balance_date = set_client_balance_check_date()
    with open(Pathes.check_client_balance_path, 'r') as check_client_balance_data:
        check_client_balance_dict = json.load(check_client_balance_data)
        if client_name not in check_client_balance_dict.keys():
            check_client_balance_dict[client_name] = [check_client_balance_date, client_url]

            with open(Pathes.check_client_balance_path, 'w') as check_client_balance_data_write:
                json.dump(check_client_balance_dict, check_client_balance_data_write, indent=2, sort_keys=True, ensure_ascii=False)


def add_client_into_global_db(client_name, client_url, client_data):
    client_tel = client_data[0]
    client_email = client_data[1]
    client_physical_address = client_data[2]
    client_physical_address_notes = client_data[3]
    client_is_active = client_data[4]
    client_is_converter = client_data[5]
    client_manager = client_data[6]
    client_notes = client_data[7]
    client_connection_data = client_data[8]
    client_contracts = client_data[10]

    with open(Pathes.clients_path, 'r') as clients:
        clients_dict = json.load(clients)
        clients_dict[client_name] = (
            client_tel,
            client_email,
            client_physical_address,
            client_physical_address_notes,
            client_is_active,
            client_is_converter,
            client_manager,
            client_notes,
            client_connection_data,
            client_url,
            client_contracts)

    with open(Pathes.clients_path, 'w') as clients_data:
        json.dump(clients_dict, clients_data, indent=2, sort_keys=True, ensure_ascii=False)


def load_clients_ip_gateway_mask_file():
    with open(Pathes.clients_ip_gateway_mask_dict_path, 'r') as clients_ip_gateway_mask_str_dict_json:
        clients_ip_gateway_mask_str_dict = json.load(clients_ip_gateway_mask_str_dict_json)

        clients_ip_gateway_mask_dict = {}
        for key in clients_ip_gateway_mask_str_dict.keys():
            value = clients_ip_gateway_mask_str_dict[key]
            tuple_key = tuple(key.split(','))
            clients_ip_gateway_mask_dict[tuple_key] = value

        return clients_ip_gateway_mask_dict


def get_manager_info(name):
    return confidential.MANAGERS.manager_dictionary[name]


def remake_client_port_for_cacti_urls_dict(port):
    client_port = int(port.strip('#'))
    if client_port < 10:
        cacti_port = f'Port 0{client_port}'
    else:
        cacti_port = f'Port {client_port}'

    return cacti_port


def strip_symbols_from_client_name(name):
    client_name = name.lower()
    replace_symbols = ('(', ')', '/', '.', ',', '\\')
    for symbol in replace_symbols:
        client_name = client_name.replace(symbol, ' ')

    return client_name.strip()


def get_client_connection_preferences(ip_addresses, ip_mask_dictionary):
    client_connection_preferences = {}
    for ip_addr in ip_addresses:
        for ip_zone in ip_mask_dictionary.keys():
            if ip_addr in ip_zone:
                client_connection_preferences[ip_addr] = ip_mask_dictionary[ip_zone]

    return client_connection_preferences


def get_switch_name(client_switch_ip):
    for switch_model_ips in confidential.SwitchModels.switches:
        if client_switch_ip in switch_model_ips:
            return switch_model_ips[0]

    sw_model = find_sw_model(client_switch_ip)
    return sw_model


def get_client_contracts(browser, client_netstore_url):
    client_netstore_contract_page = client_netstore_url.replace('client', 'contract', 1)

    try:
        browser.get(client_netstore_contract_page)
    except TimeoutException:
        browser.quit()
        time.sleep(300)
        browser = netstore_authorisation(client_netstore_contract_page)
    except MaxRetryError:
        time.sleep(300)
        browser = netstore_authorisation(client_netstore_contract_page)

    client_contracts_objects = browser.find_elements(*NetstoreClientPageLocators.CLIENT_CONTRACTS)
    client_contracts = []
    i = 0
    while i < len(client_contracts_objects):
        record = client_contracts_objects[i].get_attribute("value")
        if record in ('АУ', 'НБ', 'Ау', 'ау', 'аУ', 'Нб', 'нб', 'нБ'):
            client_contract = f'{record}{client_contracts_objects[i + 1].get_attribute("value")}'
            client_contracts.append(client_contract.lower())
            i += 2
        else:
            i += 1

    return client_contracts


def set_client_balance_check_date():
    #исключаем выходные дни
    date_now = datetime.now()
    check_date = date_now + timedelta(days=3)

    if check_date.weekday() in (5, 6, 0):
        check_date = date_now + timedelta(days=5)

    if int(check_date.day) < 10:
        check_day = f'0{check_date.day}'
    else:
        check_day = check_date.day

    if int(check_date.month) < 10:
        check_month = f'0{check_date.month}'
    else:
        check_month = check_date.month

    client_balance_check_date = str(datetime.fromisoformat(f'{check_date.year}-{check_month}-{check_day} 12:00:00'))

    return client_balance_check_date


def process_turned_on_clients(active_client_name_url_dict, terminated_client_name_url_dict):
    with open(Pathes.active_clients_name_url_data_path, 'r') as active_client_name_url_data:
        active_client_name_url_dict_old = json.load(active_client_name_url_data)

    with open(Pathes.terminated_clients_name_url_data_path, 'r') as terminated_client_name_url_data:
        terminated_client_name_url_dict_old = json.load(terminated_client_name_url_data)

    if active_client_name_url_dict_old != active_client_name_url_dict:
        with open(Pathes.clients_path, 'r') as clients_data:
            clients_names = list(json.load(clients_data).keys())

        new_clients = active_client_name_url_dict.keys() - active_client_name_url_dict_old.keys()

        credit_clients = {}
        for new_client in new_clients:

            client_name, client_url = new_client, active_client_name_url_dict[new_client]
            if client_name in terminated_client_name_url_dict_old.keys():
                edit_client_status_parameter_in_db(client_name, 'Активний')
                check_client_balance_date = set_client_balance_check_date()
                credit_clients[client_name] = [check_client_balance_date, client_url]

            elif client_name not in terminated_client_name_url_dict_old.keys() and client_name not in clients_names:
                browser = netstore_authorisation(client_url)
                client_data = get_client_data(browser, client_url)
                browser.quit()
                add_client_into_global_db(client_name, client_url, client_data)
                add_client_into_ip_name_dict(client_name, tuple(client_data[8].keys()))
                add_client_into_contract_name_dict(client_name, client_url)

        if credit_clients:
            with open(Pathes.check_client_balance_path, 'r') as check_clients:
                check_clients_dict = json.load(check_clients)

            with open(Pathes.check_client_balance_path, 'w') as check_clients_to_write:
                check_clients_dict.update(credit_clients)
                json.dump(check_clients_dict, check_clients_to_write, indent=2, sort_keys=True, ensure_ascii=False)

        with open(Pathes.active_clients_name_url_data_path, 'w') as active_client_name_url_data:
            json.dump(active_client_name_url_dict, active_client_name_url_data, indent=2, sort_keys=True, ensure_ascii=False)

    if terminated_client_name_url_dict_old != terminated_client_name_url_dict:
        turned_off_clients = terminated_client_name_url_dict.keys() - terminated_client_name_url_dict_old.keys()
        if turned_off_clients:
            for client_name in turned_off_clients:
                edit_client_status_parameter_in_db(client_name, 'Неактивний')

        with open(Pathes.terminated_clients_name_url_data_path, 'w') as terminated_client_name_url_data:
            json.dump(terminated_client_name_url_dict, terminated_client_name_url_data, indent=2, sort_keys=True, ensure_ascii=False)

def get_ipaddr_and_switch_name_and_port_from_client_note(browser, note):
    client_ip_addresses = tuple(ip_address.text for ip_address in browser.find_elements(*NetstoreClientPageLocators.IP_ADDRESSES))
    switches = re.findall(r'==[A-Za-z0-9-_\/. #]+==', note)
    switches = tuple(switch.strip('==') for switch in switches)

    client_connection_data = {}
    if not client_ip_addresses:
        client_connection_data['IP не указан'] = 'Пожалуйста заполните анкету клиента в нетсторе'
        return client_connection_data

    with open(Pathes.switch_name_ip_dict_path, 'r') as switch_name_ip_data:
        switch_name_ip_dict = json.load(switch_name_ip_data)

    ip_mask_dictionary = load_clients_ip_gateway_mask_file()

    for i in range(len(client_ip_addresses)):
        for ip_zone in ip_mask_dictionary.keys():
            if client_ip_addresses[i] in ip_zone:
                client_connection_preferences = ip_mask_dictionary[ip_zone]
                client_gateway = client_connection_preferences[0]
                client_mask = client_connection_preferences[1]
                break
            else:
                client_gateway = 'None'
                client_mask = 'None'

        if not switches:
            client_connection_data[client_ip_addresses[i]] = ('None',
                                                          'None',
                                                          'None',
                                                          client_gateway,
                                                          client_mask,
                                                          'None',
                                                          'None',
                                                          'None'
                                                          )
            continue

        try:
            client_port = re.findall(r'#\d+', switches[i])
        except IndexError:
            client_port = re.findall(r'#\d+', switches[0])
            if not client_port:
                client_port = 'None'

        try:
            client_switch_name = switches[i][:switches[i].index('#')].strip()
        except IndexError:
            client_switch_name = switches[0][:switches[0].index('#')].strip()
        except ValueError:
            client_switch_name = switches[0].strip()
        if not client_switch_name:
            client_switch_name = 'None'

        try:
            client_switch_ip = switch_name_ip_dict[client_switch_name]
        except KeyError:
            client_switch_ip = 'None'

        client_switch_model = get_switch_name(client_switch_ip)

        cacti_client_port = remake_client_port_for_cacti_urls_dict(client_port[0])
        with open(Pathes.cacti_urls_path, 'r') as cacti_urls:
            cacti_urls_dict = json.load(cacti_urls)

        try:
            client_cacti_ulr = cacti_urls_dict[client_switch_ip][cacti_client_port]
        except (KeyError, IndexError):
            client_cacti_ulr = 'None'

        try:
            uplink_cacti_url = cacti_urls_dict[client_switch_ip]["Port uplink"]
        except (KeyError, IndexError):
            uplink_cacti_url = 'None'

        client_connection_data[client_ip_addresses[i]] = (client_switch_name,
                                                          client_switch_ip,
                                                          client_port[0],
                                                          client_gateway,
                                                          client_mask,
                                                          client_switch_model,
                                                          client_cacti_ulr,
                                                          uplink_cacti_url
                                                          )

    return client_connection_data


def collect_clients_data(url, login_, password, parse_level):
    browser = driver(url)
    try:
        login = browser.find_element(*NetstoreLocators.LOGIN)
        login.send_keys(login_)

        passwd = browser.find_element(*NetstoreLocators.PASSWD)
        passwd.send_keys(password)

        enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
        enter_button.click()

        open_all_clients_button = browser.find_element(*NetstoreLocators.GET_ALL_CLIENTS_PAGE)
        open_all_clients_button.click()

        active_clients = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST)
        terminated_clients = browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)

        client_objects = active_clients + terminated_clients

        if parse_level == 'local':
            active_client_name_url_dict = {}
            for active_client in active_clients:
                active_client_object = active_client.find_element_by_tag_name('a')
                active_client_name = strip_symbols_from_client_name(active_client_object.text)
                active_client_netstore_url = active_client_object.get_attribute("href").replace('_properties', '_client')
                active_client_name_url_dict[active_client_name] = active_client_netstore_url

            terminated_client_name_url_dict = {}
            for terminate_client in terminated_clients:
                terminate_client_object = terminate_client.find_element_by_tag_name('a')
                terminate_client_name = strip_symbols_from_client_name(terminate_client_object.text)
                terminate_client_netstore_url = terminate_client_object.get_attribute("href").replace('_properties', '_client')
                terminated_client_name_url_dict[terminate_client_name] = terminate_client_netstore_url

            return active_client_name_url_dict, terminated_client_name_url_dict

        elif parse_level == 'total':
            clients_netstore_name_url_list = []
            for client in client_objects:
                client_object = client.find_element_by_tag_name('a')

                client_name = strip_symbols_from_client_name(client_object.text)
                client_netstore_url = client_object.get_attribute("href").replace('_properties', '_client')

                clients_netstore_name_url_list.append((client_name, client_netstore_url))

        elif parse_level == 'closed':
            clients_netstore_name_url_list = []
            closed_clients = browser.find_elements(*NetstoreLocators.GET_ALL_CLOSED_CLIENTS_LIST)
            for closed_client in closed_clients:
                closed_client_object = closed_client.find_element_by_tag_name('a')

                closed_client_name = strip_symbols_from_client_name(closed_client_object.text)
                closed_client_netstore_url = closed_client_object.get_attribute("href").replace('_properties', '_client')
                clients_netstore_name_url_list.append((closed_client_name, closed_client_netstore_url))

            update_closed_clinents_name_url_dict(url, clients_netstore_name_url_list)

        clients_database = {}
        for client in clients_netstore_name_url_list:
            client_data = get_client_data(browser, client[1])

            client_name = client[0]
            client_tel = client_data[0]
            client_email = client_data[1]
            client_physical_address = client_data[2]
            client_physical_address_notes = client_data[3]

            if parse_level == 'closed':
                client_is_active = 'Выбывший'
            else:
                client_is_active = client_data[4]

            client_is_converter = client_data[5]
            client_manager = client_data[6]
            client_notes = client_data[7]
            client_connection_data = client_data[8]
            client_netstore_url = client[1]
            client_contracts = client_data[10]

            clients_database[client_name] = (
                client_tel,
                client_email,
                client_physical_address,
                client_physical_address_notes,
                client_is_active,
                client_is_converter,
                client_manager,
                client_notes,
                client_connection_data,
                client_netstore_url,
                client_contracts
            )

        return clients_database

    finally:
        browser.quit()


def get_client_data(browser, client_netstore_url):
    try:
        browser.get(client_netstore_url)
    except TimeoutException:
        browser.quit()
        time.sleep(300)
        browser = netstore_authorisation(client_netstore_url)
    except MaxRetryError:
        time.sleep(300)
        browser = netstore_authorisation(client_netstore_url)

    try:
        client_physical_address = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS).text
        client_physical_address_notes = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS_NOTES).text
    except NoSuchElementException:
        client_physical_address = None
        client_physical_address_notes = None

    try:
        client_tel = browser.find_element(*NetstoreClientPageLocators.TEL).get_attribute("value")
    except NoSuchElementException:
        client_tel = None

    try:
        client_email = browser.find_element(*NetstoreClientPageLocators.EMAIL).get_attribute("value")
    except NoSuchElementException:
        client_email = None

    try:
        client_is_active = browser.find_element(*NetstoreClientPageLocators.IS_ACTIVE).text
    except NoSuchElementException:
        client_is_active = None

    try:
        client_is_converter = 'НЕТ' if browser.find_element(*NetstoreClientPageLocators.IS_CONVERTER).get_attribute("checked") == None else 'ЕСТЬ'
    except NoSuchElementException:
        client_is_converter = None

    try:
        client_manager = get_manager_info(browser.find_element(*NetstoreClientPageLocators.MANAGER).get_attribute("value"))
    except NoSuchElementException:
        client_manager = None

    if client_manager == None:
        try:
            client_manager = get_manager_info(browser.find_element(*NetstoreClientPageLocators.MANAGER_2).get_attribute("value"))
        except NoSuchElementException:
            client_manager = None
    try:
        client_notes = browser.find_element(*NetstoreClientPageLocators.NOTES).text
    except NoSuchElementException:
        client_notes = 'None'

    client_connection_data = get_ipaddr_and_switch_name_and_port_from_client_note(browser, client_notes)

    client_contracts = get_client_contracts(browser, client_netstore_url)

    client_data = (
            client_tel,
            client_email,
            client_physical_address,
            client_physical_address_notes,
            client_is_active,
            client_is_converter,
            client_manager,
            client_notes,
            client_connection_data,
            client_netstore_url,
            client_contracts)

    return client_data


def update_clients_data(parse_level):

    if parse_level == 'local':
        update_clients_ip_gateway_mask_file()

        active_client_name_url_dict, terminated_client_name_url_dict = collect_clients_data(confidential.NetstoreLoginData.netstore1_url,
                                            confidential.NetstoreLoginData.netstore1_login,
                                            confidential.NetstoreLoginData.netstore_passwd,
                                            parse_level)

        active_client_name_url_dict_from_netstore2, terminated_client_name_url_dict_from_netstore2 = collect_clients_data(
            confidential.NetstoreLoginData.netstore2_url,
            confidential.NetstoreLoginData.netstore2_login,
            confidential.NetstoreLoginData.netstore_passwd,
            parse_level)

        active_client_name_url_dict.update(active_client_name_url_dict_from_netstore2)
        terminated_client_name_url_dict.update(terminated_client_name_url_dict_from_netstore2)
        process_turned_on_clients(active_client_name_url_dict, terminated_client_name_url_dict)

    elif parse_level == 'total':

        if ping_status(CactiLoginData.cacti_url[7:23]):
            update_switch_name_ip_file()

        clients_data = collect_clients_data(confidential.NetstoreLoginData.netstore1_url,
                                            confidential.NetstoreLoginData.netstore1_login,
                                            confidential.NetstoreLoginData.netstore_passwd,
                                            parse_level)

        clients_data.update(collect_clients_data(confidential.NetstoreLoginData.netstore2_url,
                                                 confidential.NetstoreLoginData.netstore2_login,
                                                 confidential.NetstoreLoginData.netstore_passwd,
                                                 parse_level))

        with open(Pathes.closed_clients_path, 'r') as closed_clients_data:
            closed_clients_dict = json.load(closed_clients_data)

        clients_data.update(closed_clients_dict)

        with open(Pathes.clients_path, 'w') as dict_with_clients:
            json.dump(clients_data, dict_with_clients, indent=2, sort_keys=True, ensure_ascii=False)

        update_client_ip_name_dict()
        update_client_contract_name_dict()

    elif parse_level == 'closed':
        closed_clients_dict = collect_clients_data(confidential.NetstoreLoginData.netstore1_url,
                                            confidential.NetstoreLoginData.netstore1_login,
                                            confidential.NetstoreLoginData.netstore_passwd,
                                            parse_level)

        closed_clients_dict.update(collect_clients_data(confidential.NetstoreLoginData.netstore2_url,
                                                 confidential.NetstoreLoginData.netstore2_login,
                                                 confidential.NetstoreLoginData.netstore_passwd,
                                                 parse_level))

        with open(Pathes.closed_clients_path, 'w') as closed_clients_data:
            json.dump(closed_clients_dict, closed_clients_data, indent=2, sort_keys=True, ensure_ascii=False)