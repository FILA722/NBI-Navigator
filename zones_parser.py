import re
from confidential import ZonesLoginData
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
        while str_num < len_zones:
            gateway_pattern = r'; .+ \d+\.\d+\.\d+\.\d+\/\d+'
            client_pattern = r'\d+-\d+-\d+-\d+.+IN.+A.+\d\.\d.+; [\w.]+'
            string = zones[str_num]
            gateway = re.match(gateway_pattern, string)
            client = re.match(client_pattern, string)
            clients_ip_addresses = []
            client_dict = {}
            if gateway:
                gateway_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num+1])
                print('gateway=', gateway_ip[0])
                str_num += 2
                continue
            elif client:
                client_ip = re.findall('\d+\.\d+\.\d+\.\d+', zones[str_num])
                clients_ip_addresses.append(client_ip)
                print('client=', client_ip[0])
                str_num += 1
                continue
            str_num += 1
        print(client_dict)

def main():
    # get_zone_data()
    parse_zone_data()

main()

