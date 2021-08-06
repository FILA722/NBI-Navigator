from parsers.confidential import SwitchLoginData


def get_connection_data_from_switch(switch_ip_address, switch_port):
    zyxel = {
        'device_type': 'huawei',
        # 'device_type': 'zte_zxros',
        'host': switch_ip_address,
        'username': SwitchLoginData.sw_login,
        'password': SwitchLoginData.sw_passwd,
    }
    print(switch_port[1:])

    zyxel_connect = ConnectHandler(**zyxel)
    zyxel_connect.enable()
    # result = zyxel_connect.send_command_timing(f'show mac address-table port {switch_port[1:]}', delay_factor=10)
    result1 = zyxel_connect.send_command_timing('su', delay_factor=10)
    # result2 = zyxel_connect.send_command_timing(SwitchLoginData.sw_passwd, delay_factor=10)
    # result3 = zyxel_connect.send_command_timing('display interface brief', delay_factor=10)

    print(result1)

def main(connection_data):
    for connect_interface in connection_data:
        ip_address = connect_interface
        switch_name = connection_data[connect_interface][0]
        switch_ip_address = connection_data[connect_interface][1]
        switch_port = connection_data[connect_interface][2]

        get_connection_data_from_switch(switch_ip_address, switch_port)

# main({
#       "80.78.39.165": [
#         "Magnit 1 Asva sw1",
#         "10.10.18.5",
#         "#6"
#       ]})
#       # "80.78.51.28": [
#       #   "Magnit 1 Popov sw1",
#       #   "10.10.26.14",
#       #   "#3"
#       # ]
#     # },)

