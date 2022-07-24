import config
import sqlite3
import re
from difflib import SequenceMatcher
import api


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
    fields = {'artist_name', 'artist_surname', 'artist_firstname'}.intersection(f for f in artist_dict.keys()
                                                                                if artist_dict.get(f, None))
    for row in lines:
        artist_id, artist_type, artist_name, artist_surname, artist_firstname, artist_role, sort_name = row
        current_dict = {
            'artist_id': artist_id,
            'artist_type': artist_type,
            'artist_name': artist_name,
            'artist_surname': artist_surname,
            'artist_firstname': artist_firstname,
            'artist_role': artist_role,
            'sort_name': sort_name
        }
        for field in fields:
            if similarity_ratio(str(artist_dict[field]).lower(), str(current_dict[field]).lower()) >= similarity_level:
                similar_artists.append(current_dict)
                break
    return similar_artists


def get_db_columns():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    ret_dict = dict()
    for table in config.DB_TABLES:
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


def add_artist_type_firstname_surname():
    # todo: NOT FINISHED, check todo at the end first
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("""
        SELECT albums.album_id, albums.artist_name, 
        artists.artist_type, artists.artist_firstname, artists.artist_surname
        FROM albums
        INNER JOIN artists ON albums.artist_name = artists.artist_name
        """)
    lines = cur.fetchall()
    for line in lines:
        album_id, artist_name, artist_type, artist_firstname, artist_surname = line
        cur.execute("UPDATE albums SET artist_type = (?) WHERE album_id = (?)", (artist_type, album_id))
    conn.commit()
    cur.close()


def add_record_to_table(record, table):
    # todo: adding records to "albums" table
    if table not in config.DB_TABLES:
        print('There is no table "{}" in the database.'.format(table))
        return
    # "artists" - simple case
    # check if there is such an artist in the database
    similar_artists = find_similar_artist(record)
    add_record = True
    if similar_artists:
        print('The following artists were found in the database:')
        print(api.pretty_table_from_dicts(similar_artists,
                                          list(similar_artists[0].keys())))
        decision = input('Do you still want to add the new artist (y/n)? ')
        add_record = decision in {'y', 'Y'}

    if add_record:
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        # add record
        placeholder = ", ".join(['?'] * len(record))
        stmt = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table=table,
                                                                           columns=",".join(record.keys()),
                                                                           values=placeholder)
        cur.execute(stmt, list(record.values()))
        conditions = ' AND '.join(str(k) + '="' + str(v) +'"' for k, v in record.items() if v)
        cur.execute("SELECT {idx} FROM {table} WHERE {conditions}".format(idx=table[:-1] + '_id',
                                                                          table=table,
                                                                          conditions=conditions))
        idx = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return idx
    return None


def find_incorrect_main_artist_id_in_albums():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("""
        SELECT albums.album_id, albums.album_title, albums.artist_name, albums.main_artist_id, 
        artists.artist_id, artists.artist_type, artists.artist_firstname, artists.artist_surname
        FROM albums
        LEFT JOIN artists ON albums.main_artist_id = artists.artist_id
        """)
    lines = cur.fetchall()
    interesting = list()
    for line in lines:
        if line[4] != line[3]:
            interesting.append([str(_)[:30] for _ in line])
    conn.commit()
    cur.close()
    print(api.pretty_table_from_tuples(interesting, ['L.album_id', 'L.album_title', 'L.artist_name', 'L.main_artist_id',
                                                     'R.artist_id', 'R.artist_type', 'R.artist_firstname',
                                                     'R.artist_surname']))


def dummy():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    # print(get_db_columns())
    # quit()
    find_incorrect_main_artist_id_in_albums()
    pass

# todo: check if there are main_artist_id in albums that are not in artists (left/right join), fix them
# todo: albums: add first name and surname (complete add_artist_type_firstname_surname)


# todo: add artist_id index to albums table or a new table albums_artists:
#  album_id, artist_id(many)...
# todo: check for incorrect artists names in albums
# todo: add_record_to_table(record, table)
