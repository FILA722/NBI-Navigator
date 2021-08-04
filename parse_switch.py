from start_browser import driver
from netmiko import ConnectHandler
import time

def get_connection_data_from_switch(switch_ip_address, switch_port):
    try:
        browser = driver(f'http://{switch_ip_address}/')
    finally:
        time.sleep(15)
        browser.quit()

def main(connection_data):
    for connect_interface in connection_data:
        ip_address = connect_interface
        switch_name = connection_data[connect_interface][0]
        switch_ip_address = connection_data[connect_interface][1]
        switch_port = connection_data[connect_interface][2]

        get_connection_data_from_switch(switch_ip_address, switch_port)

main({
      "80.78.39.165": [
        "Magnit 1 Asva sw1",
        "10.10.26.23",
        "#6"
      ],
      "80.78.51.28": [
        "Magnit 1 Popov sw1",
        "10.10.26.14",
        "#3"
      ]
    },)

