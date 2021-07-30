import parse_netstore
from client_description import Client
import json
import os

def main():
    client = input('Введите имя клиента:')
    if os.path.isfile('clients.json'):
        parse_netstore.update_clients()

    with open('clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
    try:
        print(client, clients[client])
    except KeyError:
        print(f"Client doesn't found")

# test()
main()
# parse_netstore.update_clients()