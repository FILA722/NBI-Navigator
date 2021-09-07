import logging

logging.info('Вывод данных в консоль')

def print_nbi_header():
    print('=' * 100)
    print(' ' * 40, '-=NBI-NAVIGATOR=-')
    print('=' * 100)


def console_output(client_name, client_data):
    left_field = 20
    right_field = 70
    total_width = 100
    print(f'-' * total_width)
    print(f'| Имя клиента ', ' ' * (left_field - len('Имя клиента')), '|', client_name.upper(), ' ' * (right_field - len(client_name)), '|')
    print(f'-' * total_width)
    print(f'| Контактный телефон ', ' ' * (left_field - len('Контактный телефон')), '|', client_data[0], ' ' * (right_field - len(client_data[0])), '|')
    print(f'-' * total_width)
    print(f'| Email ', ' ' * (left_field - len('Email')), '|', client_data[1].lower(), ' ' * (right_field - len(client_data[1])), '|')
    print(f'-' * total_width)
    print(f'| Состояние клиента ', ' ' * (left_field - len('Состояние клиента')), '|', client_data[4].upper(), ' ' * (right_field - len(client_data[4])), '|')
    print(f'-' * total_width)
    print(f'| Наличие конвертора ', ' '*(left_field - len('Наличие конвертора')),'|',client_data[5], ' '*(right_field - len(client_data[5])),'|')
    print(f'-' * total_width)
    print(f'| Скорость ', ' ' * (left_field - len('Скорость')), '|', f'{client_data[6]} Kb/sec', ' ' * (right_field - len(f'{client_data[6]} Kb/sec')), '|')
    print(f'-' * total_width)
    if client_data[-2]:
        for count in range(len(client_data[-2])):
            client_ip_address = list(client_data[-2].keys())[count]
            if client_data[-2][client_ip_address][-1] == 'Пожалуйста пропишите имя свича и порт клиента в Нетсторе':
                print(f'| Подключение {count + 1} ', ' ' * (left_field - len(f'Подключение {count + 1}')), '|', client_data[-2][client_ip_address][0], ' ' * (right_field - len(client_data[-2][client_ip_address][0])), '|')
                print(f'-' * total_width)
            elif client_data[-2][client_ip_address][-1] == 'НЕТ СОЕДИНЕНИЯ СО СВИЧЕМ':
                print(f'| Подключение {count + 1} ', ' ' * (left_field - len(f'Подключение {count + 1}')), '|', f'НЕТ СВЯЗИ С {client_data[-2][client_ip_address][0]}', ' ' * (right_field - len(client_data[-2][client_ip_address])), '|')
                print(f'-' * total_width)
            else:

                switch_name = client_data[-2][client_ip_address][0]
                switch_model = client_data[-2][client_ip_address][5]
                switch_port = client_data[-2][client_ip_address][2][1:]
                switch_ip_address = client_data[-2][client_ip_address][1]

                switch_ip_str = f'http://{switch_ip_address}/' if switch_model != 'huawei' else switch_ip_address

                answer_connection_to = f'{switch_name}#{switch_port} -> {switch_ip_str} {switch_model}'
                print(f'| Подключение {count + 1} ', ' ' * (left_field - len(f'Подключение {count + 1}')), '|', f'{answer_connection_to}', ' ' * (right_field - len(f'{answer_connection_to}')), '|')
                print(f'- ' * int(total_width / 2))

                if switch_model in ['huawei', 'zyxel']:
                    port_condition = client_data[-2][client_ip_address][6]
                    if port_condition == 'Не получилось собрать информацию':
                        print('| Cостояние порта: ', ' ' * (left_field - len(f'Cостояние порта:')), '|', port_condition, ' ' * (right_field - len(port_condition)), '|')
                    else:
                        saved_mac_address = client_data[-2][client_ip_address][7]
                        current_mac_address = client_data[-2][client_ip_address][8]
                        port_errors = client_data[-2][client_ip_address][9]

                        if current_mac_address == saved_mac_address:
                            port_status = f'   {port_condition.upper()}   |  MAC: {str(saved_mac_address)}  |  Errors: {str(port_errors)}'
                            print('| Cостояние порта: ', ' ' * (left_field - len(f'Cостояние порта:')), '|', port_status, ' ' * (right_field - len(port_status)), '|')
                        else:
                            port_status = f'   {str(port_condition.upper())}   | MAC прописан: {str(saved_mac_address)} | MAC на порту: {str(current_mac_address)} | Errors: {str(port_errors)}'
                            print(f'| Cостояние порта: ', ' ' * (left_field - len(f'Cостояние порта:')), '|', port_status, ' ' * (right_field - len(port_status)), '|')
                    print(f'- ' * int(total_width / 2))
                gateway = client_data[-2][client_ip_address][3]
                mask = client_data[-2][client_ip_address][4]
                answer_connection = f'IP: {client_ip_address} | GW: {gateway} | MASK: {mask}'
                print(f'| Параметры подключения:', '|', answer_connection, ' ' * (right_field - len(answer_connection)), '|')
                print(f'-' * total_width)

    print(f'| Netstore ', ' ' * (left_field - len('Netstore')), '|', f'{client_data[-1]}', ' ' * (right_field - len(f'{client_data[-1]}')), '|')
    logging.info('Данные выведены в консоль')