from flask import Flask, render_template, request, url_for, flash, redirect
from search_engine import search_engine
from switch_operations import write_mac_address, reboot_client_port
from client_managment.client_turn_on import turn_on
from parsers.confidential import KEYS
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = KEYS.flask_key


def get_suspended_clients():
    suspended_clients = []
    with open('search_engine/clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
        for client in clients:
            if clients[client][4] == "Неактивний":
                suspended_clients.append(client)
    return suspended_clients


def add_client_data_to_cash(client_name, client_data):
    with open('search_engine/clients_cash.json', 'r') as clients_cash:
        clients = json.loads(clients_cash.read())
        if client_name not in clients.keys():
            clients[client_name] = client_data
            client_cash = json.dumps(clients, indent=2, sort_keys=True, ensure_ascii=False)
            with open('search_engine/clients_cash.json', 'w') as clients_cash:
                clients_cash.write(client_cash)


@app.route('/port_reboot', methods=['POST'])
def port_reboot():
    if request.method == 'POST':
        port_reboot_data = request.form['port_reboot']
        switch_ip, switch_port, switch_model, client_name = port_reboot_data.split('+')
        reboot_client_port(switch_ip, switch_port[1:], switch_model)
        return redirect(f'/client/{client_name}')


@app.route('/write_mac', methods=['POST'])
def write_mac():
    if request.method == 'POST':
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
    with open('search_engine/clients_cash.json', 'r') as clients_cash:
        clients = json.loads(clients_cash.read())
        client_data = clients[client_name]

    client_tel = client_data[0]
    client_email = client_data[1]
    client_address = client_data[2]
    client_address_notes = client_data[3].split('\n')
    client_is_active = 'Активний'
    client_converter = client_data[5]
    client_manager = client_data[6]
    client_notes = client_data[7].split('\n')
    client_connection_data = client_data[8]

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
                           client_url=client_url) if turn_on_operation else redirect('/')


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
        client_name, client_data = search_engine.get_full_client_data(client_name)
        add_client_data_to_cash(client_name, client_data)
        # client_name = 'кармазіна ірина юрївна'
        # client_data = ['0675075036,0442273438',
        #                'i.dronova@nbi.ua, i.dronova@unitex.od.ua',
        #                'Бизнес-центр Євгена Сверстюка, 11A',
        #                'ВНДІХІМПРОЕКТ - хозяин здания\n516-8478 Александр Владимирович - нач.тех.отдела\n\nсвязист Константин 095 4456484 (работает только по понедельникам)\n\nОборудование стоит в НОВИЙ БЦ ТОВ, знает где стоит - Артем гл. инж.\n050 1520558 (ребутнет если чего, категорически не приветствует)\n!!! Шлюз 80.78.40.17 !!!\nПодключено конверторами с МР17. Конвертор МР11-МР17 FOXGATE EC-23721-1SM-20 #EC20110252670\nSwitch Zyxel MES-35000-24\nS/N: S120H27009921\n(АТС подвал)\nSwitch2 Quidway  S2326TP-EI \n12(пов.)',
        #                'Активний',
        #                'НЕТ',
        #                '(050)383-06-91 Николай Дмитриевич',
        #                '==Sverstyuka 11A sw2#5==\nНеобмежений:\nсвіт - 10М\nУкраїна - до 100М\n\nМАС-адрес:\n50ff-204a-eb4e\n\nзміна прізвища з Дронова на Кармазіна Ірина Юріївна',
        #                {'80.78.40.13': ['Sverstyuka 11A sw2', '10.10.16.8', '#5', '80.78.40.17', '255.255.255.224', 'huawei', 'up', ['50ff-204a-eb4e'], [('50ff-204a-eb4e', 'green')], '0', False, '5', False, True]},
        #                'https://netstore2.nbi.com.ua/show_client.php?client_id=124']

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
                               client_url=client_url)
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
