from flask import Flask, render_template, request, url_for, flash, redirect
from search_engine import search_engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iuywfiyug23poiuj2piou5h2pio53thj2[3io5jtp25'

@app.route('/')
def search():
    return render_template('search.html')


@app.route('/client/<client_name>')
def find_client(client_name):
    search_result = search_engine.search(client_name)
    client_name = search_result[0]
    client_data = search_result[1]
    print(client_name)
    print(client_data)
    if not search_result:
        return 'Client not found'
    else:
        return client_name



if __name__ == '__main__':
    app.run()