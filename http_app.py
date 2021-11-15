import time
from datetime import datetime
from flask import Flask, render_template, request, redirect
from multiprocessing import Process
from search_engine import search_engine
from switch_operations import write_mac_address, reboot_client_port
from client_managment.client_turn_on import turn_on
from client_managment.client_turn_off import turn_off_clients, check_client_debt_status
from parsers.confidential import KEYS
from parsers.update_clients_database import update_clients_data, edit_client_status_parameter_in_db, migrate_client_from_terminated_to_active, remove_client_from_check_client_balance_data,  add_client_to_check_client_balance_data
from debugers.check_ping_status import ping_status
from parsers import confidential
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = KEYS.flask_key


def get_suspended_clients():
    with open('search_engine/terminated_clients_name_url_data.json', 'r') as terminated_clients:
        clients = json.loads(terminated_clients.read())
        suspended_clients = clients.keys()
    return suspended_clients


def add_client_data_to_cash(client_name, client_data):
    with open('search_engine/clients_cash.json', 'w') as client_cash:
        clients = dict()
        clients[client_name] = client_data
        json.dump(clients, client_cash, indent=2, sort_keys=True, ensure_ascii=False)


def get_client_data_from_cash():
    with open('search_engine/clients_cash.json', 'r') as client_cash:
        client_data = json.load(client_cash)
    return client_data


def work_time():
    time_now = time.localtime(time.time())

    if ((0 <= time_now.tm_wday <= 5) and (9 <= time_now.tm_hour <= 17)):
        return True
    else:
        return False


def update_main_db():
    while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):

        print(f'Start update GLOBAL DB at {datetime.now()}')
        start = time.time()
        update_clients_data('total')
        print(f'End of update GLOBAL DB, spended time {time.time() - start}')
        turn_off_clients()

        if work_time():
            time.sleep(1800)
        else:
            # time.sleep(700)
            time.sleep(10800)


def update_name_url_db():
    while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):
        start = time.time()
        print(f'Start update LOCAL DB at {datetime.now()}')
        update_clients_data('local')
        print(f'End of update LOCAL DB, spended time: {time.time() - start}')

        if work_time():
            time.sleep(180)
        else:
            # time.sleep(180)
            time.sleep(10800)


def start_background_processes():
    update_client_url_db_operation = Process(target=update_name_url_db)
    update_main_db_operation = Process(target=update_main_db)

    update_client_url_db_operation.start()
    update_main_db_operation.start()


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/port_reboot', methods=['POST'])
def port_reboot():
    port_reboot_data = request.form['port_reboot']
    switch_ip, switch_port, switch_model, client_name = port_reboot_data.split('+')
    reboot_client_port(switch_ip, switch_port[1:], switch_model)

    client_dict = get_client_data_from_cash()

    client_name = tuple(client_dict.keys())[0]
    client_data = client_dict[client_name]

    client_tel = client_data[0]
    client_email = client_data[1]
    client_address = client_data[2]
    client_address_notes = client_data[3].split('\n')
    client_is_active = client_data[4]
    client_converter = client_data[5]
    client_manager = client_data[6]
    client_notes = client_data[7].split('\n')
    client_connection_data = client_data[8]
    client_url = client_data[9]
    client_debt = client_data[10]

    toast_alert = 'Порт передёрнут'

    return render_template('client.html',
                           client_name=client_name,
                           client_tel=client_tel,
                           client_email=client_email,
                           client_address=client_address,
                           client_address_notes=client_address_notes,
                           client_is_active=client_is_active,
                           client_converter=client_converter,
                           client_manager=client_manager,
                           client_notes=client_notes,
                           client_connection_data=client_connection_data,
                           client_url=client_url,
                           client_debt=client_debt,
                           toast_alert=toast_alert)


@app.route('/write_mac', methods=['POST'])
def write_mac():
    write_mac_data = request.form['write_mac_address']
    write_mac_data_list = write_mac_data.split('+')

    if write_mac_data_list[4] == 'zyxel':
        mac_address_pattern = r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w'
    else:
        mac_address_pattern = r'\w{4}-\w{4}-\w{4}'

    saved_mac_addresses = re.findall(mac_address_pattern, write_mac_data_list[0])
    current_mac_addresses = re.findall(mac_address_pattern, write_mac_data_list[1])

    switch_ip = write_mac_data_list[2]
    client_port = write_mac_data_list[3][1:]
    switch_model = write_mac_data_list[4]
    client_ip = write_mac_data_list[5]
    client_name = write_mac_data_list[6]
    client_vlan = write_mac_data_list[7]

    ans = write_mac_address(saved_mac_addresses,
                            current_mac_addresses,
                            switch_ip,
                            client_port,
                            switch_model,
                            client_ip,
                            client_vlan,
                            client_name)

    return redirect(f'/client/{client_name}')


@app.route('/client_turn_on', methods=['POST'])
def client_turn_on():
    client_name, client_url = request.form['client_turn_on'].split('+')
    turn_on_operation = turn_on(client_url)
    if turn_on_operation:
        edit_client_status_parameter_in_db(client_name, "Активний")
        migrate_client_from_terminated_to_active(client_name)
        remove_client_from_check_client_balance_data(client_name)
        add_client_to_check_client_balance_data(client_name, client_url)
        with open('search_engine/clients_cash.json', 'r') as clients_cash:
            clients = json.loads(clients_cash.read())
            try:
                client_data = clients[client_name]
            except KeyError:
                return redirect(f'/client/{client_name}')

        client_tel = client_data[0]
        client_email = client_data[1]
        client_address = client_data[2]
        client_address_notes = client_data[3].split('\n')
        client_is_active = 'Активний'
        client_converter = client_data[5]
        client_manager = client_data[6]
        client_notes = client_data[7].split('\n')
        client_connection_data = client_data[8]
        client_debt = client_data[10]

        return render_template('client.html',
                               client_name=client_name,
                               client_tel=client_tel,
                               client_email=client_email,
                               client_address=client_address,
                               client_address_notes=client_address_notes,
                               client_is_active=client_is_active,
                               client_converter=client_converter,
                               client_manager=client_manager,
                               client_notes=client_notes,
                               client_connection_data=client_connection_data,
                               client_debt=client_debt,
                               client_url=client_url)
    else:
        #вывести тоаст сообщение что не удалось включить клиента
        return redirect('/')


@app.route('/client_turn_on/<client_name>')
def client_turn_on_from_search_page(client_name):
    client_url = edit_client_status_parameter_in_db(client_name, "Активний")
    turn_on_operation = turn_on(client_url)
    if turn_on_operation:
        migrate_client_from_terminated_to_active(client_name)
        remove_client_from_check_client_balance_data(client_name)
        add_client_to_check_client_balance_data(client_name, client_url)
        return redirect('/')
    else:
        #вывести тоаст-сообщение Включить не удалось
        pass


@app.route('/', methods=['POST', 'GET'])
def search():
    suspended_clients = get_suspended_clients()

    if request.method == 'POST':
        clients = search_engine.get_coincidence_names(request.form['client'])

        if clients == False:
            return render_template('search.html', clients=['Клиент не найден'], suspended_clients=suspended_clients)
        elif len(clients) == 1:
            return redirect(f'/client/{clients[0]}')
        else:
            return render_template('search.html', clients=clients, suspended_clients=suspended_clients)
    else:
        return render_template('search.html', suspended_clients=suspended_clients)


@app.route('/client/<client_name>', methods=['POST', 'GET'])
def show_client_page(client_name):
    if request.method == 'GET':
        start = time.time()
        client_name, client_data = search_engine.get_full_client_data(client_name)

        client_tel = client_data[0]
        client_email = client_data[1]
        client_address = client_data[2]
        client_address_notes = client_data[3].split('\n')
        client_is_active = client_data[4]
        client_converter = client_data[5]
        client_manager = client_data[6]
        client_notes = client_data[7].split('\n')
        client_connection_data = client_data[8]
        client_url = client_data[9]
        client_debt = check_client_debt_status(client_name)
        toast_alert = ' '

        client_data += [client_debt]
        add_client_data_to_cash(client_name, client_data)

        end = time.time()
        print(f'search time = {end - start}')

        return render_template('client.html',
                               client_name=client_name,
                               client_tel=client_tel,
                               client_email=client_email,
                               client_address=client_address,
                               client_address_notes=client_address_notes,
                               client_is_active=client_is_active,
                               client_converter=client_converter,
                               client_manager=client_manager,
                               client_notes=client_notes,
                               client_connection_data=client_connection_data,
                               client_url=client_url,
                               client_debt=client_debt,
                               toast_alert=toast_alert)
    else:
        suspended_clients = get_suspended_clients()
        clients = search_engine.get_coincidence_names(request.form['client'])
        if clients == False:
            return render_template('search.html', clients=['Клиент не найден'], suspended_clients=suspended_clients)
        elif len(clients) == 1:
            return redirect(f'/client/{clients[0]}')
        else:
            return render_template('search.html', clients=clients, suspended_clients=suspended_clients)


if __name__ == '__main__':
    app.run(debug=True)
    # update_name_url_db()
    # update_main_db()