def mac_check(saved_mac_address, current_mac_address):
    for mac in current_mac_address:
        if mac in saved_mac_address:
            return True