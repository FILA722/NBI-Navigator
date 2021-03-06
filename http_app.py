import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
from search_engine import search_engine
from switch_operations import write_mac_address, reboot_client_port
from client_managment.client_turn_on import turn_on
from client_managment.client_turn_off import turn_off_clients, check_client_debt_status
from client_managment.send_bill_to_client import send_bill_via_email
from parsers.confidential import KEYS
from parsers.update_clients_database import update_clients_data, edit_client_status_parameter_in_db, migrate_client_from_terminated_to_active, remove_client_from_check_client_balance_data,  add_client_to_check_client_balance_data
from debugers.check_ping_status import ping_status
from parsers import confidential
from parsers.pathes import Pathes
from selenium.common.exceptions import NoSuchElementException
import logging
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = KEYS.flask_key

logging.basicConfig(format='%(asctime)s %(message)s', filename=Pathes.logs_path, level=logging.INFO)


def get_suspended_clients():
    with open(Pathes.terminated_clients_name_url_data_path, 'r') as terminated_data:
        terminated_clients = json.loads(terminated_data.read())
    with open(Pathes.check_client_balance_path) as credit_data:
        credit_clients = json.loads(credit_data.read())
    terminated_clients_list = terminated_clients.keys()
    credit_clients_list = credit_clients.keys()

    suspended_clients = []
    for client in terminated_clients_list:
        if client not in credit_clients_list:
            suspended_clients.append(client)

    return suspended_clients


def add_client_data_to_cash(client_name, client_data):
    with open(Pathes.clients_cash_path, 'w') as client_cash:
        clients = dict()
        clients[client_name] = client_data
        json.dump(clients, client_cash, indent=2, sort_keys=True, ensure_ascii=False)


def get_client_data_from_cash():
    with open(Pathes.clients_cash_path, 'r') as client_cash:
        client_data = json.load(client_cash)
    return client_data


def log_cleaner():
    clean_log = []
    with open(Pathes.logs_path) as log:
        logs = (string for string in log if 'Authentication' not in string and 'Connected' not in string and '\n' != string)
        for i in logs:
            clean_log.append(i)
    with open(Pathes.logs_path, 'w') as cleaned_log_data:
        cleaned_log_data.writelines(clean_log)


def update_dbs():
    next_time_local_update = next_time_total_update = datetime.fromisoformat(f'2021-10-10 14:00:00')
    flag = 1
    while True:
        while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):
            datetime_now = datetime.now()

            if datetime.strptime('5:00', '%H:%M') <= datetime.strptime(f'{datetime.now().hour}:{datetime.now().minute:02d}', '%H:%M') <= datetime.strptime('5:15', '%H:%M'):
                continue

            if ((0 <= datetime_now.weekday() <= 5) and (8 <= datetime_now.hour <= 17)):
                sleeptime_seconds = 10
                local_db_timedelta_minutes = 3
                total_db_timedelta_minutes = 30
            else:
                sleeptime_seconds = 60
                local_db_timedelta_minutes = 30
                total_db_timedelta_minutes = 120

            if datetime.now() >= next_time_total_update:
                print(f'Start update -=TOTAL=- DB at {datetime.now()}')
                start_time = datetime.now()
                try:
                    update_clients_data('total')
                except NoSuchElementException:
                    time.sleep(60)
                    update_clients_data('total')
                turn_off_clients()
                end_time = datetime.now()
                print(f'End of update -=TOTAL=- DB, spended time: {end_time - start_time}')
                next_time_total_update = end_time + timedelta(minutes=total_db_timedelta_minutes)

            if datetime.now() >= next_time_local_update:
                print(f'Start update LOCAL DB at {datetime.now()}')
                start_time = datetime.now()
                try:
                    update_clients_data('local')
                except NoSuchElementException:
                    time.sleep(60)
                    update_clients_data('local')
                end_time = datetime.now()
                print(f'End of update LOCAL DB, spended time: {end_time - start_time}')
                next_time_local_update = end_time + timedelta(minutes=local_db_timedelta_minutes)

            if flag == 1:
                log_cleaner()
                print(f'Start update -=CLOSED=- DB at {datetime.now()}')
                start_time = datetime.now()
                try:
                    update_clients_data('closed')
                except NoSuchElementException:
                    time.sleep(60)
                    update_clients_data('closed')
                end_time = datetime.now()
                print(f'End of update -=CLOSED=- DB, spended time: {end_time - start_time}')
                flag = 0

            time.sleep(sleeptime_seconds)

        print('NO ping to the Netstore')
        time.sleep(60)


@app.route('/', methods=['POST', 'GET'])
def search():
    suspended_clients = get_suspended_clients()

    if request.method == 'POST':
        search = request.form['client']

        if search[:3] == '===':
            client_name = search[3:]
            logging.info(f'Request for turn on client from search page: {client_name}')
            client_url = edit_client_status_parameter_in_db(client_name, "????????????????")
            turn_on_operation = turn_on(client_url)
            if turn_on_operation:
                migrate_client_from_terminated_to_active(client_name)
                remove_client_from_check_client_balance_data(client_name)
                add_client_to_check_client_balance_data(client_name, client_url)
                del suspended_clients[suspended_clients.index(client_name)]
                logging.info(f'{client_name} turned on successful')
                return render_template('search.html', suspended_clients=suspended_clients, toast_alert=f'???????????? {client_name} ??????????????')
            else:
                logging.info(f'{client_name} turned on failed')
                return render_template('search.html', suspended_clients=suspended_clients, toast_alert=f'Operation Error')
        else:
            logging.info(f'Searching request: {search}')
            clients = search_engine.get_coincidence_names(search)
            logging.info(f'Finded coincidence names: {clients}')

            if clients == False:
                return render_template('search.html', clients=['???????????? ???? ????????????'], suspended_clients=suspended_clients, toast_alert=' ')
            else:
                return render_template('search.html', clients=clients, suspended_clients=suspended_clients, toast_alert=' ')
    else:
        return render_template('search.html', suspended_clients=suspended_clients, toast_alert=' ')


@app.route('/client/<client_name>', methods=['POST', 'GET'])
def show_client_page(client_name):
    if request.method == 'GET':

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

        logging.info(f'{client_name} data viewed on http page')
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
        action_request = request.form['client_page']

        if action_request[:3] == '===':
            logging.info(f'{client_name} requested to turn on from client page')
            turn_on_client_data = action_request[3:]
            client_name, client_url = turn_on_client_data.split('+')

            with open(Pathes.clients_cash_path) as clients_cash:
                clients = json.loads(clients_cash.read())
                try:
                    client_data = clients[client_name]
                except KeyError:
                    return redirect(f'/client/{client_name}')

            client_tel = client_data[0]
            client_email = client_data[1]
            client_address = client_data[2]
            client_address_notes = client_data[3].split('\n')
            client_is_active = client_data[4]
            client_converter = client_data[5]
            client_manager = client_data[6]
            client_notes = client_data[7].split('\n')
            client_connection_data = client_data[8]
            client_debt = client_data[11]

            turn_on_operation = turn_on(client_url)

            if turn_on_operation:
                logging.info(f'{client_name} turn on successful')
                client_is_active = '????????????????'
                edit_client_status_parameter_in_db(client_name, "????????????????")
                migrate_client_from_terminated_to_active(client_name)
                remove_client_from_check_client_balance_data(client_name)
                add_client_to_check_client_balance_data(client_name, client_url)
                toast_alert = '???????????? ??????????????'
            else:
                logging.info(f'{client_name} turn on ERROR')
                toast_alert = 'Operation Error'

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
                                   client_url=client_url,
                                   toast_alert=toast_alert)

        elif action_request[:3] == '***':
            logging.info(f'{client_name} requested to port reboot')
            port_reboot_client_data = action_request[3:]
            switch_ip, switch_port, switch_model, client_name = port_reboot_client_data.split('+')
            reboot_client_port(switch_ip, switch_port[1:], switch_model)
            logging.info(f'{client_name} port reboot successful')
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
            client_debt = client_data[11]
            toast_alert = '???????? ????????????????????'

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

        elif action_request[:3] == '+++':
            logging.info(f'{client_name} requested to write mac')
            client_write_mac_data = action_request[3:]
            write_mac_data_list = client_write_mac_data.split('+')

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

            write_mac_address(saved_mac_addresses,
                                    current_mac_addresses,
                                    switch_ip,
                                    client_port,
                                    switch_model,
                                    client_ip,
                                    client_vlan,
                                    client_name)
            logging.info(f'{client_name} write mac successful')
            return redirect(f'/client/{client_name}')

        elif action_request[:3] == '@@@':
            logging.info(f'{client_name} requested to send bill via email')
            client_url = action_request[3:]
            operation = send_bill_via_email(client_url)
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
            client_debt = client_data[11]
            if operation:
                logging.info(f'{client_name} bill was sent via email')
                toast_alert = '???????? ????????????'
            else:
                logging.info(f'{client_name} error while sending email')
                toast_alert = 'Operation Error'

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
            logging.info(f'Search request from client page {clients}')
            if clients == False:
                return render_template('search.html', clients=['???????????? ???? ????????????'], suspended_clients=suspended_clients, toast_alert=' ')
            else:
                return render_template('search.html', clients=clients, suspended_clients=suspended_clients, toast_alert=' ')

# @app.route('/neo')
# def neo():
#     return render_template('knock-knock-neo.html')


def update_main_db():
    while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(
            confidential.NetstoreLoginData.netstore2_url[8:28]):

        print(f'Start update GLOBAL DB at {datetime.now()}')
        start = time.time()
        update_clients_data('total')
        print(f'End of update GLOBAL DB, spended time {time.time() - start}')
        turn_off_clients()
        time.sleep(120)


def update_name_url_db():
    while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):
        start = time.time()
        print(f'Start update LOCAL DB at {datetime.now()}')
        update_clients_data('local')
        print(f'End of update LOCAL DB, spended time: {time.time() - start}')
        time.sleep(180)


def update_closed_name_url_db():
    while ping_status(confidential.NetstoreLoginData.netstore1_url[8:27]) and ping_status(confidential.NetstoreLoginData.netstore2_url[8:28]):
        start = time.time()
        print(f'Start update CLOSED DB at {datetime.now()}')
        update_clients_data('closed')
        print(f'End of update CLOSED DB, spended time: {time.time() - start}')
        time.sleep(120)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run('10.20.31.101')
    # update_name_url_db()
    # update_main_db()
    # update_closed_name_url_db()
    # update_dbs()