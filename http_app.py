from flask import Flask, render_template, request, url_for, flash, redirect
from search_engine import search_engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iuywfiyug23poiuj2piou5h2pio53thj2[3io5jtp25'


@app.route('/', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        clients = search_engine.search(request.form['client'])

        if clients == False:
            return render_template('search.html', clients=['Клиент не найден'])
        else:
            return render_template('search.html', clients=clients)
    else:
        return render_template('search.html')


@app.route('/client/<client_name>')
def find_client(client_name):
    search_result = search_engine.search(client_name)
    client_name = search_result[0]
    client_data = search_result[1]
    print(client_name)
    print(client_data)

    return render_template('client.html', search_result=search_result)



if __name__ == '__main__':
    app.run(debug=True)