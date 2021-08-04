import parse_netstore
import parse_switch
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

    while True:
        print('==========================================')
        client = input('Введите имя клиента:').lower()
        search_result = search_engine.search(client)

        if str(search_result.__class__) == "<class 'tuple'>":
            client_name = search_result[0]
            client_data = search_result[1]
            break

        print('Выберите клиента:')
        for client_name in search_result:
            print(client_name)
    print(client_name)
    # print(client_data[-2])
    client_switch_data = parse_switch.main(client_data[-2])
    print(client_switch_data)
    # client_data = (
    #     f'Клиент : {coincidence_names[0]}',
    #     f'Контактный телефон : {client_object[0]}',
    #     f'Email : {client_object[1].lower()}',
    #     f'Бизнесс центр : {client_object[2]}',
    #     f'Заметки бизнесс центра: {client_object[3]}',
    #     f'Состояние клиента : {client_object[4]}',
    #     f'Наличие конвертора : {client_object[5]}',
    #     f'Скорость : {client_object[6]} Kb/sec',
    #     f'Заметки : {client_object[7]}',
    #     f'Параметры подключения : {client_object[8]}',
    #     f'Ссылка на клиента в Нетсторе : {client_object[9]}')
    # connection_data = parse_switch.main(client_info[-2])
    # for field in connection_data:
    #     print(field)
    #     print('-------------------------------------------')
main()
