import json
import re

with open('clients.json', 'r') as dict_with_clients:
    clients = json.loads(dict_with_clients.read())
    clients_names = clients.keys()

def search(client):
    coincidence_names = []
    pattern = f'{client}[ \w]+'
    for client_name in clients_names:
        if re.match(pattern, client_name):
            coincidence_names.append(client_name)
    if len(coincidence_names) == 1:
        client_object = clients[coincidence_names[0]]
        client_data = (
            f'Клиент : {coincidence_names[0]}',
            f'Контактный телефон : {client_object[0]}',
            f'Email : {client_object[1].lower()}',
            f'Бизнесс центр : {client_object[2]}',
            f'Заметки бизнесс центра: {client_object[3]}',
            f'Состояние клиента : {client_object[4]}',
            f'Наличие конвертора : {client_object[5]}',
            f'Скорость : {client_object[6]} Kb/sec',
            f'Заметки : {client_object[7]}',
            f'Параметры подключения : {client_object[8]}',
            f'Ссылка на клиента в Нетсторе : {client_object[9]}')
        return client_data
    return coincidence_names