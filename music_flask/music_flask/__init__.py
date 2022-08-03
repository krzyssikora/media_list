from flask import Flask, render_template, request
import json
from music_flask import config, utils, api
from music_flask.config import _logger

app = Flask(__name__)
counter_value = 1


@app.route('/')
def index():
    global counter_value
    title = 'my music'
    # get_page_number(counter=counter_value, func='index')
    return render_template('index.html',
                           title=title,
                           )


@app.route('/query', methods=['POST'])
def query():
    global counter_value
    artist_name = request.form.get('artist_name')
    album_title = request.form.get('album_title')
    title = 'my music'
    users_query, table = api.get_query(artist_name, album_title)
    return render_template('query.html',
                           title=title,
                           table=table,  # [counter - 1],
                           table_json=json.dumps(table),
                           query=users_query,
                           counter=counter_value,
                           pages=len(table) // 10 + 1,
                           )


@app.route('/browse')
def browse():
    title = 'my music'
    return render_template('browse.html',
                           title=title,
                           )


# @app.route('/get_page_number/<string:counter>', methods=['POST'])
# def get_page_number(counter, func=None):
#     global counter_value
#     counter_value = int(counter)
#     _logger.debug('counter: {}, type {} called from: {}'.format(counter_value, type(counter_value), func))
#     return('/')


@app.route('/about')
def about():
    title = 'about'
    return render_template('about.html', title=title)


if __name__ == '__main__':
    app.run(debug=True)


# todo cut results of queries into pieces of 10 (custom)
