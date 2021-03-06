from parsers.confidential import SwitchLoginData
import telnetlib
import logging
import time


def to_bytes(line):
    return f"{line}\n".encode("utf-8")


def reboot_client_port(switch_ip, switch_port, switch_model):

    port_reboot_operation = False

    if switch_model == 'zyxel':
        port_reboot_operation = port_reboot_zyxel(switch_ip, switch_port)
    elif switch_model == 'huawei':
        port_reboot_operation = port_reboot_huawei(switch_ip, switch_port)

    time.sleep(3)
    return True if port_reboot_operation else False


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
    time.sleep(3)
    return write_mac_operation


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
            return False

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('su'))
        telnet.expect([b"Password:", b">"], timeout=2)

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")

        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")

        for mac_address_to_delete in mac_addresses_to_delete:
            telnet.write(to_bytes(f'undo user-bind static ip-address {client_ip} mac-address {mac_address_to_delete}'))
            telnet.expect([b"]"], timeout=3)
            time.sleep(1)

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

        telnet.close()

    return True

def write_mac_zyxel(saved_mac_addresses, current_mac_addresses, switch_ip_address, client_port, client_ip, client_vlan):
    mac_addresses_to_delete = []
    for saved_mac_address in saved_mac_addresses:
        if saved_mac_address not in current_mac_addresses:
            mac_addresses_to_delete.append(saved_mac_address)

    mac_addresses_to_write = []
    for current_mac_address in current_mac_addresses:
        if current_mac_address not in saved_mac_addresses:
            mac_addresses_to_write.append(current_mac_address)

    with telnetlib.Telnet(switch_ip_address) as telnet:
        telnet.expect([b":"], timeout=2)

        telnet.write(to_bytes(SwitchLoginData.sw_login))
        telnet.read_until(b"Password:")

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.expect([b"#"])

        logging.info("?????????????????????? ???????????? ???? ?????????? ???????????? ??????????????")
        telnet.write(to_bytes('configure'))
        telnet.expect([b"#"])

        for mac_address_to_delete in mac_addresses_to_delete:
            telnet.write(to_bytes(f'no ip source binding {mac_address_to_delete} vlan {client_vlan}'))
            telnet.expect([b"#"], timeout=3)
            time.sleep(1)

        for mac_address_to_write in mac_addresses_to_write:
            telnet.write(to_bytes(f'ip source binding {mac_address_to_write} vlan {client_vlan} {client_ip} interface port-channel {client_port}'))
            telnet.expect([b"#"], timeout=3)
            time.sleep(1)
        telnet.write(to_bytes('exit'))
        telnet.expect([b"#"])
        telnet.write(to_bytes('write memory'))
        telnet.expect([b"#"])
    return True


def port_reboot_huawei(switch_ip_address, switch_port):
    with telnetlib.Telnet(switch_ip_address) as telnet:
        session = telnet.read_until(b"Password:")

        if session:
            logging.info("???????????? ???????????? ??????????????????????")
        else:
            logging.info("???????????? ???? ???????????? ??????????????????????")
            raise EOFError

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.read_until(b">")
        logging.info("?????????????????????? ???????????? ???? ?????????? ???????????? ??????????????")

        telnet.write(to_bytes('su'))
        telnet.expect([b"Password:", b">"], timeout=2)
        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.expect([b">"], timeout=2)
        logging.info("?????????????????????? ?????? ???? ?????????? ???????????? ??????????????")

        telnet.write(to_bytes('system-view'))
        telnet.read_until(b"]")
        logging.info("?????????????? system-view ??????????????????")

        if switch_port == '25':
            port_name = 'interface GigabitEthernet0/0/1'
        elif switch_port == '26':
            port_name = 'interface GigabitEthernet0/0/2'
        else:
            port_name = f'interface Ethernet0/0/{switch_port}'

        telnet.write(to_bytes(port_name))
        telnet.expect([b">"], timeout=2)

        telnet.write(to_bytes('shutdown'))
        telnet.expect([b">"], timeout=2)

        time.sleep(3)

        telnet.write(to_bytes('undo shutdown'))
        telnet.expect([b">"], timeout=2)

        return True


def port_reboot_zyxel(switch_ip_address, switch_port):
    with telnetlib.Telnet(switch_ip_address) as telnet:
        telnet.expect([b":"], timeout=2)

        telnet.write(to_bytes(SwitchLoginData.sw_login))
        telnet.read_until(b"Password:")

        telnet.write(to_bytes(SwitchLoginData.sw_passwd))
        telnet.expect([b"#"])

        logging.info("?????????????????????? ???????????? ???? ?????????? ???????????? ??????????????")

        telnet.write(to_bytes('configure'))
        telnet.expect([b"#"])

        telnet.write(to_bytes(f'interface port-channel {switch_port}'))
        telnet.expect([b"#"])

        telnet.write(to_bytes('inactive'))
        time.sleep(3)
        telnet.write(to_bytes('no inactive'))

        telnet.expect([b"#"])

        time.sleep(3)
    return True