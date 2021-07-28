import parse_netstore
import json
import os

def main():
    client = input('Введите имя клиента:')
    if not os.path.isfile('clients.json'):
        parse_netstore.update_clients()

    with open('clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())

    try:
        print(client, clients[client])
    except KeyError:
        print(f"Client doesn't found")
# main()
parse_netstore.update_clients()