from search_engine.transliterations import Transliterations
from debugers.check_ping_status import ping_status
from parsers import switch_parse
# from parsers.parse_cacti import save_cacti_client_image_to_file
from parsers.update_clients_database import get_client_data, remake_client_port_for_cacti_urls_dict
from client_managment.login_into_netstore import netstore_authorisation
import logging
import json
import re
import time


def concatenate_local_db():
    with open('search_engine/active_clients_name_url_data.json') as active_clients:
        active_clients_dict = json.loads(active_clients.read())

    with open('search_engine/terminated_clients_name_url_data.json') as terminated_clients:
        terminated_clients_dict = json.loads(terminated_clients.read())

    active_clients_dict.update(terminated_clients_dict)

    return active_clients_dict.keys()


def get_cacti_links(switch_client_cacti_id, switch_client_uplink_id):
    graph_end = int(time.time())
    graph_start = graph_end - 86400

    client_id = switch_client_cacti_id[6:]
    uplink_id = switch_client_uplink_id[6:]

    switch_client_cacti_link = f'http://cacti.nbi.com.ua/cacti/graph_image.php?local_graph_id={client_id}&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={graph_start}&graph_end={graph_end}'
    switch_uplink_cacti_link = f'http://cacti.nbi.com.ua/cacti/graph_image.php?local_graph_id={uplink_id}&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={graph_start}&graph_end={graph_end}'

    return switch_client_cacti_link, switch_uplink_cacti_link


def request_to_db(request):
    if request == 'get_clients_names':
        clients_names = concatenate_local_db()
        return clients_names
    else:
        with open('search_engine/clients.json', 'r') as dict_with_clients:
            clients = json.loads(dict_with_clients.read())
            try:
                return clients[request]
            except KeyError:
                clients_names = concatenate_local_db()
                return clients_names[request]


def transliteration(client):
    translations = [client]
    for dictionary in Transliterations.dictionaries:
        for client in translations:
            word = ''
            for letter in client:
                try:
                    word += dictionary[letter]
                except KeyError:
                    word += letter
            if word not in translations and word != client:
                translations.append(word)
    return translations


def get_coincidence_names(client):
    client = client.lower()
    search_names = transliteration(f'{client}')
    clients_names = request_to_db('get_clients_names')

    coincidence_names = []
    for client_name in clients_names:
        for search_name in search_names:
            pattern = f'{search_name.lower()}[  \-\'\w]*'
            client_name_parts = client_name.split(' ')
            for client_name_part in client_name_parts:
                if re.match(pattern, client_name_part):
                    coincidence_names.append(client_name)

    if not coincidence_names:
        return False
    else:
        return coincidence_names


def get_full_client_data(client_name):
    client_data = request_to_db(client_name)
    logging.info(f'Найден клиент: {client_name}')

    if str(type(client_data)) == "<class 'str'>":
        client_url = client_data
        browser = netstore_authorisation(client_url)
        client_data = get_client_data(browser, client_url)

    client_connection_data = client_data[8]

    for client_ip_address in client_connection_data.keys():
        if client_ip_address == 'IP не указан' or client_connection_data[client_ip_address][0] == 'Пожалуйста пропишите имя свича и порт клиента в Нетсторе' :
            return client_name, client_data
        else:
            switch_client_cacti_id = client_connection_data[client_ip_address][6]
            switch_client_uplink_id = client_connection_data[client_ip_address][7]

            switch_client_cacti_link, switch_uplink_cacti_link = get_cacti_links(switch_client_cacti_id, switch_client_uplink_id)

            client_connection_data[client_ip_address][6] = switch_client_cacti_link
            client_connection_data[client_ip_address][7] = switch_uplink_cacti_link

            switch_ip_address = client_connection_data[client_ip_address][1]
            if not ping_status(switch_ip_address):
                data_from_switch = ['НЕТ СОЕДИНЕНИЯ СО СВИЧЕМ']
            else:
                switch_port = client_connection_data[client_ip_address][2][1:]
                data_from_switch = []

                if client_connection_data[client_ip_address][5] == 'huawei':
                    logging.info(f'Установка телнет-сессии с huawei {switch_ip_address}, Порт: {switch_port}, Клиент: {client_ip_address}')
                    data_from_switch = switch_parse.parse_huawei(switch_ip_address, client_ip_address, switch_port)
                elif client_connection_data[client_ip_address][5] == 'zyxel':
                    logging.info(f'Установка телнет-сессии с zyxel {switch_ip_address}, Порт: {switch_port}, Клиент: {client_ip_address}')
                    data_from_switch = switch_parse.parse_zyxel(switch_ip_address, client_ip_address, switch_port)

        if data_from_switch:
            if data_from_switch[0] == 'НЕТ СОЕДИНЕНИЯ СО СВИЧЕМ':
                client_connection_data[client_ip_address].append(data_from_switch[0])
            else:
                client_connection_data[client_ip_address] += data_from_switch
            logging.info('Данные со свича успешно добавлены в данные по клиенту')

        client_connection_data[client_ip_address] += (ping_status(client_ip_address), ping_status(switch_ip_address))

    return client_name, client_data





