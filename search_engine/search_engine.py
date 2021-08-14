from search_engine.transliterations import Transliterations
from parsers import switch_parse
import json
import re

with open('search_engine/clients.json', 'r') as dict_with_clients:
    clients = json.loads(dict_with_clients.read())
    clients_names = clients.keys()

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

def search(client):
    search_names = transliteration(client)

    coincidence_names = []
    for client_name in clients_names:
        for search_name in search_names:
            pattern = f'{search_name}[  \-\'\w]*'

            if re.match(pattern, client_name):
                coincidence_names.append(client_name)

    if not coincidence_names:
        return False

    elif len(coincidence_names) == 1:
        client_connection_data = clients[coincidence_names[0]][8]

        for client_ip_address in client_connection_data.keys():
            if client_connection_data[client_ip_address][5] == 'huawei':
                print(f'Сбор данных о подключении клиента {coincidence_names[0].upper()}...')

                switch_ip_address = client_connection_data[client_ip_address][1]
                switch_port = client_connection_data[client_ip_address][2][1:]

                data_from_switch = switch_parse.parse_huawei(switch_ip_address, client_ip_address, switch_port)

                client_connection_data[client_ip_address] += data_from_switch

        return coincidence_names[0], clients[coincidence_names[0]]

    return coincidence_names