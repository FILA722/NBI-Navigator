from parsers.confidential import SwitchLoginData
import telnetlib
import re
from datetime import datetime
import time


def to_bytes(line):
    return f"{line}\n".encode("utf-8")

def time_marker_for_huawei_logs():
    pass

def current_mac_address_color_marker(saved_mac_addresses, current_mac_address):
    current_mac_address_colored = []
    write_mac_address_button_status = False
    for mac_address in current_mac_address:
        if mac_address == 'Не приходит':
            current_mac_address_colored.append((mac_address, 'red'))
        elif mac_address in saved_mac_addresses:
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


def find_real_net_vlan(vlan_nums):
    vlan_max = ('-1', -1)
    for vlan_num in vlan_nums:
        if vlan_max[0] != vlan_num:
            vlan_num_count = vlan_nums.count(vlan_num)
            if vlan_num_count > vlan_max[1]:
                vlan_max = (vlan_num, vlan_num_count)
    return vlan_max[0]


def parse_huawei(switch_ip_address, client_port):
    try:
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
            port_condition, port_errors = parse_current_configuration(display_interface_brief, client_port)

            telnet.write(to_bytes('display current-configuration'))
            telnet.write(to_bytes(' '))
            display_current_configuration_output = str(telnet.read_until(b"http"))

            if client_port == '25':
                interface_name = 'GigabitEthernet0/0/1'
            elif client_port == '26':
                interface_name = 'GigabitEthernet0/0/2'
            else:
                interface_name = f'Ethernet0/0/{client_port}'

            current_configuration_pattern = f'user-bind static ip-address \d+\.\d+\.\d+.\d+ mac-address \w+-\w+-\w+ interface {interface_name} vlan \d+'
            current_configuration_of_search_port = re.findall(current_configuration_pattern, display_current_configuration_output)

            if current_configuration_of_search_port:
                saved_mac_address = []
                for mac_address_string in current_configuration_of_search_port:
                    current_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', mac_address_string)
                    if current_mac_address:
                        saved_mac_address.append(current_mac_address[0])
            else:
                saved_mac_address = ['None']

            try:
                saved_vlan = re.findall(r'vlan \d+', current_configuration_of_search_port[0])[0].strip('vlan ')
            except IndexError:
                vlan_list = re.findall(r'vlan \d+', display_current_configuration_output)
                vlan_nums = [i.strip('vlan ') for i in vlan_list]
                saved_vlan = find_real_net_vlan(vlan_nums)

            telnet.write(to_bytes('p'))

            telnet.write(to_bytes(f'display mac-address {interface_name}'))

            current_mac_address = re.findall(r'\w{4}-\w{4}-\w{4}', str(telnet.read_until(b"Total")))
            if not current_mac_address:
                current_mac_address = ['Не приходит']
            else:
                port_condition = 'up'

            telnet.write(to_bytes('display log'))
            logs = str(telnet.read_until(b"More"))
            telnet.write(to_bytes('c'))

            logs = logs.split(r'\r\n')
            port_time = False
            for string in logs:
                find = re.findall(f'{interface_name} has turned into', string)
                if find:
                    event_time_str = string[:17]
                    if event_time_str[4] == ' ':
                        event_time_str = f'{event_time_str[:4]}0{event_time_str[5:]}'
                    event_time_obj = datetime.strptime(event_time_str, '%b %d %Y %H:%M')
                    event_time = datetime.now() - event_time_obj
                    port_time = str(event_time)[:-7]
                    break

            if not port_time:
                last_event = logs[-2]
                event_time_str = last_event[:17]
                if event_time_str[4] == ' ':
                    event_time_str = f'{event_time_str[:4]}0{event_time_str[5:]}'
                event_time_obj = datetime.strptime(event_time_str, '%b %d %Y %H:%M')
                event_time = datetime.now() - event_time_obj
                if port_condition == 'up':
                    port_time = f'>{str(event_time)[:-7]}'
                else:
                    port_time = f'>{str(event_time)[:-7]}'

            telnet.write(to_bytes('q'))
            telnet.read_until(b">")
            telnet.write(to_bytes('q'))

            current_mac_addresses, write_mac_address_button_status = current_mac_address_color_marker(saved_mac_address, current_mac_address)

        return port_condition, saved_mac_address, current_mac_addresses, port_errors, write_mac_address_button_status, saved_vlan, port_time

    except (ConnectionResetError, EOFError):
        return False

def parse_zyxel(switch_ip_address, client_ip_address, switch_port):
    try:
        with telnetlib.Telnet(switch_ip_address) as telnet:
            telnet.expect([b":"], timeout=2)

            telnet.write(to_bytes(SwitchLoginData.sw_login))

            telnet.read_until(b"Password:")
            telnet.write(to_bytes(SwitchLoginData.sw_passwd))

            telnet.expect([b"#"])

            telnet.write(to_bytes(f'show interfaces {switch_port}'))
            time.sleep(1)
            show_interfaces_answer = str(telnet.expect([b"quit"], timeout=2))

            show_interfaces_config = re.findall(r'\\t\\tLink\\t\\t\\t:\w+', show_interfaces_answer)
            port_condition = 'up' if show_interfaces_config[0].split(':')[1].strip() in ('1000M', '100M') else 'down'

            try:
                port_uptime_data = re.findall(r'\\t\\tUp Time\\t\\t\\t:\w+:\w+:\w+', show_interfaces_answer)
                port_uptime = re.findall(r'\d+:\d+:\d+', port_uptime_data[0])[0]
            except IndexError:
                port_uptime = None

        with telnetlib.Telnet(switch_ip_address) as telnet:

            telnet.expect([b"User name:"], timeout=2)

            telnet.write(to_bytes(SwitchLoginData.sw_login))

            telnet.read_until(b"Password:")
            telnet.write(to_bytes(SwitchLoginData.sw_passwd))

            telnet.expect([b"#"])

            telnet.write(to_bytes(f'show mac address-table port {switch_port}'))
            current_mac_addresses = re.findall('\w+:\w+:\w+:\w+:\w+:\w+', str(telnet.read_until(b'#')))

            saved_vlan = ''
            if not current_mac_addresses:
                telnet.write(to_bytes(f'show mac address-table port {switch_port}'))
                filtered_mac_addresses = re.findall('\w+:\w+:\w+:\w+:\w+:\w+ *\d* *\d*', str(telnet.expect([b"#"])))
                current_mac_addresses = []
                for mac_address in filtered_mac_addresses:
                    mac_address_list = mac_address.split(' ')
                    if mac_address_list[-1] == str(switch_port):
                        current_mac_addresses.append(mac_address_list[0])
                        for vlan in mac_address_list[1:-1]:
                            if vlan:
                                saved_vlan = vlan
                                break
                if not current_mac_addresses:
                    current_mac_addresses = ['Не приходит']
                else:
                    port_condition = 'up'

        time.sleep(2)

        with telnetlib.Telnet(switch_ip_address) as telnet:
            telnet.expect([b"User name:"], timeout=2)

            telnet.write(to_bytes(SwitchLoginData.sw_login))
            telnet.read_until(b"Password:")

            telnet.write(to_bytes(SwitchLoginData.sw_passwd))
            telnet.expect([b"#"])

            telnet.write(to_bytes('show ip source binding'))

            time.sleep(1)

            telnet.write(to_bytes('c'))
            show_ip_source_binding_return = str(telnet.expect([b'Total', b'#']))
            show_ip_source_binding_pattern = f'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w +{client_ip_address} + \w+ + \w+ +\d+ +{switch_port}'
            show_ip_source_binding = re.findall(show_ip_source_binding_pattern,  show_ip_source_binding_return)

            if not show_ip_source_binding:
                if not saved_vlan:
                    vlan_list = re.findall('static +\d+', show_ip_source_binding_return)
                    vlan_nums = [i.strip('static ') for i in vlan_list]
                    saved_vlan = find_real_net_vlan(vlan_nums)
                saved_mac_addresses = ['None']
            else:
                if not saved_vlan:
                    saved_vlan = re.findall(r'static +\d+', show_ip_source_binding[0])[0].strip('static ')
                saved_mac_addresses = []
                for bind in show_ip_source_binding:
                    saved_mac_address = re.findall('\w+:\w+:\w+:\w+:\w+:\w+', bind)[0]
                    saved_mac_addresses.append(saved_mac_address)

            telnet.write(to_bytes('show loopguard'))
            output_1 = telnet.expect([b"continue", b"#"], timeout=2)
            telnet.write(to_bytes('c'))
            output_2 = str(telnet.read_until(b'#'))
            show_loopguard_output = f'{output_1} {output_2}'
            show_loopguard = re.findall(f'{switch_port} +Active +\w+ +\d+ +\d+ +\d+', show_loopguard_output)
            if show_loopguard:
                port_errors = [show_loopguard[0].split("  ")[-1].strip()]
            else:
                port_errors = '0'
            current_mac_addresses_colored, write_mac_address_button_status = current_mac_address_color_marker(saved_mac_addresses, current_mac_addresses)

            telnet.write(to_bytes('write memory'))

        return port_condition, saved_mac_addresses, current_mac_addresses_colored, port_errors, write_mac_address_button_status, saved_vlan, port_uptime
    except (ConnectionResetError, EOFError):
        return False


def parse_asotel(ip, password, port):
    pass