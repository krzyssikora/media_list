from flask import Flask, render_template, request
import json
from music_flask import config, utils, api
from music_flask.config import _logger

app = Flask(__name__)

counter_value = 1
items_per_page = 10
chosen_media = list()


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
    get_items_per_page(items_pp=items_per_page)
    get_media(media_list=chosen_media)
    users_query_string, users_query_object, table, table_header, table_content, html_dom_ids = \
        api.get_simple_query(artist_name, album_title, chosen_media)
    return render_template('query.html',
                           title=title,
                           table=table,  # [counter - 1],
                           table_header=table_header,
                           table_content=table_content,
                           html_dom_ids=html_dom_ids,
                           table_json=json.dumps(table),
                           query=users_query_string,
                           user_filter=users_query_object,
                           items_per_page=items_per_page,
                           counter=counter_value,
                           pages=len(table) // items_per_page + 1,
                           )


@app.route('/browse')
def browse():
    title = 'my music'
    return render_template('browse.html',
                           title=title,
                           user_filter=str({'media': ['CD', 'vinyl', 'DVD'], 'album': '', 'artist': ''})
                           )


@app.route('/edit')
def edit():
    title = 'edit database'
    return render_template('edit.html',
                           title=title,
                           )


@app.route('/get_active_media/<string:media_list>', methods=['POST'])
def get_media(media_list):
    global chosen_media
    # chosen_media = json.load(media_list)
    try:
        chosen_media = eval(str(media_list))
    except TypeError as e:
        _logger.error('type before: {}, {}'.format(type(media_list), e))
    return '/'


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
