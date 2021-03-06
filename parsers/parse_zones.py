from parsers.confidential import ZonesLoginData, IPMASK
from debugers.check_ping_status import ping_status
from parsers.pathes import Pathes
import paramiko
import re


def parse_zone_data(zones):
    len_zones = len(zones)
    str_num = 0
    ip_gateway_dict = {}
    clients_ip_addresses, gateway_ip, gateway_mask = [], [], []
    vpn_client_ip_addresses = []
    gateway_pattern = r'; .+ \d+\.\d+\.\d+\.\d+\/\d+'
    client_pattern = r'\d+-\d+-\d+-\d+.+IN.+A.+\d\.\d.+; [\w.]+'
    vpn_pattern = r'vpn\d+-\d+-\d+-\d+.+IN.+A.+\d\.\d.+; [\w.]+'
    while str_num < len_zones:
        string = zones[str_num]
        vpn = re.findall(vpn_pattern, string)
        if vpn:
            client_ip = re.findall('\d+\.\d+\.\d+\.\d+', vpn[0])
            vpn_client_ip_addresses.append(client_ip[0])
            str_num += 1
            continue

        gateway = re.match(gateway_pattern, string)
        if gateway:
            if clients_ip_addresses and gateway_ip and gateway_mask:
                try:
                    ip_gateway_dict[tuple(clients_ip_addresses)] = (gateway_ip[0], IPMASK.mask_dictionary[gateway_mask[0]])
                except KeyError:
                    pass
                clients_ip_addresses.clear()
            gateway_mask = re.findall('\/\d\d', zones[str_num])
            gateway_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num+1])
            str_num += 2
            continue

        client = re.match(client_pattern, string)
        if client:
            client_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num])
            clients_ip_addresses.append(client_ip[0])
            str_num += 1
            continue
        str_num += 1

    ip_gateway_dict[tuple(vpn_client_ip_addresses)] = ('VPN', 'VPN')

    return ip_gateway_dict


def get_zone_data():
    login_data = {
        'hostname': ZonesLoginData.zones_ip,
        'username': ZonesLoginData.zones_login,
        'password': ZonesLoginData.zones_passwd,
        'port': 22
    }

    if not ping_status(ZonesLoginData.zones_ip):
        print('!!!?????????????????? ???? ????????????????!!!')
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(**login_data)
    stdin, stdout, stderr = client.exec_command(ZonesLoginData.zones_get_command)

    zones = list(stdout)
    zones_code_new = zones[2].strip()

    with open(Pathes.zones_code_path, 'r') as zones_code_data_to_read:
        zones_code_old = zones_code_data_to_read.read()

    if zones_code_old != zones_code_new:
        with open(Pathes.zones_code_path, 'w') as zones_code_data_to_write:
            zones_code_data_to_write.write(zones_code_new)
        return parse_zone_data(zones)
    else:
        return False
