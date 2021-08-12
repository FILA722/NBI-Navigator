from parsers.confidential import SwitchLoginData
import telnetlib
import re
import time

def to_bytes(line):
    return f"{line}\n".encode("utf-8")

def parse_huawei(switch_ip_address, client_ip_address, switch_port):

    def parse_current_configuration(display_interface_brief, switch_port):
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
        telnet.read_until(b"Password:")
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")
        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")

        telnet.write(to_bytes(f'display interface brief'))
        telnet.write(to_bytes(' '))
        display_interface_brief_search_pattern = r'Ethernet\d\/\d\/\d+ +\**\w+ +\w+ +\d+\.*\d*% +\d+\.*\d*% +\d+ +\d+'
        display_interface_brief = re.findall(display_interface_brief_search_pattern, str(telnet.read_until(b'NULL')))
        port_condition, port_errors = parse_current_configuration(display_interface_brief, switch_port)



        # telnet.write(to_bytes('display current-configuration'))
        # current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface \w+\/\d+\/{port} vlan \d+'
        # current_configuration = re.findall(current_configuration_pattern, str(telnet.read_until(b"http")))
        # for i in current_configuration:
        #     print(i)
        #
        # print('---------------------------')
        #
        # telnet.write(to_bytes('p'))
        # telnet.read_until(b"]")
        #
        # telnet.write(to_bytes(f'display mac-address Ethernet0/0/{port}'))
        # port_mac_address_pattern = '\w{4}-\w{4}-\w{4}'
        # mac_address_on_port = re.findall(port_mac_address_pattern, str(telnet.read_until(b"Total")))
        # print(mac_address_on_port)
        #
        # print('---------------------------')



    return port_condition, saved_mac_address, current_mac_address, port_errors

parse_huawei('10.10.26.4', '9')

def parse_zyxel(ip, password, port):
    pass

def parse_asotel(ip, password, port):
    pass