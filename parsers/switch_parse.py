from parsers.confidential import SwitchLoginData
import telnetlib
import re


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
                return port_condition, port_errors

    with telnetlib.Telnet(switch_ip_address) as telnet:
        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('su'))
        telnet.expect([b"Password:", b">"], timeout=2)
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")

        telnet.write(to_bytes(f'display interface brief'))
        telnet.write(to_bytes(' '))
        display_interface_brief_search_pattern = r'Ethernet\d\/\d\/\d+ +\**\w+ +\w+ +\d+\.*\d*% +\d+\.*\d*% +\d+ +\d+'
        display_interface_brief = re.findall(display_interface_brief_search_pattern, str(telnet.read_until(b'NULL')))

        port_condition, port_errors = parse_current_configuration(display_interface_brief, switch_port)

        telnet.write(to_bytes('display current-configuration'))
        telnet.write(to_bytes(' '))

        if switch_port == '25':
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface GigabitEthernet0/0/1 vlan \d+'
        elif switch_port == '26':
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface GigabitEthernet0/0/2 vlan \d+'
        else:
            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface \w+\/\d+\/{switch_port} vlan \d+'

        current_configuration_of_search_port = re.findall(current_configuration_pattern, str(telnet.read_until(b"http")))

        saved_ip_address = re.findall(r'\d+\.\d+\.\d+\.\d+', current_configuration_of_search_port[0])
        saved_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', current_configuration_of_search_port[0])

        telnet.write(to_bytes('p'))

        if switch_port == '25':
            telnet.write(to_bytes(f'display mac-address GigabitEthernet0/0/1'))
        elif switch_port == '26':
            telnet.write(to_bytes(f'display mac-address GigabitEthernet0/0/2'))
        else:
            telnet.write(to_bytes(f'display mac-address Ethernet0/0/{switch_port}'))

        current_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', str(telnet.read_until(b"Total")))

        if not current_mac_address:
            current_mac_address = ['Не приходит']

        if client_ip_address not in saved_ip_address:
            port_errors = f'На порту прописан IP:{saved_ip_address}'

    return port_condition, saved_mac_address, current_mac_address, port_errors


def parse_zyxel(ip, password, port):
    pass


def parse_asotel(ip, password, port):
    pass