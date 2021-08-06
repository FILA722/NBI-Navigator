import re
from confidential import ZonesLoginData, IPMASK
import paramiko

def get_zone_data():
    login_data = {
        'hostname': ZonesLoginData.zones_ip,
        'username': ZonesLoginData.zones_login,
        'password': ZonesLoginData.zones_passwd,
        'port': 22
    }
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(**login_data)
    stdin, stdout, stderr = client.exec_command(ZonesLoginData.zones_get_command)

    with open('zones.txt', 'a') as zones:
        for string in stdout:
            zones.write(string)
    client.close()

def parse_zone_data():
    with open('zones.txt') as zones:
        zones = list(zones)
        len_zones = len(zones)
        str_num = 0
        clients_ip_addresses = ['init']
        ip_gateway_dict = {}
        gateway_ip, gateway_mask = ['init'], ['init']
        gateway_pattern = r'; .+ \d+\.\d+\.\d+\.\d+\/\d+'
        client_pattern = r'\d+-\d+-\d+-\d+.+IN.+A.+\d\.\d.+; [\w.]+'
        vpn_pattern = r'vpn\d+-\d+-\d+-\d+.+IN.+A.+\d\.\d.+; [\w.]+'
        while str_num < len_zones:
            string = zones[str_num]

            vpn = re.match(vpn_pattern,string)
            if vpn:
                continue

            gateway = re.match(gateway_pattern, string)
            if gateway:
                print(gateway_ip[0])
                print(IPMASK.mask_dictionary[gateway_mask[0]])
                ip_gateway_dict[tuple(clients_ip_addresses)] = (gateway_ip[0], IPMASK.mask_dictionary[gateway_mask[0]])
                clients_ip_addresses.clear()
                gateway_mask = re.findall('\/\d\d', zones[str_num])
                gateway_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num+1])
                print(gateway_mask)
                print('---------')
                # print('gateway=', gateway_ip[0])
                str_num += 2
                continue

            client = re.match(client_pattern, string)
            if client:
                client_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num])
                clients_ip_addresses.append(client_ip[0])
                # print('client=', client_ip[0])
                str_num += 1
                continue
            str_num += 1
        for i in ip_gateway_dict:
            print(f'{i} : {ip_gateway_dict[i]}')

def main():
    # get_zone_data()
    parse_zone_data()

main()

