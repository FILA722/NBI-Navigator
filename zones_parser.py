from confidential import ZonesLoginData
import paramiko
login_data = {
    'hostname': ZonesLoginData.zones_ip,
    'username': ZonesLoginData.zones_login,
    'password': ZonesLoginData.zones_passwd,
    'port': 22
}
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(**login_data)
stdin, stdout, stderr = client.exec_command('less /etc/namedb/primary/nbi.com.ua')

with open('zones.txt', 'a') as zones:
    for string in stdout:
        zones.write(string)

client.close()