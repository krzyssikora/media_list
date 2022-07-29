import sys
import sqlite3
import re
from difflib import SequenceMatcher

import config
import api
# from config import _logger


class DBError(Exception):
    def __init__(self, error_message=None):
        if error_message:
            print(error_message)
        sys.exit(1)


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
    cur.execute(stmt, list(record.values()))
    conditions = ' AND '.join(str(k) + '="' + str(v) + '"' for k, v in record.items() if v)
    cur.execute("SELECT {idx} FROM {table} WHERE {conditions}".format(idx=table[:-1] + '_id',
                                                                      table=table,
                                                                      conditions=conditions))
    idx = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return idx


def add_record_to_table(record, table, artist_from_album=False):
    """
    Adds a record to db table.

    Args:
        record (dict): keys is a subset of table column names
        table (str): 'artists' or 'albums'
        artist_from_album (bool): True when it is artist to be added called from adding album.
            The user's input is compared with existing db records in 'artists' table.
            User is shown matching (similar) records.
            If called from adding artist (artist_from_album == False):
                user is to decide whether to add a new or not.
            If called from adding album (artist_from_album == True):
                user is to decide which artist from similar is the one they want, or add a new one.
    Returns:
        id of the added record (album_id or artist_id depending on the table)

    """
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
                artist_chosen = api.get_multiple_choice_from_list(choices=similar_artists,
                                                                  noun_singular='artist',
                                                                  sort_column='similarity')
                if artist_chosen:
                    return artist_chosen['artist_id']
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


def get_artist_from_db_by_id(idx):
    return get_record_from_table_by_id('artists', idx)


def get_album_from_db_by_id(idx):
    return get_record_from_table_by_id('albums', idx)


def get_record_from_table_by_id(table_name, idx):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    idx_name = table_name[:-1] + '_id'
    cur.execute("SELECT * FROM {} WHERE {} = (?)".format(table_name, idx_name), (idx, ))
    record = cur.fetchall()
    conn.commit()
    cur.close()
    if record:
        if len(record) > 1:
            raise DBError(table_name[:-1] + '_id = ' + str(idx) + ' is not unique!')

        record_dict = dict()
        record = record[0]
        for field_id, field in enumerate(config.DB_COLUMNS[table_name]):
            field_value = record[field_id]
            if field_value:
                record_dict[field] = field_value
        return record_dict

    return None


def update_records_field(table, record_dict, field, value):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(k) + '="' + str(v) + '"' for k, v in record_dict.items() if v)
    cur.execute("UPDATE {} SET {} = (?) WHERE {}".format(table, field, conditions), (value, ))
    conn.commit()
    cur.close()


def update_records_fields(table, record_dict, fields, values):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(k) + ' = ' + (('"' + str(v) + '"')
                                                if isinstance(v, str) else str(v)) + ' '
                              for k, v in record_dict.items() if v)
    set_fields = ', '.join([field + ' = (?)' for field in fields])
    print("UPDATE {} SET {} WHERE {}".format(table, set_fields, conditions), (*values, ))
    cur.execute("UPDATE {} SET {} WHERE {}".format(table, set_fields, conditions), (*values, ))
    conn.commit()
    cur.close()


def dummy():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    print(get_db_columns())
    pass

# todo: check for incorrect artists names in albums
# todo: add_record_to_table(record, table)
# todo: remove all prints from database.py