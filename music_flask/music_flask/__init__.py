from flask import Flask, render_template
# import sys
# sys.path.insert(0, 'C:/Users/krzys/Documents/Python/lekcje/music_list/')
from music_flask import config, database, utils

app = Flask(__name__)


@app.route('/')
def index():
    title = 'my music'
    table = utils.convert_dicts_to_list_of_tuples(database.get_albums_by_title_or_artist('string', 'shostakovich'),
                                                  config.DB_ALBUMS_COLUMNS)
    return render_template('index.html', title=title, table=table)


@app.route('/about')
def about():
    title = 'about'
    return render_template('about.html', title=title)


if __name__ == '__main__':
    app.run(debug=True)
