import parse_netstore
from client_description import Client
import search_engine
import json
import os
import time

def update_database():
    clients = parse_netstore.update_clients()
    json_clients_dict = json.dumps(clients, indent=2, sort_keys=True, ensure_ascii=False)
    with open('clients.json', 'w') as dict_with_clients:
        dict_with_clients.write(json_clients_dict)

def main():
    if not os.path.isfile('clients.json'):
        update_database()

    clients_name = []
    while len(clients_name) != 1:
        print('==========================================')
        client = input('Введите имя клиента:').lower()
        clients_name = search_engine.search(client)
        if str(clients_name.__class__) == "<class 'tuple'>":
            break
        for client_name in clients_name:
            print(client_name)

    for field in clients_name:
        print(field)
        print('-------------------------------------------')
        # for client_name in clients_name

    # with open('clients.json', 'r') as dict_with_clients:
    #     clients = json.loads(dict_with_clients.read())
    #     clients_names = clients.keys()
    #     client = ''
    #     while client not in clients_names:
    #         client = input('Введите имя клиента:').lower()
    #
    #         for client_name in clients_names:
    #             if client in client_name:
    #                 print(client_name)

        # print(client, clients[client], end='\n')

main()
