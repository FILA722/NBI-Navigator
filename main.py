from parsers import update_clients_database
from parsers import switch_parse
from search_engine import search_engine
import os
import time

def console_output(client_name, client_data):
    print(f'-' * 100)
    print(f'| Имя клиента ', ' ' * (30 - len('Имя клиента')), '|', client_name.upper(), ' ' * (60 - len(client_name)), '|')
    print(f'-' * 100)
    print(f'| Контактный телефон ', ' ' * (30 - len('Контактный телефон')), '|', client_data[0], ' ' * (60 - len(client_data[0])), '|')
    print(f'-' * 100)
    print(f'| Email ', ' ' * (30 - len('Email')), '|', client_data[1].lower(), ' ' * (60 - len(client_data[1])), '|')
    print(f'-' * 100)
    print(f'| Состояние клиента ', ' ' * (30 - len('Состояние клиента')), '|', client_data[4].upper(), ' ' * (60 - len(client_data[4])), '|')
    print(f'-' * 100)
    print(f'| Наличие конвертора ', ' '*(30 - len('Наличие конвертора')),'|',client_data[5], ' '*(60 - len(client_data[5])),'|')
    print(f'-' * 100)
    print(f'| Скорость ', ' ' * (30 - len('Скорость')), '|', f'{client_data[6]} Kb/sec', ' ' * (60 - len(f'{client_data[6]} Kb/sec')), '|')
    print(f'-' * 100)
    if client_data[-2]:
        for count in range(len(client_data[-2])):
            client_ip_address = list(client_data[-2].keys())[count]
            gateway = client_data[-2][client_ip_address][-3]
            mask = client_data[-2][client_ip_address][-2]
            switch_name = client_data[-2][client_ip_address][0]
            switch_model = client_data[-2][client_ip_address][5]
            switch_port = client_data[-2][client_ip_address][2][1:]
            switch_ip_address = client_data[-2][client_ip_address][1]

            switch_ip_str = f'http://{switch_ip_address}/' if switch_model != 'huawei' else switch_ip_address
            answer_connection = f'IP: {client_ip_address} | GW: {gateway} | MASK: {mask}'
            answer_connection_to = f'{switch_name}#{switch_port} -> {switch_ip_str} {switch_model}'

            print(f'| Подключение {count + 1} ', ' ' * (30 - len(f'Подключение {count + 1}')), '|', f'{answer_connection_to}', ' ' * (60 - len(f'{answer_connection_to}')), '|')
            print(f'- ' * 50)

            if switch_model == 'huawei':
                port_condition, saved_mac_address, current_mac_address, port_errors = switch_parse.parse_huawei(switch_ip_address, client_ip_address, switch_port)

            print(f'| Параметры подключения ', ' ' * (30 - len(f'Параметры подключения')), '|', f'{answer_connection}', ' ' * (60 - len(f'{answer_connection}')), '|')
            print(f'-' * 100)
    print(f'| Netstore ', ' ' * (30 - len('Netstore')), '|', f'{client_data[-1]}', ' ' * (60 - len(f'{client_data[-1]}')), '|')

def main():
    if not os.path.isfile('search_engine/clients.json'):
        print('Обновление базы данных, это может занять около 4-х минут...')
        start = time.time()
        update_clients_database.update_clients_data()
        print(f'-=База данных обновлена=-\nВремя обновления: {time.time() - start} сек.')

    while True:
        print('=' * 100)
        client = input('Введите имя клиента:').lower()
        search_result = search_engine.search(client)

        if search_result == False:
            print('КЛИЕНТ НЕ НАЙДЕН')
            continue
        elif str(search_result.__class__) == "<class 'tuple'>":
            client_name = search_result[0]
            client_data = search_result[1]
            console_output(client_name, client_data)
        else:
            print('Выберите клиента:')
            print('-' * 100)
            for client_name in search_result:
                print(client_name)

main()
