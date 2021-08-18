from parsers.confidential import SwitchLoginData
import telnetlib
import logging
import re
import time



def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def parse_huawei(switch_ip_address, client_ip_address, switch_port):

    def parse_current_configuration(display_interface_brief, switch_port):
        if len(display_interface_brief) > 24:
            display_interface_brief[-2] = display_interface_brief[-2].replace('1', '25', 1)
            display_interface_brief[-1] = display_interface_brief[-1].replace('2', '26', 1)
        for connection_status_string in display_interface_brief:
            search_port = re.search(f'Ethernet0/0/{switch_port}', connection_status_string)
            if search_port:
                connection_status_list = []
                word = ''
                for letter in connection_status_string:
                    if letter != ' ':
                        word += letter
                    else:
                        if word:
                            connection_status_list.append(word)
                            word = ''
                connection_status_list.append(word)
                port_condition = connection_status_list[1]
                port_errors = int(connection_status_list[-1]) + int(connection_status_list[-2])
                return port_condition, str(port_errors)

    with telnetlib.Telnet(switch_ip_address) as telnet:
        telnet.read_until(b"Password:")
        logging.info("Телнет сессия установлена")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")
        logging.info("Авторизация админа на свиче прошла успешно")

        telnet.write(to_bytes('su'))
        telnet.expect([b"Password:", b">"], timeout=2)
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")
        logging.info("Авторизация рут на свиче прошла успешно")

        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")
        logging.info("команда system-view выполнена")


        telnet.write(to_bytes(f'display interface brief'))
        telnet.write(to_bytes(' '))
        display_interface_brief_search_pattern = r'Ethernet\d\/\d\/\d+ +\**\w+ +\w+ +\d+\.*\d*% +\d+\.*\d*% +\d+ +\d+'
        display_interface_brief = re.findall(display_interface_brief_search_pattern, str(telnet.read_until(b'NULL')))
        logging.info("команда display interface brief выполнена")

        port_condition, port_errors = parse_current_configuration(display_interface_brief, switch_port)
        logging.info(f"данные port_condition и port_errors получены: {port_condition}, {port_errors}")

        telnet.write(to_bytes('display current-configuration'))
        telnet.write(to_bytes(' '))
        logging.info("команда display current-configuration выполнена")

        if switch_port == '25':
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface GigabitEthernet0/0/1 vlan \d+'
        elif switch_port == '26':
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface GigabitEthernet0/0/2 vlan \d+'
        else:
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface Ethernet0\/\d+\/{switch_port} vlan \d+'

        current_configuration_of_search_port = re.findall(current_configuration_pattern, str(telnet.read_until(b"http")))

        saved_ip_address = re.findall(r'\d+\.\d+\.\d+\.\d+', current_configuration_of_search_port[0])
        saved_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', current_configuration_of_search_port[0])
        logging.info(f"данные saved_ip_address и saved_mac_address получены: {saved_ip_address}, {saved_mac_address}")


        telnet.write(to_bytes('p'))

        if switch_port == '25':
            telnet.write(to_bytes(f'display mac-address GigabitEthernet0/0/1'))
        elif switch_port == '26':
            telnet.write(to_bytes(f'display mac-address GigabitEthernet0/0/2'))
        else:
            telnet.write(to_bytes(f'display mac-address Ethernet0/0/{switch_port}'))
        logging.info(f"команда display mac-address выполнена")

        current_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', str(telnet.read_until(b"Total")))
        logging.info(f"На порт приходят mac-адреса: {current_mac_address}")

        if not current_mac_address:
            current_mac_address = ['Не приходит']
            logging.info("На порт не приходит мак-адрес")

        if client_ip_address not in saved_ip_address:
            port_errors = [f'На порту прописан IP:{saved_ip_address}']
            logging.info(f"На порту привязка к другому IP:{saved_ip_address}")

    logging.info(f"Сбор данных со свича выполнен успешно:{port_condition}, {saved_mac_address}, {current_mac_address}, {port_errors}")
    return port_condition, saved_mac_address, current_mac_address, port_errors


def parse_zyxel(switch_ip_address, client_ip_address, switch_port):
    with telnetlib.Telnet(switch_ip_address) as telnet:
        logging.info("Телнет сессия установлена")
        telnet.read_until(b"User name:")
        telnet.write(to_bytes(SwitchLoginData.sw_login))

        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))

        telnet.read_until(b"#")
        logging.info("Авторизация админа на свиче прошла успешно")

        telnet.write(to_bytes(f'show interfaces config {switch_port}'))
        logging.info(f"Выполнить команду show interfaces config {switch_port}")
        show_interfaces_config = re.findall('Active \\\\t:\w+', str(telnet.read_until(b"#")))[0]
        port_condition_slice = show_interfaces_config[show_interfaces_config.index(':') + 1:]
        port_condition = 'UP' if port_condition_slice == 'Yes' else 'DOWN'
        logging.info(f"Команда show interfaces config {switch_port} выполнена, вернула значение port_condition: {port_condition}")

        telnet.write(to_bytes(f'show mac address-table port {switch_port}'))
        logging.info(f"Выполнить команду show mac address-table port {switch_port}")
        current_mac_addresses = re.findall('\w+:\w+:\w+:\w+:\w+:\w+', str(telnet.read_until(b'ic')))

        if not current_mac_addresses:
            current_mac_addresses = ['Не приходит']
        logging.info(f"Команда show mac address-table port {switch_port} выполнена, вернула значение current_mac_addresses: {current_mac_addresses}")

        telnet.write(to_bytes('show ip source binding'))
        logging.info("Выполнить команду show ip source binding")
        time.sleep(1)
        show_ip_source_binding_pattern = f'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w +{client_ip_address} + \w+ + \w+ +\d+ +{switch_port}'
        show_ip_source_binding = re.findall(show_ip_source_binding_pattern, str(telnet.read_until(b'Total')))

        port_errors = []
        if len(show_ip_source_binding) == 0:
            saved_mac_addresses = []
            port_errors.append(f'Нет привязки к {client_ip_address}')
        else:
            saved_mac_addresses = []
            for bind in show_ip_source_binding:
                saved_mac_address = re.findall('\w+:\w+:\w+:\w+:\w+:\w+', bind)[0]
                saved_mac_addresses.append(saved_mac_address)
            for current_mac_address in current_mac_addresses:
                if current_mac_address not in saved_mac_addresses:
                    port_errors.append(f'Приходящий {current_mac_address} не прописан')

        if not port_errors:
            telnet.write(to_bytes('show loopguard'))
            output_1 = telnet.expect([b"continue", b"#"], timeout=2)
            telnet.write(to_bytes('c'))
            output_2 = str(telnet.read_until(b'#'))
            show_loopguard_output = f'{output_1} {output_2}'
            show_loopguard = re.findall(f'{switch_port} +Active +\w+ +\d+ +\d+ +\d+', show_loopguard_output)[0]
            port_errors = [show_loopguard.split("  ")[-1].strip()]
        logging.info(f"Команда show ip source binding выполнена, вернула значение saved_mac_addresses: {saved_mac_addresses}, и port_errors: {port_errors}")

    logging.info(f"Сбор данных со свича выполнен успешно:{port_condition}, {saved_mac_addresses}, {current_mac_addresses}, {port_errors}")
    return port_condition, saved_mac_addresses, current_mac_addresses, port_errors


def parse_asotel(ip, password, port):
    pass