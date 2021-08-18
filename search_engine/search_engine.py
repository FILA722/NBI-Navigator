from search_engine.transliterations import Transliterations
from check_ping_status import ping_status
from parsers import switch_parse
import logging
import json
import re

with open('search_engine/clients.json', 'r') as dict_with_clients:
    clients = json.loads(dict_with_clients.read())
    clients_names = clients.keys()
    logging.info('Файл с БД клиентов открыт для чтения')

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


def search(client):
    search_names = transliteration(client)

    coincidence_names = []
    for client_name in clients_names:
        for search_name in search_names:
            pattern = f'{search_name}[  \-\'\w]*'

            if re.match(pattern, client_name):
                coincidence_names.append(client_name)

    if not coincidence_names:
        logging.info(f'Клиент не найден')
        return False

    elif len(coincidence_names) == 1:
        logging.info(f'Найден клиент: {coincidence_names[0]}')
        client_connection_data = clients[coincidence_names[0]][8]

        for client_ip_address in client_connection_data.keys():
            print(f'Сбор данных о подключении клиента {coincidence_names[0].upper()}...')
            logging.info(f'Сбор данных о подключении клиента {coincidence_names[0].upper()}')

            switch_ip_address = client_connection_data[client_ip_address][1]
            if not ping_status(switch_ip_address):
                data_from_switch = 'НЕТ СОЕДИНЕНИЯ СО СВИЧЕМ'
            else:
                switch_port = client_connection_data[client_ip_address][2][1:]
                data_from_switch = []
                try:
                    if client_connection_data[client_ip_address][5] == 'huawei':
                        logging.info(f'Установка телнет-сессии с huawei {switch_ip_address}, Порт: {switch_port}, Клиент: {client_ip_address}')
                        data_from_switch = switch_parse.parse_huawei(switch_ip_address, client_ip_address, switch_port)
                    elif client_connection_data[client_ip_address][5] == 'zyxel':
                        logging.info(f'Установка телнет-сессии с zyxel {switch_ip_address}, Порт: {switch_port}, Клиент: {client_ip_address}')
                        data_from_switch = switch_parse.parse_zyxel(switch_ip_address, client_ip_address, switch_port)
                except EOFError:
                    logging.info('Не получилось собрать информацию')
                    data_from_switch = ['Не получилось собрать информацию']

            if data_from_switch:
                if data_from_switch == 'НЕТ СОЕДИНЕНИЯ СО СВИЧЕМ':
                    client_connection_data[client_ip_address].append(data_from_switch)
                else:
                    client_connection_data[client_ip_address] += data_from_switch
                logging.info('Данные со свича успешно добавлены в данные по клиенту')
        print(client_connection_data[client_ip_address])
        return coincidence_names[0], clients[coincidence_names[0]]

    return coincidence_names