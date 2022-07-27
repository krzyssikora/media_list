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
        current_similarity_ratio = max(similarity_ratio(str(artist_dict[field]).lower(),
                                                        str(current_dict[field]).lower())
                                       for field in fields)
        if current_similarity_ratio >= similarity_level:
            current_dict['similarity'] = current_similarity_ratio
            similar_artists.append(current_dict)
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


def add_single_ready_record_to_table(record, table):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    placeholder = ", ".join(['?'] * len(record))
    stmt = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table=table,
                                                                       columns=",".join(record.keys()),
                                                                       values=placeholder)
    try:
        cur.execute(stmt, list(record.values()))
    except:
        print(stmt)
        print(list(record.values()))
        quit()
    conditions = ' AND '.join(str(k) + '="' + str(v) + '"' for k, v in record.items() if v)
    cur.execute("SELECT {idx} FROM {table} WHERE {conditions}".format(idx=table[:-1] + '_id',
                                                                      table=table,
                                                                      conditions=conditions))
    idx = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return idx


def add_record_to_table(record, table, artist_from_album=False):
    if table not in config.DB_TABLES:
        print('There is no table "{}" in the database.'.format(table))
        return

    if table == 'artists':
        # "artists" - simple case
        # check if there is such an artist in the database
        similar_artists = find_similar_artist(record)
        add_record = True
        if similar_artists:
            if artist_from_album:
                artist_chosen = api.choose_from_similar_artists(similar_artists)
                if artist_chosen:
                    return artist_chosen  # ['artist_id']
            else:
                table_keys = list(similar_artists[0].keys())
                table_keys.remove('similarity')
                # table_keys.append('similarity')
                print('The following artists were found in the database:')
                print(api.pretty_table_from_dicts(similar_artists, table_keys))
                decision = input('Do you still want to add the new artist (y/n)? ')
                add_record = decision in {'y', 'Y'}

        if add_record:
            return add_single_ready_record_to_table(record, table)
    elif table == 'albums':
        return add_single_ready_record_to_table(record, table)
    return None


def dummy():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    # print(get_db_columns())
    # quit()
    pass


# todo: add artist_id index to albums table or a new table albums_artists:
#  album_id, artist_id(many)...
# todo: check for incorrect artists names in albums
# todo: add_record_to_table(record, table)
