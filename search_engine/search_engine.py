from search_engine.transliterations import Transliterations
from debugers.check_ping_status import ping_status
from parsers import switch_parse
import logging
import json
import re


def request_to_db(request):
    with open('search_engine/clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
        clients_names = clients.keys()
    if request == 'get_clients_names':
        return clients_names
    else:
        return clients[request]


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
    logging.info(f'Составлен список для поиска в БД: {translations}')
    return translations


def get_coincidence_names(client):
    search_names = transliteration(f'{client}')

    coincidence_names = []
    clients_names = request_to_db('get_clients_names')
    for client_name in clients_names:
        for search_name in search_names:
            pattern = f'{search_name}[  \-\'\w]*'

            if re.match(pattern, client_name):
                coincidence_names.append(client_name)

    if not coincidence_names:
        logging.info(f'Клиент не найден')
        return False
    else:
        return coincidence_names


def get_full_client_data(client_name):
    client_data = request_to_db(client_name)
    logging.info(f'Найден клиент: {client_name}')

    client_connection_data = client_data[8]
    logging.info(f'Сбор данных о подключении клиента {client_name.upper()}')

    for client_ip_address in client_connection_data.keys():
        if client_ip_address == 'IP не указан' or client_connection_data[client_ip_address][0] == 'Пожалуйста пропишите имя свича и порт клиента в Нетсторе' :
            return client_name, client_data
        else:
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

        client_connection_data[client_ip_address] += [ping_status(client_ip_address), ping_status(switch_ip_address)]

    return client_name, client_data

