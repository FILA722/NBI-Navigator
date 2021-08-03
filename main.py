import parse_netstore
from client_description import Client
import json
import os
import time

def main():
    client = input('Введите имя клиента:')
    start = time.time()
    if os.path.isfile('clients.json'):
        clients = parse_netstore.update_clients()
        json_clients_dict = json.dumps(clients, indent=2, sort_keys=True, ensure_ascii=False)
        with open('clients.json', 'w') as dict_with_clients:
            dict_with_clients.write(json_clients_dict)

    middle = time.time()
    with open('clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
    end = time.time()
    print('parse time:', middle - start)
    print('record time:', end - middle)
    print('total time:', end - start)
    try:
        print(client, clients[client])
    except KeyError:
        print(f"Client doesn't found")

main()
