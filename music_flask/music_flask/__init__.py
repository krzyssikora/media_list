from flask import Flask, render_template, request
import json
from music_flask import config, utils, api
from music_flask.config import _logger

app = Flask(__name__)

counter_value = 1
items_per_page = 10


@app.route('/')
def index():
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
    # if 'items_per_page' not in vars():
    #     _logger.debug('query, items_per_page does not exist, set to 10')
    #     items_per_page = 10
    get_items_per_page(items_pp=items_per_page)
    _logger.debug('query, items_per_page: {}'.format(items_per_page))
    users_query, table = api.get_query(artist_name, album_title)
    return render_template('query.html',
                           title=title,
                           table=table,  # [counter - 1],
                           table_json=json.dumps(table),
                           query=users_query,
                           items_per_page=items_per_page,
                           counter=counter_value,
                           pages=len(table) // items_per_page + 1,
                           )


@app.route('/browse')
def browse():
    title = 'my music'
    return render_template('browse.html',
                           title=title,
                           )


@app.route('/edit')
def edit():
    title = 'edit database'
    return render_template('edit.html',
                           title=title,
                           )

# @app.route('/get_page_number/<string:counter>', methods=['POST'])
# def get_page_number(counter, func=None):
#     global counter_value
#     counter_value = int(counter)
#     _logger.debug('counter: {}, type {} called from: {}'.format(counter_value, type(counter_value), func))
#     return('/')

@app.route('/get_items_per_page/<string:items_pp>', methods=['POST'])
def get_items_per_page(items_pp):
    global items_per_page
    items_per_page = int(items_pp)
    _logger.debug('items_per_page: {}, type {}'.format(items_per_page, type(items_per_page)))
    return '/'


@app.route('/about')
def about():
    title = 'about'
    return render_template('about.html', title=title)


@app.route('/edit_test')
def edit_test():
    title = 'test'
    return render_template('edit_test.html', title=title)


if __name__ == '__main__':
    app.run(debug=True)
