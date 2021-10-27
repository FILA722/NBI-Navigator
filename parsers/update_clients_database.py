from parsers import parse_cacti, parse_zones
from parsers import confidential
from start_browser import driver
from parsers.locators import NetstoreLocators, NetstoreClientPageLocators
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import logging
import json
import re

logging.basicConfig(filename="logs.txt", level=logging.INFO)

def get_manager_info(name):
    return confidential.MANAGERS.manager_dictionary[name]

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
    return 'Модель свича не найдена'


def get_ipaddr_and_switch_name_and_port_from_client_note(browser, note, switch_name_ip_dict, ip_mask_dictionary):
    client_ip_addresses = tuple(ip_address.text for ip_address in browser.find_elements(*NetstoreClientPageLocators.IP_ADDRESSES))
    switches = re.findall(r'==[A-Za-z0-9-_\/. #]+==', note)
    switches = tuple(switch.strip('==') for switch in switches)

    client_connection_data = {}

    if not client_ip_addresses:
        client_connection_data['IP не указан'] = 'Пожалуйста заполните анкету клиента в нетсторе'
        return client_connection_data

    for i in range(len(client_ip_addresses)):

        for ip_zone in ip_mask_dictionary.keys():
            if client_ip_addresses[i] in ip_zone:
                try:
                    client_connection_preferences = ip_mask_dictionary[ip_zone]
                    client_gateway = client_connection_preferences[0]
                    client_mask = client_connection_preferences[1]
                except (IndexError, UnboundLocalError) :
                    logging.warning(f'Ошибка в данных подключения, проверьте Нетсторе {client_ip_addresses[i]}')
                break
            else:
                client_gateway = 'не найден'
                client_mask = 'не найден'

        if not switches:
            client_connection_data[client_ip_addresses[i]] = ['Пожалуйста пропишите имя свича и порт клиента в Нетсторе',
                                                              client_gateway,
                                                              client_mask]
            continue

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

        client_switch_model = get_switch_name(client_switch_ip)

        client_connection_data[client_ip_addresses[i]] = (client_switch_name,
                                                          client_switch_ip,
                                                          client_port[0],
                                                          client_gateway,
                                                          client_mask,
                                                          client_switch_model)

    return client_connection_data


def collect_clients_data(url, login_, password, parse_level):
    try:
        logging.info("Запуск браузера")
        browser = driver(url)

        login = browser.find_element(*NetstoreLocators.LOGIN)
        login.send_keys(login_)

        passwd = browser.find_element(*NetstoreLocators.PASSWD)
        passwd.send_keys(password)

        enter_button = browser.find_element(*NetstoreLocators.ENTER_BUTTON)
        enter_button.click()

        open_all_clients_button = browser.find_element(*NetstoreLocators.GET_ALL_CLIENTS_PAGE)
        open_all_clients_button.click()
        logging.info("Авторизация в нетсторе прошла успешно")

        active_clients = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST)
        terminated_clients = browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
        client_objects = active_clients + terminated_clients
        logging.info("Сбор клиент-объектов прошел успешно")

        if parse_level == 'local':
            active_client_name_url_dict = {}
            for active_client in active_clients:
                active_client_object = active_client.find_element_by_tag_name('a')
                active_client_name = active_client_object.text
                active_client_netstore_url = active_client_object.get_attribute("href").replace('_properties', '_client')
                active_client_name_url_dict[active_client_name] = active_client_netstore_url

            terminated_client_name_url_dict = {}
            for terminate_client in terminated_clients:
                terminate_client_object = terminate_client.find_element_by_tag_name('a')
                terminate_client_name = terminate_client_object.text
                terminate_client_netstore_url = terminate_client_object.get_attribute("href").replace('_properties', '_client')
                terminated_client_name_url_dict[terminate_client_name] = terminate_client_netstore_url

            return active_client_name_url_dict, terminated_client_name_url_dict

        switch_name_ip_dict = parse_cacti.main()
        clients_ip_gateway_mask_dict = parse_zones.get_zone_data()

        clients_netstore_name_url_list = []

        for client in client_objects:
            client_object = client.find_element_by_tag_name('a')
            client_name = client_object.text
            client_netstore_url = client_object.get_attribute("href").replace('_properties', '_client')
            clients_netstore_name_url_list.append((client_name, client_netstore_url))

        clients_database = {}
        logging.info("Начало сбора данных всех клиентов с нетсторе")
        for client in clients_netstore_name_url_list:
            client_name = ((client[0].lower()).replace('(', '')).replace(')', '')
            client_netstore_url = client[1]

            browser.get(client_netstore_url)

            try:
                client_physical_address = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS).text
                client_physical_address_notes = browser.find_element(*NetstoreClientPageLocators.PHYSICAL_ADDRESS_NOTES).text
            except NoSuchElementException:
                client_physical_address = None
                client_physical_address_notes = None

            if client_physical_address in confidential.UnprocessedNames.not_processed_bussines_centres:
                continue

            client_tel = browser.find_element(*NetstoreClientPageLocators.TEL).get_attribute("value")
            client_email = browser.find_element(*NetstoreClientPageLocators.EMAIL).get_attribute("value")
            client_is_active = browser.find_element(*NetstoreClientPageLocators.IS_ACTIVE).text
            client_is_converter = 'НЕТ' if browser.find_element(*NetstoreClientPageLocators.IS_CONVERTER).get_attribute("checked") == None else 'ЕСТЬ'

            try:
                client_manager = get_manager_info(browser.find_element(*NetstoreClientPageLocators.MANAGER).get_attribute("value"))
            except NoSuchElementException:
                client_manager = get_manager_info(browser.find_element(*NetstoreClientPageLocators.MANAGER_2).get_attribute("value"))

            client_notes = browser.find_element(*NetstoreClientPageLocators.NOTES).text
            client_connection_data = get_ipaddr_and_switch_name_and_port_from_client_note(browser, client_notes, switch_name_ip_dict,  clients_ip_gateway_mask_dict)

            clients_database[client_name] = (
                    client_tel,
                    client_email,
                    client_physical_address,
                    client_physical_address_notes,
                    client_is_active,
                    client_is_converter,
                    # client_speed,
                    client_manager,
                    client_notes,
                    client_connection_data,
                    client_netstore_url)
    finally:
        browser.quit()
    logging.info("Конец сбора данных с нетсторе")
    return clients_database


def update_clients_data(parse_level):

    if parse_level == 'local':
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

        with open('search_engine/active_clients_name_url_data.json', 'r') as active_client_name_url_data:
            active_client_name_url_dict_old = json.load(active_client_name_url_data)

        if active_client_name_url_dict_old != active_client_name_url_dict:
            with open('search_engine/active_clients_name_url_data.json', 'w') as active_client_name_url_data:
                json.dump(active_client_name_url_dict, active_client_name_url_data, indent=2, sort_keys=True, ensure_ascii=False)

            with open('search_engine/terminated_clients_name_url_data.json', 'r') as terminated_client_name_url_data:
                terminated_client_name_url_dict_old = json.load(terminated_client_name_url_data)

            if terminated_client_name_url_dict_old != terminated_client_name_url_dict:
                turned_on_clients = terminated_client_name_url_dict_old.keys() - terminated_client_name_url_dict.keys()

                check_client_balance_date = str(datetime.now() + timedelta(days=3))

                with open('search_engine/check_client_balance.txt', 'a') as check_clients:
                    for turned_on_client in turned_on_clients:
                        check_clients.write(f'{turned_on_client} | {check_client_balance_date} | {terminated_client_name_url_dict_old[turned_on_client]} \n')

                with open('search_engine/terminated_clients_name_url_data.json', 'w') as terminated_client_name_url_data:
                    json.dump(terminated_client_name_url_dict, terminated_client_name_url_data, indent=2, sort_keys=True, ensure_ascii=False)

    elif parse_level == 'total':
        clients_data = collect_clients_data(confidential.NetstoreLoginData.netstore1_url,
                                            confidential.NetstoreLoginData.netstore1_login,
                                            confidential.NetstoreLoginData.netstore_passwd,
                                            parse_level)

        clients_data.update(collect_clients_data(confidential.NetstoreLoginData.netstore2_url,
                                                 confidential.NetstoreLoginData.netstore2_login,
                                                 confidential.NetstoreLoginData.netstore_passwd,
                                                 parse_level))

        with open('search_engine/clients.json', 'w') as dict_with_clients:
            json.dump(clients_data, dict_with_clients, indent=2, sort_keys=True, ensure_ascii=False)

