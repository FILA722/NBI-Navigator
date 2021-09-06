from flask import Flask, render_template, request, url_for, flash, redirect
from search_engine import search_engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iuywfiyug23poiuj2piou5h2pio53thj2[3io5jtp25'

@app.route('/')
def search():
    return render_template('search.html')


@app.route('/client', methods=('GET', 'POST'))
def find_client():
    if request.method == 'POST':
        client = request.form['client']

        if not client:
            flash('Client not found')
        else:
            coincidence_names = search_engine.search(client)
            print(coincidence_names)
            return render_template('client.html', client=coincidence_names)



if __name__ == '__main__':
    app.run()