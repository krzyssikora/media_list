import config
import sqlite3
import re
from difflib import SequenceMatcher


def similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_similar_artist(artist_dict, similarity_level=0.7):
    """
    Args:
        artist_dict:  includes at least one of the following keys: artist_name, artist_surname, artist_firstname
        similarity_level: only artists for which at least one field is similar on at least this level will be returned

    Returns:
        a list of dicts with artists similar to the one in question
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM artists''')
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    similar_artists = list()
    for row in lines:
        artist_id, artist_type, artist_name, artist_surname, artist_firstname, artist_role = row
        current_dict = {
            'artist_id': artist_id,
            'artist_type': artist_type,
            'artist_name': artist_name,
            'artist_surname': artist_surname,
            'artist_firstname': artist_firstname,
            'artist_role': artist_role
        }
        for field in artist_dict:
            if similarity_ratio(str(artist_dict[field]).lower(), str(current_dict[field]).lower()) >= similarity_level:
                similar_artists.append(current_dict)
                print(current_dict)
                continue
    return similar_artists


def get_db_columns():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    ret_dict = dict()
    for table in ['albums', 'artists']:
        command = "SELECT sql FROM sqlite_master WHERE tbl_name = '{}' AND type = 'table'".format(table)
        cur.execute(command)
        my_string = cur.fetchall()[0][0].replace('\n', '')
        pattern = r'\((.+)\)'
        separated = re.search(pattern, my_string)[1].split(',')
        columns = [elt.strip().split()[0] for elt in separated]
        ret_dict[table] = columns
    conn.commit()
    cur.close()
    return ret_dict


def old_add_main_artist_id_to_albums():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("""SELECT albums.album_id, albums.artist_name, artists.artist_id FROM albums
    INNER JOIN artists ON albums.artist_name = artists.artist_name""")
    lines = cur.fetchall()
    for line in lines:
        album_id, artist_name, main_artist_id = line
        cur.execute("UPDATE albums SET main_artist_id = (?) WHERE album_id = (?)", (main_artist_id, album_id))
    conn.commit()
    cur.close()


def dummy():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    # print(get_db_columns())
    # quit()
    find_null_main_artist_id_in_albums()
    pass

# todo: check missing main_artist_id in albums
# todo: add artist_id index to albums table or a new table albums_artists:
#  album_id, artist_id(many)...
# todo: check for incorrect artists names in albums
