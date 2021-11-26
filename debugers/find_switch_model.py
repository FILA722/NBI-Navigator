from parsers.confidential import SwitchModels
import telnetlib

def find_sw_model(switch_ip_address):
    if switch_ip_address == 'None':
        return 'None'
    try:
        with telnetlib.Telnet(switch_ip_address) as telnet:
            greeting = telnet.read_until(b":")

            if greeting == b'\r\nUser name:':
                new_zyxel = (switch_ip_address,)
                SwitchModels.zyxel += new_zyxel
                return 'zyxel'

            elif greeting in (b'\r\nWarning:',
                              b'\r\r\n\r\nLogin authentication\r\n\r\n\r\nPassword:'):
                new_huawei = (switch_ip_address,)
                SwitchModels.huawei += new_huawei
                return 'huawei'
            else:
                return 'None'

    except (ConnectionResetError, EOFError):
        return 'None'

