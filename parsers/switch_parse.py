from parsers.confidential import SwitchLoginData
import telnetlib
import logging
import re
import time


def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def current_mac_address_color_marker(saved_mac_address, current_mac_address):
    current_mac_address_colored = []
    write_mac_address_button_status = False
    for mac_address in current_mac_address:
        if mac_address == 'Не приходит':
            current_mac_address_colored.append((mac_address, 'red'))
        elif mac_address in saved_mac_address:
            current_mac_address_colored.append((mac_address, 'green'))
        else:
            current_mac_address_colored.append((mac_address, 'red'))
            write_mac_address_button_status = True
    return current_mac_address_colored, write_mac_address_button_status


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


def parse_huawei(switch_ip_address, client_ip_address, client_port):
    with telnetlib.Telnet(switch_ip_address) as telnet:
        session = telnet.read_until(b"Password:")

        if session:
            logging.info("Телнет сессия установлена")
        else:
            logging.info("Телнет НЕ сессия установлена")
            raise EOFError

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
        print("команда system-view выполнена")
        telnet.write(to_bytes(f'display interface brief'))
        telnet.write(to_bytes(' '))
        display_interface_brief_search_pattern = r'Ethernet\d\/\d\/\d+ +\**\w+ +\w+ +\d+\.*\d*% +\d+\.*\d*% +\d+ +\d+'
        display_interface_brief = re.findall(display_interface_brief_search_pattern, str(telnet.read_until(b'NULL')))
        logging.info("команда display interface brief выполнена")
        port_condition, port_errors = parse_current_configuration(display_interface_brief, client_port)
        logging.info(f"данные port_condition и port_errors получены: {port_condition}, {port_errors}")
        print(f"данные port_condition и port_errors получены: {port_condition}, {port_errors}")
        telnet.write(to_bytes('display current-configuration'))
        telnet.write(to_bytes(' '))
        display_current_configuration_output = str(telnet.read_until(b"http"))
        logging.info("команда display current-configuration выполнена")
        print("команда display current-configuration выполнена")
        if client_port == '25':
            interface_name = 'GigabitEthernet0/0/1'
        elif client_port == '26':
            interface_name = 'GigabitEthernet0/0/2'
        else:
            interface_name = f'Ethernet0/0/{client_port}'

        current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface {interface_name} vlan \d+'
        current_configuration_of_search_port = re.findall(current_configuration_pattern, display_current_configuration_output)

        try:
            saved_ip_address = re.findall(r'\d+\.\d+\.\d+\.\d+', current_configuration_of_search_port[0])
            saved_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', current_configuration_of_search_port[0])
            saved_vlan = re.findall(r'vlan \d+', current_configuration_of_search_port[0])[0].strip('vlan ')
        except IndexError:
            saved_ip_address = ''
            saved_mac_address = ''

            vlan_list = re.findall(r'vlan \d+', display_current_configuration_output)
            vlan_nums = [i.strip('vlan ') for i in vlan_list]
            vlan_max = ('-1', -1)
            for vlan_num in vlan_nums:
                if vlan_max[0] != vlan_num:
                    vlan_num_count = vlan_nums.count(vlan_num)
                    if vlan_num_count > vlan_max[1]:
                        vlan_max = (vlan_num, vlan_num_count)
            saved_vlan = vlan_max[0]
        logging.info(f"данные saved_ip_address и saved_mac_address получены: {saved_ip_address}, {saved_mac_address}")
        telnet.write(to_bytes('p'))
        print(f"данные saved_ip_address и saved_mac_address получены: {saved_ip_address}, {saved_mac_address}")

        telnet.write(to_bytes(f'display mac-address {interface_name}'))
        logging.info(f"команда display mac-address выполнена")

        current_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', str(telnet.read_until(b"Total")))
        logging.info(f"На порт приходят mac-адреса: {current_mac_address}")
        if not current_mac_address:
            current_mac_address = ['Не приходит']
            logging.info("На порт не приходит мак-адрес")

        if client_ip_address not in saved_ip_address:
            port_errors = [f'На порту прописан IP:{saved_ip_address}']
            logging.info(f"На порту привязка к другому IP:{saved_ip_address}")

        telnet.write(to_bytes('q'))
        telnet.read_until(b">")
        telnet.write(to_bytes('q'))

        current_mac_addresses, write_mac_address_button_status = current_mac_address_color_marker(saved_mac_address, current_mac_address)

        logging.info(f"Сбор данных со свича выполнен успешно:{port_condition}, {saved_mac_address}, {current_mac_addresses}, {port_errors}")
        print(f"Сбор данных со свича выполнен успешно:{port_condition}, {saved_mac_address}, {current_mac_addresses}, {port_errors}")

        return port_condition, saved_mac_address, current_mac_addresses, port_errors, write_mac_address_button_status, saved_vlan


def parse_zyxel(switch_ip_address, client_ip_address, switch_port):
    time.sleep(1)
    with telnetlib.Telnet(switch_ip_address) as telnet:
        start_question = telnet.expect([b":"], timeout=2)
        if start_question:
            logging.info("Телнет сессия установлена")
        else:
            logging.info("Телнет сессия НЕ установлена")
            raise EOFError

        telnet.write(to_bytes(SwitchLoginData.sw_login))

        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))

        telnet.expect([b"#"])
        logging.info("Авторизация админа на свиче прошла успешно")

        telnet.write(to_bytes(f'show interfaces {switch_port}'))
        time.sleep(1)
        logging.info(f"Выполнить команду show interfaces {switch_port}")
        show_interfaces_answer = str(telnet.expect([b"quit"], timeout=2))
        show_interfaces_config = re.findall(r'\\t\\tLink\\t\\t\\t:\w+', show_interfaces_answer)

        if show_interfaces_config:
            port_condition = 'DOWN' if show_interfaces_config[0].split(':')[1].strip() == 'Down' else 'UP'
        else:
            port_condition = 'Не определён'
        logging.info(f"Команда show interfaces {switch_port} выполнена, вернула значение port_condition: {port_condition}")

    with telnetlib.Telnet(switch_ip_address) as telnet:

        start_question = telnet.expect([b"User name:"], timeout=2)
        if start_question:
            logging.info("Телнет сессия установлена")
        else:
            logging.info("Телнет сессия НЕ установлена")
            raise EOFError

        telnet.write(to_bytes(SwitchLoginData.sw_login))

        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))

        telnet.expect([b"#"])
        logging.info("Авторизация админа на свиче прошла успешно")

        telnet.write(to_bytes(f'show mac address-table port {switch_port}'))
        logging.info(f"Выполнить команду show mac address-table port {switch_port}")
        current_mac_addresses = re.findall('\w+:\w+:\w+:\w+:\w+:\w+', str(telnet.read_until(b'#')))

        if not current_mac_addresses:
            current_mac_addresses = ['Не приходит']
        logging.info(
            f"Команда show mac address-table port {switch_port} выполнена, вернула значение current_mac_addresses: {current_mac_addresses}")

    time.sleep(2)
    with telnetlib.Telnet(switch_ip_address) as telnet:

        start_question = telnet.expect([b"User name:"], timeout=2)
        if start_question:
            logging.info("Телнет сессия установлена")
        else:
            logging.info("Телнет сессия НЕ установлена")
            raise EOFError

        telnet.write(to_bytes(SwitchLoginData.sw_login))

        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))

        telnet.expect([b"#"])
        logging.info("Авторизация админа на свиче прошла успешно")

        telnet.write(to_bytes('show ip source binding'))
        logging.info("Выполнить команду show ip source binding")
        time.sleep(1)
        telnet.write(to_bytes('c'))
        show_ip_source_binding_pattern = f'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w +{client_ip_address} + \w+ + \w+ +\d+ +{switch_port}'
        show_ip_source_binding = re.findall(show_ip_source_binding_pattern, str(telnet.expect([b'Total', b'#'])))

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
            show_loopguard = re.findall(f'{switch_port} +Active +\w+ +\d+ +\d+ +\d+', show_loopguard_output)
            if show_loopguard:
                port_errors = [show_loopguard[0].split("  ")[-1].strip()]
            else:
                port_errors = 0

        logging.info(f"Команда show ip source binding выполнена, вернула значение saved_mac_addresses: {saved_mac_addresses}, и port_errors: {port_errors}")

        current_mac_addresses_colored = current_mac_address_color_marker(saved_mac_address, current_mac_address)

    logging.info(f"Сбор данных со свича выполнен успешно:{port_condition}, {saved_mac_addresses}, {current_mac_addresses_colored}, {port_errors}")
    return port_condition, saved_mac_addresses, current_mac_addresses_colored, port_errors,


def parse_asotel(ip, password, port):
    pass