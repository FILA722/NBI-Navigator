from parsers.confidential import SwitchLoginData
import telnetlib
import logging
import time

def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def port_reboot_huawei(switch_ip_address, switch_port):
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

        if switch_port == '25':
            port_name = 'interface GigabitEthernet0/0/1'
        elif switch_port == '26':
            port_name = 'interface GigabitEthernet0/0/2'
        else:
            port_name = f'interface Ethernet0/0/{switch_port}'

        telnet.write(to_bytes(port_name))
        telnet.expect(b">", timeout=2)

        telnet.write(to_bytes('shutdown'))
        telnet.expect(b">", timeout=2)

        time.sleep(2)

        telnet.write(to_bytes('undo shutdown'))
        telnet.expect(b">", timeout=2)

        return 'port reboot successful'