from parsers.confidential import SwitchLoginData
import telnetlib
import logging
import time
import re

def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def write_mac_huawei(saved_mac_addresses, current_mac_addresses, switch_ip_address, client_port, client_ip, client_vlan):

    mac_addresses_to_delete = []
    for saved_mac_address in saved_mac_addresses:
        if saved_mac_address not in current_mac_addresses:
            mac_addresses_to_delete.append(saved_mac_address)

    mac_addresses_to_write = []
    for current_mac_address in current_mac_addresses:
        if current_mac_address not in saved_mac_addresses:
            mac_addresses_to_write.append(current_mac_address)

    if client_port == '25':
        interface_name = 'interface GigabitEthernet0/0/1'
    elif client_port == '26':
        interface_name = 'interface GigabitEthernet0/0/2'
    else:
        interface_name = f'interface Ethernet0/0/{client_port}'

    with telnetlib.Telnet(switch_ip_address) as telnet:
        session = telnet.expect([b"Password:"], timeout=2)

        if not session:
            return 'not session'

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('su'))
        telnet.expect([b"Password:", b">"], timeout=2)

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")

        # for mac_address_to_delete in mac_addresses_to_delete:
        #     telnet.write(to_bytes(f'undo user-bind static ip-address {client_ip} mac-address {mac_address_to_delete}'))
        #     telnet.expect([b"]"], timeout=3)
        #     time.sleep(1)

        for mac_address_to_write in mac_addresses_to_write:
            telnet.write(to_bytes(f'user-bind static ip-address {client_ip} mac-address {mac_address_to_write} {interface_name} vlan {client_vlan}'))
            telnet.expect([b"]"], timeout=3)
            time.sleep(1)

        telnet.write(to_bytes('q'))
        telnet.read_until(b">")

        telnet.write(to_bytes('save'))
        telnet.read_until(b"]")

        telnet.write(to_bytes('y'))
        telnet.expect([b">"], timeout=7)
        telnet.write(to_bytes('q'))

        return True

def write_mac_zyxel(saved_mac_addresses, current_mac_addresses, switch_ip_address, client_port, client_ip, client_vlan):
    pass


def write_mac_address(saved_mac_addresses, current_mac_addresses, switch_ip, client_port, switch_model, client_ip, client_vlan, clien_name):

    write_mac_operation = False

    if switch_model == 'zyxel':
        write_mac_operation = write_mac_zyxel(saved_mac_addresses,
                                              current_mac_addresses,
                                              switch_ip,
                                              client_port,
                                              client_ip,
                                              client_vlan)
    elif switch_model == 'huawei':
        write_mac_operation = write_mac_huawei(saved_mac_addresses,
                                               current_mac_addresses,
                                               switch_ip,
                                               client_port,
                                               client_ip,
                                               client_vlan)


    if write_mac_operation:
        # найти по client_name клиента в БД и записать current_mac_addresses в saved_mac_addresses
        return True
    else:
        return False


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

        return True


def port_reboot_zyxel(switch_ip_address, switch_port):
    pass

