from flask import Flask, render_template, request
from music_flask import config, utils, api
from music_flask.config import _logger

app = Flask(__name__)


@app.route('/')
def index():
    title = 'my music'
    users_query, table = api.get_query()
    return render_template('index.html', title=title, table=table, query=users_query)


@app.route('/query', methods=['POST'])
def query():
    artist_name = request.form.get('artist_name')
    album_title = request.form.get('album_title')
    title = 'my music'
    users_query, table = api.get_query(artist_name, album_title)
    return render_template('index.html', title=title, table=table, query=users_query)


@app.route('/about')
def about():
    title = 'about'
    return render_template('about.html', title=title)


if __name__ == '__main__':
    app.run(debug=True)


# todo cut results of queries into pieces of 10 (custom)
