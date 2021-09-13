import json


def check():
    with open('search_engine/clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
        clients_names = clients.keys()
        for client_name in clients_names:
            if clients[client_name][2] == 'Бизнес-центр Новозабарська, 2/6':
                continue
            client_data = clients[client_name][8]
            for client_ip_address in client_data:
                if client_data[client_ip_address][0] == 'Пожалуйста пропишите имя свича и порт клиента в Нетсторе':
                    print(client_name)
                    print(clients[client_name][-1])
                    print('-' * 60)