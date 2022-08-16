from flask import Flask, render_template, request
from music_flask import config, utils, api, database
from music_flask.config import _logger

app = Flask(__name__)

counter_value = 1
items_per_page = 10
chosen_media = list()
new_query = dict()
publishers = database.get_distinct_entries('albums', 'publisher')
query_from_saved = ''
from_saved_query = False


@app.route('/')
def index():
    title = 'my music'
    # get_page_number(counter=counter_value, func='index')
    return render_template('index.html',
                           title=title,
                           )


@app.route('/query', methods=['POST'])
def query():
    global counter_value, from_saved_query

    artist_name = request.form.get('artist_name')
    album_title = request.form.get('album_title')
    publisher = request.form.get('publisher')
    title = 'my music'
    get_items_per_page(items_pp=items_per_page)
    get_media(media_list=chosen_media)
    users_query_string, users_query_object, table_header, table_content, html_dom_ids = \
        api.get_simple_query(artist_name, album_title, chosen_media, publisher)
    return render_template('query.html',
                           title=title,
                           table_header=table_header,
                           table_content=table_content,
                           html_dom_ids=html_dom_ids,
                           publishers=publishers,
                           query=users_query_string,
                           user_filter=users_query_object,
                           items_per_page=items_per_page,
                           counter=counter_value,
                           pages=len(table_content) // items_per_page,
                           )


@app.route('/browse')
def browse():
    title = 'my music'
    return render_template('browse.html',
                           title=title,
                           user_filter=str({'medium': ['CD', 'vinyl', 'DVD'],
                                            'title': '',
                                            'artist': '',
                                            'publisher': ''})
                           )


@app.route('/edit')
def edit():
    title = 'edit database'
    return render_template('edit.html',
                           title=title,
                           )


@app.route('/save_query')
def save_query():
    title = 'saved queries'
    get_query(query_to_save=new_query)
    saved_query_message = database.save_query(new_query)
    queries_table_header, queries_table, query_dicts = api.get_queries_table()
    return render_template('saved_queries.html',
                           title=title,
                           saved_query_message=saved_query_message,
                           queries_table_header=queries_table_header,
                           queries_table=queries_table,
                           query_dicts=query_dicts,
                           )


@app.route('/saved_queries')
def saved_queries():
    title = 'saved queries'
    queries_table_header, queries_table, query_dicts = api.get_queries_table()
    return render_template('saved_queries.html',
                           title=title,
                           queries_table_header=queries_table_header,
                           queries_table=queries_table,
                           query_dicts=query_dicts,
                           )


@app.route('/use_query/<string:query_to_use>', methods=['POST'])
def use_query(query_to_use):
    global counter_value, from_saved_query, query_from_saved
    from_saved_query = True
    query_from_saved = query_to_use
    return '/'


@app.route('/query_from_saved', methods=['POST', 'GET'])
def query_from_saved():
    global counter_value, from_saved_query, query_from_saved, chosen_media
    # query_from_saved = ''
    use_query(query_from_saved)
    _logger.debug('query_from_saved: {}'.format(query_from_saved))
    query_from_saved = eval(query_from_saved)
    artist_name = query_from_saved.get('artist', None)
    album_title = query_from_saved.get('title', None)
    publisher = query_from_saved.get('publisher', None)
    chosen_media = query_from_saved.get('medium', None)
    title = 'my music'
    get_items_per_page(items_pp=items_per_page)
    users_query_string, users_query_object, table_header, table_content, html_dom_ids = \
        api.get_simple_query(artist_name, album_title, chosen_media, publisher)
    return render_template('query.html',
                           title=title,
                           table_header=table_header,
                           table_content=table_content,
                           html_dom_ids=html_dom_ids,
                           publishers=publishers,
                           query=users_query_string,
                           user_filter=users_query_object,
                           items_per_page=items_per_page,
                           counter=counter_value,
                           pages=len(table_content) // items_per_page,
                           )


@app.route('/get_active_media/<string:media_list>', methods=['POST'])
def get_media(media_list):
    global chosen_media
    # chosen_media = json.load(media_list)
    chosen_media = eval(str(media_list))
    return '/'


@app.route('/get_query_to_save/<string:query_to_save>', methods=['POST'])
def get_query(query_to_save):
    global new_query
    new_query = eval(str(query_to_save))
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


# TODO: in script_make_query.js
#  1. line 82: if page == 'query_from_saved', collapse the div showing inputs (make query object non-active?)
#  2. save_query button does not work when keywords in displayed query are changed to strong with use of module.js
