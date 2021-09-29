from flask import Flask, render_template, request, url_for, flash, redirect
from search_engine import search_engine
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iuywfiyug23poiuj2piou5h2pio53thj2[3io5jtp25'

@app.route('/port_reboot')
def port_reboot():
    print("Port reboot")
    return "nothing"


@app.route('/write_mac')
def write_mac():
    print("Write mac")
    return "nothing"


@app.route('/client_turn_on')
def client_tuen_on():
    print('client_turn_on')
    return 'nothing'


def get_suspended_clients():
    suspended_clients = []
    with open('search_engine/clients.json', 'r') as dict_with_clients:
        clients = json.loads(dict_with_clients.read())
        for client in clients:
            if clients[client][4] == "Неактивний":
                suspended_clients.append(client)
    return suspended_clients


@app.route('/', methods=['POST', 'GET'])
def search():
    suspended_clients = get_suspended_clients()
    if request.method == 'POST':
        clients = search_engine.search(request.form['client'])
        if clients == False:
            return render_template('search.html', clients=['Клиент не найден'], suspended_clients=suspended_clients)
        elif str(clients.__class__) == "<class 'tuple'>":
            client_name = clients[0]
            return redirect(f'/client/{client_name}')
        else:
            return render_template('search.html', clients=clients, suspended_clients=suspended_clients)
    else:
        return render_template('search.html', suspended_clients=suspended_clients)


@app.route('/client/<client_name>', methods=['POST', 'GET'])
def find_client(client_name):
    suspended_clients = get_suspended_clients()
    if request.method == 'POST':
        clients = search_engine.search(request.form['client'])
        if clients == False:
            return render_template('search.html', clients=['Клиент не найден'], suspended_clients=suspended_clients)
        elif str(clients.__class__) == "<class 'tuple'>":
            client_name = clients[0]
            return redirect(f'/client/{client_name}')
        else:
            return render_template('search.html', clients=clients, suspended_clients=suspended_clients)
    else:
        search_result = search_engine.search(client_name)

        client_name = search_result[0]
        client_data = search_result[1]
        # client_name = 'кармазіна ірина юрївна'
        # client_data = ['0675075036,0442273438',
        #                'i.dronova@nbi.ua, i.dronova@unitex.od.ua',
        #                'Бизнес-центр Євгена Сверстюка, 11A',
        #                'ВНДІХІМПРОЕКТ - хозяин здания\n516-8478 Александр Владимирович - нач.тех.отдела\n\nсвязист Константин 095 4456484 (работает только по понедельникам)\n\nОборудование стоит в НОВИЙ БЦ ТОВ, знает где стоит - Артем гл. инж.\n050 1520558 (ребутнет если чего, категорически не приветствует)\n!!! Шлюз 80.78.40.17 !!!\nПодключено конверторами с МР17. Конвертор МР11-МР17 FOXGATE EC-23721-1SM-20 #EC20110252670\nSwitch Zyxel MES-35000-24\nS/N: S120H27009921\n(АТС подвал)\nSwitch2 Quidway  S2326TP-EI \n12(пов.)',
        #                'Неактивний',
        #                'НЕТ',
        #                '(050)383-06-91 Николай Дмитриевич',
        #                '==Sverstyuka 11A sw2#5==\nНеобмежений:\nсвіт - 10М\nУкраїна - до 100М\n\nМАС-адрес:\n50ff-204a-eb4e\n\nзміна прізвища з Дронова на Кармазіна Ірина Юріївна',
        #                {'80.78.40.13': ['Sverstyuka 11A sw2', '10.10.16.8', '#5', '80.78.40.17', '255.255.255.224', 'huawei', 'up', ['50ff-204a-eb4e'], ['50ff-204a-eb4e'], '0', True, True]},
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

        return render_template('client.html', client_name=client_name,
                                            client_tel = client_tel,
                                            client_email=client_email,
                                            client_address=client_address,
                                            client_address_notes=client_address_notes,
                                            client_is_active=client_is_active,
                                            client_converter=client_converter,
                                            client_manager=client_manager,
                                            client_notes=client_notes,
                                            client_connection_data=client_connection_data,
                                            client_url=client_url)


if __name__ == '__main__':
    app.run(debug=True)