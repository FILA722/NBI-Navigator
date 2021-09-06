from parsers import parse_cacti, parse_zones
from parsers import confidential
from start_browser import driver
from check_ping_status import ping_status
from parsers.locators import NetstoreLocators, NetstoreClientPageLocators
from selenium.common.exceptions import NoSuchElementException
import logging
import json
import re

logging.basicConfig(filename="logs.txt", level=logging.INFO)


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
    for i in range(len(client_ip_addresses)):
        if not switches:
            client_connection_data[client_ip_addresses[i]] = 'Пожалуйста пропишите имя свича и порт клиента в Нетсторе'
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

        client_switch_model = get_switch_name(client_switch_ip)

        for ip_zone in ip_mask_dictionary.keys():
            if client_ip_addresses[i] in ip_zone:
                client_connection_preferences = ip_mask_dictionary[ip_zone]

        try:
            client_connection_data[client_ip_addresses[i]] = (client_switch_name,
                                                              client_switch_ip,
                                                              client_port[0],
                                                              client_connection_preferences[0],
                                                              client_connection_preferences[1],
                                                              client_switch_model)
        except IndexError:
            client_connection_preferences = {'Ошибка в данных подключения, проверьте Нетсторе'}
            logging.warning('Ошибка в данных подключения, проверьте Нетсторе')
        except UnboundLocalError:
            client_connection_preferences = {f'Ошибка в данных подключения, проверьте Нетсторе {client_ip_addresses[i]}'}
            logging.warning(f'Ошибка в данных подключения, проверьте Нетсторе {client_ip_addresses[i]}')

    return client_connection_data


def collect_clients_data(url, login_, password):
    switch_name_ip_dict = parse_cacti.main()
    clients_ip_gateway_mask_dict = parse_zones.get_zone_data()
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

        client_objects = browser.find_elements(*NetstoreLocators.GET_ALL_ACTIVE_CLIENTS_LIST) + browser.find_elements(*NetstoreLocators.GET_ALL_TERMINATED_CLIENTS_LIST)
        logging.info("Сбор клиент-объектов прошел успешно")

        clients_netstore_name_url_list = []

        for client in client_objects:
            client_object = client.find_element_by_tag_name('a')
            client_name = client_object.text
            client_netstore_url = client_object.get_attribute("href").replace('_properties', '_client')
            clients_netstore_name_url_list.append((client_name, client_netstore_url))

        clients_database = {}
        logging.info("Начало сбора данных всех клиентов с нетсторе")
        for client in clients_netstore_name_url_list:
            client_name = client[0].lower()
            client_netstore_url = client[1]

            if client_name in confidential.UnprocessedNames.not_processed_clients:
                continue

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
            client_speed = browser.find_element(*NetstoreClientPageLocators.SPEED).get_attribute("value")
            client_notes = browser.find_element(*NetstoreClientPageLocators.NOTES).text
            client_connection_data = get_ipaddr_and_switch_name_and_port_from_client_note(browser, client_notes, switch_name_ip_dict,  clients_ip_gateway_mask_dict)

            clients_database[client_name] = (
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
    finally:
        browser.quit()
    logging.info("Конец сбора данных с нетсторе")
    return clients_database


def update_clients_data():
    clients_data = {}

    logging.info("Обновление нетсторе 1")
    if not ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]):
        print('!!!Нет соединения с Нетсторе 1!!!')
        logging.info("!!!Нет соединения с Нетсторе 1!!!")
    else:
        clients_data.update(collect_clients_data(confidential.NetstoreLoginData.netstore1_url,
                                            confidential.NetstoreLoginData.netstore1_login,
                                            confidential.NetstoreLoginData.netstore_passwd))
        logging.info("Обновление нетсторе 1 прошел успешно")

    if not ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):
        print('!!!Нет соединения с Нетсторе 2!!!')
        logging.info("!!!Нет соединения с Нетсторе 2!!!")
    else:
        logging.info("Обновление нетсторе 2")
        clients_data.update(collect_clients_data(confidential.NetstoreLoginData.netstore2_url,
                                                 confidential.NetstoreLoginData.netstore2_login,
                                                 confidential.NetstoreLoginData.netstore_passwd))
        logging.info("Обновление нетсторе 2 прошел успешно")

    logging.info("Запись БД в clients.json")
    json_clients_dict = json.dumps(clients_data, indent=2, sort_keys=True, ensure_ascii=False)
    with open('search_engine/clients.json', 'w') as dict_with_clients:
        dict_with_clients.write(json_clients_dict)
    logging.info("*************** БД обновлена успешно ***************")

